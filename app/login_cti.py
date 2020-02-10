# Python imports
import os
import shutil
import time
import subprocess
from datetime import datetime
from datetime import date
import sys
from configparser import ConfigParser

# Selenium Imports
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
			exit(1)

		for i in range(IncomingArrayLength):
			if i % 2 != 0:
				ResultDict[IncomingArray[i-1]] = IncomingArray[i]

		return ResultDict

	def WaitForElement(self, target, method=By.XPATH, callCounter=0):

		'''

		This one waits for an element to be present within standard wait 
		Calls itself recursively for N times until it dies with exit(1)

		'''

		self.LogAndPrint("WaitForElement(): {0}".format(callCounter))

		if callCounter >= 5:
			self.LogAndPrint("MaxAttempts reached {0}".format(callCounter))
			self.DriverObject.quit()
			exit(1)

		callCounter += 1

		try:
		
			self.StandardWaitObject.until(EC.presence_of_element_located((method, target)))
			self.LogAndPrint("WaitForElement(): Target found")
		
		except Exception as e:	
		
			self.LogAndPrint("WaitForElement(): Target not found!")
			
			# Refresh will cause all fields to refresh and lose their values if this 
			# function is used for not-the-first element on the page
			# e.g. login will lose value if password field gets lost and page is refreshed

			self.DriverObject.refresh()
			time.sleep(2)
			self.WaitForElement(target,callCounter=callCounter)

	def LocateAWindowByTitle(self, WindowTitle):

		'''
		
		Checking if WindowTitle is present
		Loooping until found or reached 100 attempts

		'''

		self.LogAndPrint("LocateAWindowByTitle start")

		ExitCode = None
		AttemptsCounter = 0
		MaxAttempts = 150

		CheckWindowExePath = os.path.realpath(os.path.join(self.ExeFolderPath, "CheckWindow.exe"))

		while ExitCode !=0 and AttemptsCounter < MaxAttempts:
			ChildProcess = subprocess.Popen([CheckWindowExePath, WindowTitle], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

			for line in ChildProcess.stdout.readlines():
				ChildProcess.wait()
				# Outputs title and handle
				#LogAndPrint(LoginLoggerObject, line)
				ExitCode=ChildProcess.returncode

			time.sleep(5)
			AttemptsCounter = AttemptsCounter + 1
			self.LogAndPrint("Attempt " + str(AttemptsCounter))
			self.LogAndPrint("ExitCode: " + str(ExitCode))

			if (AttemptsCounter == MaxAttempts and ExitCode !=0):
				self.LogAndPrint("MaxAttempts reached: " + str(AttemptsCounter) + "/" + str(MaxAttempts))
				self.LogAndPrint("LocateAWindowByTitle(): end")
				exit(1)
			else:
				self.LogAndPrint("Window \"{0}\" found, proceed".format(WindowTitle))
				time.sleep(3)
				self.LogAndPrint("LocateAWindowByTitle():  end")

	def LocateWindowByTitleNew(self, WindowTitle):

		if not WindowTitle:
			self.LogAndPrint("LocateWindowByTitle(): No WindowTitle is supplied")
			exit(1)

			CheckWindowExePath = os.path.realpath(os.path.join(self.ExeFolderPath, "CheckWindow.exe"))

			child = subprocess.Popen([CheckWindowExePath, WindowTitle], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
			rc = child.poll()

			while (True and rc == None):
				
				output = child.stdout.readline()
				if output == '' and child.poll() is not None:
					break
				if output:
					self.LogAndPrint(output.strip().decode())

				rc = child.poll()

			self.LogAndPrint("RC: {0}".format(rc))
			self.LogAndPrint("LocateWindowByTitleNew(): end")
	
	# Helper functions end
	
	def InitDriver(self):

		'''

		Initialize Chrome Driver
		Sets self.DriverObject and self.StandardWaitObject
		
		'''

		self.LogAndPrint("InitDriver(): start")

		ChromeOptions = Options()
		ChromeOptions.binary_location = self.ChromeBinaryLocation
		ChromeOptions.add_argument("disable-metrics-system")
		ChromeOptions.add_argument("disable-logging")
		ChromeOptions.add_argument("disable-dev-tools")
		ChromeOptions.add_argument("profile.ephemeral_mode")
		ChromeOptions.add_argument("user-data-dir={0}".format(str(self.ChromeUserDirLocation)))
		ChromeOptions.add_argument("--disable-extensions")
		ChromeOptions.add_argument("--no-network-profile-warning")
		ChromeOptions.add_argument("disable-background-networking")
		ChromeOptions.add_argument("disable-client-side-phishing-detection")
		ChromeOptions.add_argument("disable-default-apps")
		ChromeOptions.add_argument("disable-domain-reliability")
		ChromeOptions.add_argument("disk-cache-size={0}".format( 64* 1024 * 1024 ))
		ChromeOptions.add_argument("incognito")
		ChromeOptions.add_argument("no-default-browser-check")
		ChromeOptions.add_argument("no-first-run")
		ChromeOptions.add_argument("window-position={0},{1}".format(0, 0))
		ChromeOptions.add_argument("--suppress-message-center-popups")
		ChromeOptions.add_argument("--no-crash-upload")
		ChromeOptions.add_argument("--light")
		ChromeOptions.add_argument("--disable-perfetto")

		# Needed for PulseSecure pop-up handling

		prefs = {"protocol_handler.excluded_schemes":{"pulsesecure":False}}
		ChromeOptions.add_experimental_option("prefs",prefs)
		#ChromeOptions.add_argument("user_experience_metrics.reporting_enabled={0}".format("false"))

		self.DriverObject = webdriver.Chrome(executable_path=self.ChromeDriverLocation, chrome_options=ChromeOptions)
		#driver.execute_script("window.confirm = function(msg) { return true; }")
		
		self.DriverObject.set_window_size(1024, 768)
		self.StandardWaitObject = WebDriverWait(self.DriverObject, 20)
		
		self.LogAndPrint("InitDriver(): end")

	def LaunchReadAuth(self):

		'''

		Launches authenticator.exe
		Requires NodeJS to be installed ?
		https://www.npmjs.com/package/authenticator-cli
		https://www.npmjs.com/package/pkg

		'''

		self.LogAndPrint("LaunchReadAuth(): start")
		AuthFileLocation = os.path.realpath(os.path.join(self.ExeFolderPath, "authenticator.exe"))
		AuthArgs = ["--key ", self.AuthSecret]

		ChildProcess = subprocess.Popen([AuthFileLocation, AuthArgs], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		ExitCode = ChildProcess.poll()
		ResultString = ""

		while (True and ExitCode == None):
			
			ProcessOutput = ChildProcess.stdout.readline()
			if ProcessOutput == '' and ChildProcess.poll() is not None:
				break
			if ProcessOutput:
			#print(output.strip().decode())
				ResultString +=  ProcessOutput.strip().decode() + "\n"

			ExitCode = ChildProcess.poll()

		self.AuthCode = self.ListToDict(ResultString.split())['Token:']

		#LogAndPrint("RC: {0}".format(rc))
		self.LogAndPrint("AuthCode: {0}".format(self.AuthCode))
		self.LogAndPrint("LaunchReadAuth() end")

	def LoginToOkta(self):

		'''

		Logging to OKTA
		Reads: self.OktaLogin, self.OktaPassword

		'''

		self.LogAndPrint("LoginToOkta")
		self.DriverObject.get("https://esri.okta.com/")

		time.sleep(3)

		# User and password
		self.LogAndPrint("Logging in as: " + str(self.OktaLogin))

		self.DriverObject.find_element_by_id("okta-signin-username").clear()
		self.DriverObject.find_element_by_id("okta-signin-username").send_keys(self.OktaLogin)

		self.DriverObject.find_element_by_id("okta-signin-password").clear()
		self.DriverObject.find_element_by_id("okta-signin-password").send_keys(self.OktaPassword)

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

		self.LogAndPrint("Login successful")

		return 0

	def ParseOktaButtons(self):

		'''

		Gets all buttons in OKTA
		Sets self.OktaButtons

		'''
		self.LogAndPrint("ParseOktaButtons(): start")

		buttons = self.DriverObject.find_elements_by_xpath('//*[@id="main-content"]/div/div[3]/ul[2]/li[*]/a')
		names = self.DriverObject.find_elements_by_xpath('//*[@id="main-content"]/div/div[3]/ul[2]/li[*]/p')

		# Forming array with all buttons on OKLA

		if len(buttons) == len(names):
			res =[]
			for incr in range(0,len(buttons)):
				res.insert(incr, {'name':str(names[incr].get_attribute("oldtitle")), 'button':buttons[incr]})
		else:
			self.LogAndPrint("Parsing buttons failed"  + "\n")
			exit(1)

		self.LogAndPrint("ParseOktaButtons end")
		self.LogAndPrint(res)
		self.OktaButtons = res if res else exit(1)

	def ClickOktaButtonByName(self, ButtonName):

		'''
		Clicks a button by its name

		'''

		IncomingButtons = self.OktaButtons
		PassedButtonsArray = []

		self.LogAndPrint("ClickOktaButtonByName(): start")
		self.LogAndPrint("Target: " + ButtonName + "\n")

		for button in IncomingButtons:
			
			PassedButtonsArray.append(button['name'])

			if ButtonName == button['name']:
				self.LogAndPrint("Found: " + str(ButtonName))
				button['button'].click()
				self.LogAndPrint("Clicked: " + str(ButtonName))
				self.LogAndPrint("ClickOktaButtonByName() end")

	def GoToXenApp(self):

		'''

		Finds "Connect to Xenapp" link after OKTA button is clicked"

		'''

		self.LogAndPrint("GoToXenApp(): start")
		XenAppTableXPath = "/html/body/table[5]/tbody/tr/td[2]/center/table/tbody/tr/td/div[1]/div/table/tbody/tr/td/table/tbody/tr/td/div[1]/table[33]/tbody/tr/td[1]/table/tbody/tr/td[2]/a"
		self.WaitForElement(XenAppTableXPath)

		XenAppElement = self.DriverObject.find_element_by_xpath(XenAppTableXPath)
		XenAppLink = (XenAppElement.get_attribute('href'))
		self.LogAndPrint("XenAppLink: " + str(XenAppLink))

		self.DriverObject.get(XenAppLink)
		time.sleep(3)
		
		self.LogAndPrint("GoToXenApp end")

	def LoginToXenApp(self):

		'''
	
		Logs into Xenapp Frame
		Reads self.OktaLogin and self.OktaPassword

		'''

		self.LogAndPrint("LoginToXenApp start")
		
		LoginFrameXPath = "/html/body/div/table/tbody/tr/td[1]/iframe"
		self.WaitForElement(LoginFrameXPath)

		LoginFrame = self.DriverObject.find_element_by_xpath(LoginFrameXPath)
		LoginFrameLink = LoginFrame.get_attribute('src')
		
		self.LogAndPrint("LoginFrameLink: " +  str(LoginFrameLink))
		self.DriverObject.get(LoginFrameLink)
		time.sleep(5)

		# USERNAME AND PASSWORD
		self.LogAndPrint("Logging in as : " + str(self.OktaLogin))
		UserNameInputXPath = "//*[@id=\"user\"]"
		self.WaitForElement(UserNameInputXPath)

		UserNameInputField = self.DriverObject.find_element_by_xpath(UserNameInputXPath)
		UserNameInputField.clear()
		UserNameInputField.send_keys(self.OktaLogin)
		time.sleep(2)

		# USERNAME AND PASSWORD
		PasswordInputXPath = "//*[@id=\"password\"]"
		self.WaitForElement(PasswordInputXPath)

		PasswordInputField = self.DriverObject.find_element_by_xpath(PasswordInputXPath)
		PasswordInputField.clear()
		PasswordInputField.send_keys(self.OktaPassword)
		time.sleep(2)

		LoginButtonXPath = "//*[@id=\"btnLogin\"]"
		LoginButton = self.DriverObject.find_element_by_xpath(LoginButtonXPath)
		LoginButton.click()

		time.sleep(2)
		self.LogAndPrint("LoginToXenApp(): end")

	def ClickWDESkypeMenu(self):

		'''

		Clicks WDESkypeMenu
	
		'''

		self.LogAndPrint("ClickWDESkypeMenu(): start")
		time.sleep(2)

		WDESkypeMenuPRDXPath = "//*[@id=\"Citrix.MPS.App.BISGreen.WDESkypeMenuPRD\"]"

		self.WaitForElement(WDESkypeMenuPRDXPath)

		WDESkypeMenuPRDElement = self.DriverObject.find_element_by_xpath(WDESkypeMenuPRDXPath)
		time.sleep(2)
		
		WDESkypeMenuPRDElement.click()
		time.sleep(1)

		self.LogAndPrint("ClickWDESkypeMenu(): end")

	def ProcessWDE(self, RequestedFunction):
		
		'''

		Clicks remote window buttons
		RequestedFunction = [ 'LogInToSkype', 'LogInToWDE', 'SetAtDeskWDE' ]

		'''
	
		self.LogAndPrint("ProcessWDE start: {0}".format(RequestedFunction))
		self.LogAndPrint("Starting exe file...")

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

		self.LogAndPrint("ProcessWDE end: {0}".format(RequestedFunction))


DriverWrapperObject = DriverWrapper()

DriverWrapperObject.InitDriver()
time.sleep(1)

DriverWrapperObject.LoginToOkta()
time.sleep(3)

DriverWrapperObject.ParseOktaButtons()
DriverWrapperObject.ClickOktaButtonByName("US-West VPN (Redlands Tech Support)")
DriverWrapperObject.LogAndPrint("Sleeping ... ")
time.sleep(15)
DriverWrapperObject.LogAndPrint("Sleeping...end")

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