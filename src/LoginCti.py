# Python imports
import sys
import os
import shutil
import time
import subprocess

from datetime import date
from datetime import datetime
from configparser import ConfigParser

# Selenium Imports
import selenium
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options

# Logging
from logger.mylogger import MyLogger

class DriverWrapper():

	def __init__(self):

		self.LoggerObject = MyLogger("Login_")
		
		# General locations
		self.MyLocation = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
		self.ExeFolderPath = os.path.realpath(os.path.join(self.MyLocation,"exe"))
		self.ConfigLocation = os.path.realpath(os.path.join(self.MyLocation , "tmp", "config.txt"))


		# Chrome locations
		self.ChromeDriverLocation = os.path.realpath(os.path.join(self.MyLocation, "..", "chromedriver","chromedriver80.exe"))
		self.ChromeRootLocation = os.path.realpath((os.path.join(self.MyLocation, "..", "chrome")))
		self.ChromeUserDirLocation = os.path.realpath(os.path.join(self.ChromeRootLocation, "userdir"))
		self.ChromeBinaryLocation = os.path.realpath((os.path.join(self.ChromeRootLocation, "app", "chrome.exe")))

		# General variables
		self.ConfigParserObject = ConfigParser()
		self.ConfigParserObject.read(self.ConfigLocation)

		self.OktaLogin = self.ConfigParserObject.get("Credentials","User")
		self.OktaPassword = self.ConfigParserObject.get("Credentials","Pass")
		self.AuthSecret = self.ConfigParserObject.get("Credentials","AuthSecret")

		self.OktaButtons = None

		# Cleaning Chrome Data Dir
		for root, dirs, files in os.walk(self.ChromeUserDirLocation):
			for f in files:
				os.unlink(os.path.join(root, f))
			for d in dirs:
				shutil.rmtree(os.path.join(root,d))

	# Helper functions
	def LogAndPrint(self, Message):

		self.LoggerObject.LogAndPrint(Message)

	def ListToDict(self, IncomingArray):
		
		'''
		
		Converts incoming array into dict 
		Works only with arrays having even number of elements
		["hello", "world", "good", "day"]  = {"hello":"world", "good":"day"}

		'''

		IncomingArrayLength = len(IncomingArray)
		ResultDict = {}

		if IncomingArrayLength % 2 != 0:

			self.LogAndPrint("ListToDict: Array given is not even!")
			self.LogAndPrint(IncomingArray)
			sys.exit(1)

		for i in range(IncomingArrayLength):
			if i % 2 != 0:
				ResultDict[IncomingArray[i-1]] = IncomingArray[i]

		return ResultDict

	def WaitForElement(self, target, method=By.XPATH, callCounter=0):

		'''

		This one waits for an element to be present within standard wait 
		Calls itself recursively for N times until it dies with sys.exit(1)

		'''

		self.LogAndPrint("WaitForElement(): Attempt {0}".format(callCounter))

		if callCounter >= 5:
			self.LogAndPrint("WaitForElement(): MaxAttempts reached {0}".format(callCounter))
			self.DriverObject.quit()
			sys.exit(1)

		callCounter += 1

		try:
		
			self.StandardWaitObject.until(EC.presence_of_element_located((method, target)))
			self.LogAndPrint("WaitForElement(): Found")
		
		except Exception as e:	
		
			self.LogAndPrint("WaitForElement(): Not found!")
			
			# Refresh will cause all fields to refresh and lose their values if this 
			# function is used for not-the-first element on the page
			# e.g. login will lose value if password field gets lost and page is refreshed

			# This refresh can be a bit dangerous as it can reset element state
			self.DriverObject.refresh()
			time.sleep(1)
			self.WaitForElement(target,callCounter=callCounter)

	def InitDriver(self):

		'''

		Initialize Chrome Driver
		Sets self.DriverObject and self.StandardWaitObject
		
		'''

		self.LogAndPrint("\nInitDriver(): Start")

		ChromeOptions = Options()
		ChromeOptions.binary_location = self.ChromeBinaryLocation
		ChromeOptions.add_argument("disable-metrics-system")
		ChromeOptions.add_argument("disable-logging")
		ChromeOptions.add_argument("disable-dev-tools")
		ChromeOptions.add_argument("profile.ephemeral_mode")
		ChromeOptions.add_argument("user-data-dir={0}".format(str(self.ChromeUserDirLocation)))
		ChromeOptions.add_argument("disable-extensions")
		ChromeOptions.add_argument("no-network-profile-warning")
		ChromeOptions.add_argument("disable-background-networking")
		ChromeOptions.add_argument("disable-client-side-phishing-detection")
		ChromeOptions.add_argument("disable-default-apps")
		ChromeOptions.add_argument("disable-domain-reliability")
		ChromeOptions.add_argument("disk-cache-size={0}".format( 64 * 1024 * 1024 ))
		ChromeOptions.add_argument("incognito")
		ChromeOptions.add_argument("no-default-browser-check")
		ChromeOptions.add_argument("no-first-run")
		ChromeOptions.add_argument("window-position={0},{1}".format(0, 0))
		ChromeOptions.add_argument("suppress-message-center-popups")
		ChromeOptions.add_argument("no-crash-upload")
		ChromeOptions.add_argument("light")
		ChromeOptions.add_argument("disable-perfetto")

		# Needed for PulseSecure pop-up handling

		prefs = {"protocol_handler.excluded_schemes":{"pulsesecure":False}}
		ChromeOptions.add_experimental_option("prefs",prefs)
		ChromeOptions.add_argument("user_experience_metrics.reporting_enabled={0}".format("false"))

		self.DriverObject = webdriver.Chrome(executable_path=self.ChromeDriverLocation, options=ChromeOptions)
		#driver.execute_script("window.confirm = function(msg) { return true; }")
		self.DriverObject.set_window_size(1024, 768)
		self.StandardWaitObject = WebDriverWait(self.DriverObject, 20)

		self.LogAndPrint("InitDriver(): End")

	def LaunchReadAuth(self):

		'''

		Launches authenticator.exe
		Requires NodeJS to be installed ?
		https://www.npmjs.com/package/authenticator-cli
		https://www.npmjs.com/package/pkg

		'''

		self.LogAndPrint("LaunchReadAuth(): Start")
		AuthFileLocation = os.path.realpath(os.path.join(self.ExeFolderPath, "authenticator.exe"))
		AuthArgs = [" --key ", self.AuthSecret]
		ChildProcessPath = AuthFileLocation + AuthArgs[0] + AuthArgs[1]
		#print(ChildProcessPath)

		ChildProcess = subprocess.Popen(ChildProcessPath, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		ExitCode = ChildProcess.poll()
		ResultString = ""

		while (True and ExitCode == None):
			
			ProcessOutput = ChildProcess.stdout.readline()
			if ProcessOutput == '' and ChildProcess.poll() is not None:
				break
			if ProcessOutput:
				#print("output: " + ProcessOutput.strip().decode())
				ResultString +=  ProcessOutput.strip().decode() + "\n"

			ExitCode = ChildProcess.poll()

		self.AuthCode = self.ListToDict(ResultString.split())['Token:']

		#LogAndPrint("RC: {0}".format(rc))
		self.LogAndPrint("LaunchReadAuth(): AuthCode: {0}".format(self.AuthCode))
		self.LogAndPrint("LaunchReadAuth(): End")

	def LoginToOkta(self):

		'''

		Logging to OKTA
		Reads: self.OktaLogin, self.OktaPassword

		'''

		self.LogAndPrint("\nLoginToOkta(): Start")
		self.DriverObject.get("https://esri.okta.com/")

		time.sleep(3)

		# User and password
		self.LogAndPrint("LoginToOkta(): Username: " + str(self.OktaLogin))

		self.DriverObject.find_element_by_id("okta-signin-username").clear()
		time.sleep(1)
		self.DriverObject.find_element_by_id("okta-signin-username").send_keys(self.OktaLogin)
		time.sleep(1)

		self.DriverObject.find_element_by_id("okta-signin-password").clear()
		time.sleep(1)
		self.DriverObject.find_element_by_id("okta-signin-password").send_keys(self.OktaPassword)
		time.sleep(1)

		self.DriverObject.find_element_by_id("okta-signin-submit").click()

		## WinAuth
		time.sleep(3)

		# Sets self.AuthCode
		self.LaunchReadAuth()

		time.sleep(3)
		elems = self.DriverObject.find_elements_by_css_selector('[id^="input"]')
		elems[0].send_keys(self.AuthCode)

		# Verify button
		# Hidden in div so loop and click all

		buttons = self.DriverObject.find_elements_by_class_name("o-form-button-bar")
		for button in buttons:
			button.click()

		time.sleep(3)

		OktaButtonsXPath = '//*[@id="main-content"]/div/div[3]/ul[2]/li[*]/a'
		
		try:
			
			self.WaitForElement(OktaButtonsXPath)
			self.LogAndPrint("LoginToOkta(): End")
	
		except Exception as e:

			self.LogAndPrint(e)
			sys.exit(1)
		
	def ParseOktaButtons(self):

		'''

		Gets all buttons in OKTA
		Sets self.OktaButtons

		'''
		self.LogAndPrint("\nParseOktaButtons(): Start")

		buttons = self.DriverObject.find_elements_by_xpath('//*[@id="main-content"]/div/div[3]/ul[2]/li[*]/a')
		names = self.DriverObject.find_elements_by_xpath('//*[@id="main-content"]/div/div[3]/ul[2]/li[*]/p')

		# Forming array with all buttons on OKLA

		if len(buttons) == len(names):
			res =[]
			for incr in range(0,len(buttons)):
				res.insert(incr, {'name':str(names[incr].get_attribute("oldtitle")), 'button':buttons[incr]})
		else:
			self.LogAndPrint("Parsing buttons failed!"  + "\n")
			self.LogAndPrint("Buttons: {0}".format(buttons)  + "\n")
			self.LogAndPrint("Names: {0}".format(names)  + "\n")
			sys.exit(1)

		self.LogAndPrint("ParseOktaButtons(): End")
		#self.LogAndPrint(res)
		self.OktaButtons = res if res else sys.exit(1)

	def ClickOktaButtonByName(self, ButtonName):

		'''

		Clicks a button by its name

		'''

		IncomingButtons = self.OktaButtons
		PassedButtonsArray = []

		self.LogAndPrint("\nClickOktaButtonByName(): Start")
		self.LogAndPrint("ClickOktaButtonByName(): Target: " + ButtonName)

		for button in IncomingButtons:
			
			PassedButtonsArray.append(button['name'])

			if ButtonName == button['name']:
				self.LogAndPrint("ClickOktaButtonByName(): Found: " + str(ButtonName))
				button['button'].click()
				self.LogAndPrint("ClickOktaButtonByName(): Clicked: " + str(ButtonName))
				self.LogAndPrint("ClickOktaButtonByName(): End")
			
	def GoToXenApp(self):

		'''

		Finds "Connect to Xenapp" link after OKTA button is clicked"

		'''

		self.LogAndPrint("\nGoToXenApp(): Start")
		XenAppTableXPath = "/html/body/table[5]/tbody/tr/td[2]/center/table/tbody/tr/td/div[1]/div/table/tbody/tr/td/table/tbody/tr/td/div[1]/table[33]/tbody/tr/td[1]/table/tbody/tr/td[2]/a"
		self.WaitForElement(XenAppTableXPath)

		XenAppElement = self.DriverObject.find_element_by_xpath(XenAppTableXPath)
		XenAppLink = (XenAppElement.get_attribute('href'))
		self.LogAndPrint("GoToXenApp(): XenAppLink: " + str(XenAppLink))

		self.DriverObject.get(XenAppLink)
		time.sleep(2)
		
		self.LogAndPrint("GoToXenApp(): End")

	def LoginToXenApp(self):

		'''
	
		Logs into Xenapp Frame
		Reads self.OktaLogin and self.OktaPassword

		'''

		self.LogAndPrint("\nLoginToXenApp(): Start")
		
		LoginFrameXPath = "/html/body/div/table/tbody/tr/td[1]/iframe"
		self.WaitForElement(LoginFrameXPath)

		LoginFrame = self.DriverObject.find_element_by_xpath(LoginFrameXPath)
		LoginFrameLink = LoginFrame.get_attribute('src')
		
		self.LogAndPrint("LoginToXenApp(): LoginFrameLink: " +  str(LoginFrameLink))
		self.DriverObject.get(LoginFrameLink)
		time.sleep(2)

		# USERNAME AND PASSWORD
		self.LogAndPrint("LoginToXenApp(): Username:" + str(self.OktaLogin))
		UserNameInputXPath = "//*[@id=\"user\"]"
		self.WaitForElement(UserNameInputXPath)

		UserNameInputField = self.DriverObject.find_element_by_xpath(UserNameInputXPath)
		UserNameInputField.clear()
		UserNameInputField.send_keys(self.OktaLogin)
		time.sleep(1)

		# USERNAME AND PASSWORD
		PasswordInputXPath = "//*[@id=\"password\"]"
		self.WaitForElement(PasswordInputXPath)

		PasswordInputField = self.DriverObject.find_element_by_xpath(PasswordInputXPath)
		PasswordInputField.clear()
		PasswordInputField.send_keys(self.OktaPassword)
		time.sleep(1)

		LoginButtonXPath = "//*[@id=\"btnLogin\"]"
		LoginButton = self.DriverObject.find_element_by_xpath(LoginButtonXPath)
		LoginButton.click()

		time.sleep(1)

		# Sometimes browser will show a page to download Citrix Online Web Plugin
		try:

			PluginAlreadyInstalledButtonXPath = "/html/body/div[1]/div/div/div[1]/div/div[3]/div[2]/div[2]/p[1]/a"
			self.WaitForElement(PluginAlreadyInstalledButtonXPath, By.XPATH, 4)
			PluginAlreadyInstalledButton = self.DriverObject.find_element_by_xpath(PluginAlreadyInstalledButtonXPath)
			PluginAlreadyInstalledButton.click()
			self.LogAndPrint("LoginToXenApp(): Citrix plugin download button clicked")

		except Exception as e:
			
			self.LogAndPrint(e)
			pass

		self.LogAndPrint("LoginToXenApp(): End")

	def ClickWDESkypeMenu(self):

		'''

		Clicks WDESkypeMenu
	
		'''

		self.LogAndPrint("\nClickWDESkypeMenu(): Start")
		time.sleep(2)

		WDESkypeMenuPRDXPath = "//*[@id=\"Citrix.MPS.App.BISGreen.WDESkypeMenuPRD\"]"

		self.WaitForElement(WDESkypeMenuPRDXPath)

		WDESkypeMenuPRDElement = self.DriverObject.find_element_by_xpath(WDESkypeMenuPRDXPath)
		time.sleep(2)
		
		WDESkypeMenuPRDElement.click()
		time.sleep(1)

		self.LogAndPrint("ClickWDESkypeMenu(): End")

	def ProcessWDE(self, RequestedFunction):
		
		'''

		Clicks remote window buttons
		RequestedFunction = [ 'LogInToSkype', 'LogInToWDE', 'SetAtDeskWDE' ]

		'''
	
		self.LogAndPrint("\nProcessWDE Start: {0}".format(RequestedFunction))

		ProcessWDEExePath = os.path.realpath(os.path.join(self.ExeFolderPath, "ProcessWDE.exe"))

		child = subprocess.Popen([ProcessWDEExePath, RequestedFunction], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		
		rc = child.poll()

		while True and (rc == None or rc == 1):
			output = child.stdout.readline()
			if output == '' and child.poll() is not None:
				break
			if output:
				self.LogAndPrint(output.strip().decode())
			rc = child.poll()

		self.LogAndPrint("ProcessWDE() End: {0}".format(RequestedFunction))

DriverWrapperObject = DriverWrapper()

DriverWrapperObject.InitDriver()
time.sleep(1)

DriverWrapperObject.LoginToOkta()
time.sleep(3)

DriverWrapperObject.ParseOktaButtons()
DriverWrapperObject.ClickOktaButtonByName("US-West VPN (Redlands Tech Support)")

DriverWrapperObject.LogAndPrint("Sleeping ... ")
time.sleep(15)
DriverWrapperObject.LogAndPrint("Done")

SecondTab = DriverWrapperObject.DriverObject.window_handles[1]
DriverWrapperObject.DriverObject.switch_to.window(SecondTab)
time.sleep(2)

#DriverWrapperObject.DriverObject.refresh()
#time.sleep(2)

DriverWrapperObject.GoToXenApp()
time.sleep(2)

DriverWrapperObject.LoginToXenApp()
time.sleep(2)

DriverWrapperObject.ClickWDESkypeMenu()
time.sleep(3)

DriverWrapperObject.ProcessWDE("LogInToSkype")
time.sleep(3)

DriverWrapperObject.ProcessWDE("LogInToWDE")
time.sleep(3)

DriverWrapperObject.ProcessWDE("SetAtDeskWDE")
time.sleep(3)