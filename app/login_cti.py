import os
import shutil
import time
import subprocess
#import threading
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

# Additional parsers
#import lxml.html
#from lxml import etree
#from lxml.cssselect import CSSSelector
#import csv
#from bs4 import BeautifulSoup

# Video capture and Logging
#from capture.videohandler import VideoHandler
from logger.mylogger import MyLogger

def InitLogger():

	LoggerObject = MyLogger("Login_")
	return LoggerObject

def LogAndPrint(LoggerObject, Message):

	LoggerObject.LogAndPrint(Message)

'''

def InitCapture():

	LogAndPrint(LoginLoggerObject, "InitCapture start")

	VideoHandlerObject = VideoHandler()

	return VideoHandlerObject

def StartVideoCapture(VideoHandlerObject):

	LogAndPrint(LoginLoggerObject, "Video capture started")
	VideoHandlerObject.start()

def StopVideoCapture(VideoHandlerObject):

	LogAndPrint(LoginLoggerObject, "Video capture stopped")
	VideoHandlerObject.stop()

'''

def InitDriver():

	'''
	
	Init Chrome Driver

	'''

	LogAndPrint(LoginLoggerObject, "InitDriver start")

	my_location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
	chrome_driver_location = os.path.realpath(os.path.join(my_location, "..", "chromedriver","chromedriver80.exe"))
	chrome_location = os.path.realpath((os.path.join(my_location, "..", "chrome")))
	chrome_userdir = os.path.realpath(os.path.join(chrome_location, "userdir"))
	chrome_binary = os.path.realpath((os.path.join(chrome_location, "app", "chrome.exe")))
	
	chrome_options = Options()
	
	chrome_options.binary_location = chrome_binary
	chrome_options.add_argument("disable-metrics-system")
	chrome_options.add_argument("disable-logging")
	chrome_options.add_argument("disable-dev-tools")
	chrome_options.add_argument("profile.ephemeral_mode")
	chrome_options.add_argument("user-data-dir={0}".format(str(chrome_userdir)))
	chrome_options.add_argument("--disable-extensions")
	chrome_options.add_argument("--no-network-profile-warning")
	
	chrome_options.add_argument("disable-background-networking")
	chrome_options.add_argument("disable-client-side-phishing-detection")
	chrome_options.add_argument("disable-default-apps")
	chrome_options.add_argument("disable-domain-reliability")
	chrome_options.add_argument("disk-cache-size={0}".format( 64* 1024 * 1024 ))
	chrome_options.add_argument("incognito")
	chrome_options.add_argument("no-default-browser-check")
	chrome_options.add_argument("no-first-run")
	chrome_options.add_argument("window-position={0},{1}".format(0, 0))
	chrome_options.add_argument("--suppress-message-center-popups")
	chrome_options.add_argument("--no-crash-upload")
	chrome_options.add_argument("--light")
	chrome_options.add_argument("--disable-perfetto")
	
	

	chrome_options.add_argument("user_experience_metrics.reporting_enabled={0}".format("false"))
	#	chrome_options.add_argument("--headless")
	
	
	# Needed to pass through Pulse Secure Protocol Open pop-up in Chrome
	prefs = {"protocol_handler.excluded_schemes":{"pulsesecure":False}}
	chrome_options.add_experimental_option("prefs",prefs)

	# Removes controlled by automated software message
	#chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"] )

	# Cleaning chrome user dir to maintain the zero session state
	for root, dirs, files in os.walk(chrome_userdir):
		for f in files:
			os.unlink(os.path.join(root, f))
		for d in dirs:
			shutil.rmtree(os.path.join(root,d))

	
	driver = webdriver.Chrome(executable_path=chrome_driver_location, chrome_options=chrome_options)
	driver.execute_script("window.confirm = function(msg) { return true; }")
	driver.set_window_size(1024, 768)

	standard_wait = WebDriverWait(driver, 20)

	LogAndPrint(LoginLoggerObject, "InitDriver done")

	return [driver, standard_wait]

def LaunchWinAuth_old():

	'''
	Launches WinAuth as a subprocess via AutoIt script
	
	'''

	LogAndPrint(LoginLoggerObject, "WinAuth launch start")
	ExeFolderPath = os.path.realpath(os.path.join(my_location,"exe"))
	WinAuthFileLocation = os.path.realpath(os.path.join(ExeFolderPath,"OpenWinAuth.exe"))

	try:
		subprocess.call(os.path.realpath(os.path.join(my_location , WinAuthFileLocation)))
		LogAndPrint(LoginLoggerObject, "LaunchWinAuth done")

	except subprocess.CalledProcessError as e:

		LogAndPrint(LoginLoggerObject, "Error: LaunchWinAuth")
		LogAndPrint(LoginLoggerObject, e)
		exit(1)

def ListToDict(IncomingArray):

	'''
	Converts incoming array into dict 
	Works only with arrays having even number of elements
	["hello", "world", "good", "day"]  = {"hello":"world", "good":"day"}
	'''

	IncomingArrayLength = len(IncomingArray)
	ResultDict = {}

	if IncomingArrayLength % 2 != 0:

		print("ListToDict: Array given is not even!")
		print(IncomingArray)

		exit(1)

	for i in range(IncomingArrayLength):
		if i % 2 != 0:
			ResultDict[IncomingArray[i-1]] = IncomingArray[i]
	return ResultDict

def LaunchReadAuth(win_auth_key):

	'''
	Launches authenticator.exe 
	Requires NodeJS to be installed
	https://www.npmjs.com/package/authenticator-cli
	https://www.npmjs.com/package/pkg
	'''

	LogAndPrint(LoginLoggerObject,"LaunchReadAuth() start")
	my_location  = os.path.realpath(os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))))
	ExeFolderPath = os.path.realpath(os.path.join(my_location,"exe"))
	AuthFileLocation = os.path.realpath(os.path.join(ExeFolderPath,"authenticator.exe"))
	AuthArgs = ["--key ", win_auth_key] 

	child = subprocess.Popen([AuthFileLocation, AuthArgs], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

	rc = child.poll()

	resultString = ""

	while (True and rc == None):
		output = child.stdout.readline()
		if output == '' and child.poll() is not None:
			break
		if output:
			print(output.strip().decode())
			resultString += output.strip().decode() + "\n"

		rc = child.poll()
	
	code = ListToDict(resultString.split())['Token:']
	LogAndPrint(LoginLoggerObject,"RC: {0}".format(rc))
	LogAndPrint(LoginLoggerObject,"LaunchReadAuth() end")

	return code

def ReadWinAuthCode():

	'''
	Reads a code from wiauth_code.txt
	'''

	dirname = 'tmp'
	LogAndPrint(LoginLoggerObject, "Reading WinAuth code")

	try:
		
		mypath = os.path.realpath((os.path.join(my_location, dirname, "winauth_code.txt")))
		LogAndPrint(LoginLoggerObject, "Looking in " + mypath)
		fh = open(os.path.realpath(os.path.join(my_location, dirname, "winauth_code.txt")) , "r")
		res = fh.read()
		LogAndPrint(LoginLoggerObject, "Got code: " + str(res))
		return res
	
	except (FileNotFoundError, Exception) as e:
		
		LogAndPrint(LoginLoggerObject, e)
		LogAndPrint(LoginLoggerObject, "Got NO code using FAKE one...")
		return "123456"

def LoginToOkta(win_auth_key):

	'''
	Logging to OKTA

	'''

	# Need to add checking the login state
	time.sleep(2)
	LogAndPrint(LoginLoggerObject, "LoginToOkta started")

	# Getting login page
	driver.get("https://esri.okta.com/")	

	time.sleep(3)

	# User and password
	LogAndPrint(LoginLoggerObject, "Logging in as: " + str(okta_login))
	
	driver.find_element_by_id("okta-signin-username").clear()
	driver.find_element_by_id("okta-signin-username").send_keys(okta_login)

	driver.find_element_by_id("okta-signin-password").clear()
	driver.find_element_by_id("okta-signin-password").send_keys(okta_password)
	
	driver.find_element_by_id("okta-signin-submit").click()

	## WinAuth
	time.sleep(3)
	
	# WinAuth
	# LaunchWinAuth()
	# winauth_code = ReadWinAuthCode()
	winauth_code = LaunchReadAuth(win_auth_key)
	LogAndPrint(LoginLoggerObject, "AuthCode: {0}".format(winauth_code))

	time.sleep(3)
	elems = driver.find_elements_by_css_selector('[id^="input"]')
	elems[0].send_keys(winauth_code)

	"""
	if DEBUG == "1":
		for elem in elems:
			LogAndPrint(LoginLoggerObject, "Index: " + str(elems.index(elem)) + "ID: " + str(elem.get_attribute('id')))
			try:
				LogAndPrint(LoginLoggerObject, "Sending Keys to" + elem.get_attribute('id') )
				elem.send_keys(str(winauth_code))
			except:
				LogAndPrint(LoginLoggerObject, "no")
	"""

	# Verify button
	# Hidden in div so loop and click all
	buttons = driver.find_elements_by_class_name("o-form-button-bar")
	for button in buttons:
		button.click()

	LogAndPrint(LoginLoggerObject, "Login successful")

	return 0

def ParseOktaButtons():

	'''

	Gets all buttons on OKTA

	'''

	#Replace with EC WAIT!

	time.sleep(10)

	LogAndPrint(LoginLoggerObject, "ParseOktaButtons start")

	#Finding all buttons and their names on the page
	
	buttons = driver.find_elements_by_xpath('//*[@id="main-content"]/div/div[3]/ul[2]/li[*]/a')
	names = driver.find_elements_by_xpath('//*[@id="main-content"]/div/div[3]/ul[2]/li[*]/p')

	LogAndPrint(LoginLoggerObject, "Found buttons: " + str(buttons) + "\n")
	LogAndPrint(LoginLoggerObject, "Found names: " + str(names) + "\n")
	
	# Forming array with all buttons on OKLA

	if len(buttons) == len(names):
		res =[]
		for incr in range(0,len(buttons)):
			res.insert(incr, {'name':str(names[incr].get_attribute("oldtitle")), 'button':buttons[incr]})
	else:
		LogAndPrint(LoginLoggerObject, "Parsing buttons failed. Check page layout"  + "\n")
		exit(1)

	LogAndPrint(LoginLoggerObject, "ParseOktaButtons end")

	return res if res else exit(1)

def ClickOktaButtonByName(buttons, name):

	'''
	Clicks button by a name

	'''

	LogAndPrint(LoginLoggerObject, "ClickOktaButtonByName start")

	for button in buttons:
		LogAndPrint(LoginLoggerObject, "Processing button: " + str(button['name']) + "\n")
		if name == button['name']:
			LogAndPrint(LoginLoggerObject, "Found button: " + str(name))
			button['button'].click()
			LogAndPrint(LoginLoggerObject, "Clicked button: " + str(name))
			LogAndPrint(LoginLoggerObject, "ClickOktaButtonByName end")
			return 0
		else:
			LogAndPrint(LoginLoggerObject, "Could not click button: " + str(name))
			exit(1)

def WaitForElement(target, method=By.XPATH, callCounter=0):

	#LogAndPrint(LoginLoggerObject, "WaitForElement(): {0}".format(target))
	LogAndPrint(LoginLoggerObject, "WaitForElement(): {0}".format(callCounter))

	if callCounter >= 5:
		
		LogAndPrint(LoginLoggerObject, "MaxAttempts reached {0}".format(callCounter))
		driver.quit()
		exit(1)

	callCounter += 1

	try:

		standard_wait.until(
			EC.presence_of_element_located(
				(method, target)
				))
		LogAndPrint(LoginLoggerObject, "WaitForElement(): Target found!")

	except Exception as e:
			
			LogAndPrint(LoginLoggerObject, "WaitForElement(): Target not!")
			driver.refresh()
			time.sleep(2)
			WaitForElement(target,callCounter=callCounter)

def GoToXenApp():

	'''
	Finds "Connect to Xenapp" link after OKTA button is clicked"
	
	'''

	LogAndPrint(LoginLoggerObject, "GoToXenApp start")

	XenAppTableXPath = "/html/body/table[5]/tbody/tr/td[2]/center/table/tbody/tr/td/div[1]/div/table/tbody/tr/td/table/tbody/tr/td/div[1]/table[33]/tbody/tr/td[1]/table/tbody/tr/td[2]/a"

	WaitForElement(XenAppTableXPath)

	XenAppElement = driver.find_element_by_xpath(XenAppTableXPath)
	XenAppLink = (XenAppElement.get_attribute('href'))
	LogAndPrint(LoginLoggerObject, "XenAppLink: " + str(XenAppLink))

	driver.get(XenAppLink)

	time.sleep(2)
	LogAndPrint(LoginLoggerObject, "GoToXenApp end")

	return 0

def LoginToXenApp():

	'''
	Logs into Xenapp Frame
	'''

	LogAndPrint(LoginLoggerObject, "LoginToXenApp start")
	LoginFrameXPath = "/html/body/div/table/tbody/tr/td[1]/iframe"

	standard_wait.until(
            EC.presence_of_element_located(
            	(By.XPATH, LoginFrameXPath)
            	))

	LoginFrame = driver.find_element_by_xpath(LoginFrameXPath)
	LoginFrameLink = LoginFrame.get_attribute('src')
	LogAndPrint(LoginLoggerObject, "LoginFrameLink: " +  str(LoginFrameLink))
	driver.get(LoginFrameLink)

	time.sleep(5)

	# USERNAME AND PASSWORD
	LogAndPrint(LoginLoggerObject, "Logging in as : " + str(okta_login))

	UserNameInputXPath = "//*[@id=\"user\"]"
	standard_wait.until(
            EC.presence_of_element_located(
            	(By.XPATH, UserNameInputXPath)
            	))

	UserNameInputField = driver.find_element_by_xpath(UserNameInputXPath)
	UserNameInputField.clear()
	UserNameInputField.send_keys(okta_login)
	time.sleep(2)

	# USERNAME AND PASSWORD

	PasswordInputXPath = "//*[@id=\"password\"]"
	PasswordInputField = driver.find_element_by_xpath(PasswordInputXPath)
	PasswordInputField.clear()
	PasswordInputField.send_keys(okta_password)
	time.sleep(2)

	LoginButtonXPath = "//*[@id=\"btnLogin\"]"
	LoginButton = driver.find_element_by_xpath(LoginButtonXPath)
	LoginButton.click()
	
	time.sleep(2)
	LogAndPrint(LoginLoggerObject, "LoginToXenApp end")

	return 0

def ClickWDESkypeMenu():

	'''
	Clicks WDESkypeMenu
	'''

	LogAndPrint(LoginLoggerObject, "ClickWDESkypeMenu start")


	time.sleep(2)

	WDESkypeMenuPRDXPath = "//*[@id=\"Citrix.MPS.App.BISGreen.WDESkypeMenuPRD\"]"

	standard_wait.until(
            EC.presence_of_element_located(
            	(By.XPATH, WDESkypeMenuPRDXPath)
            	))

	WDESkypeMenuPRDElement = driver.find_element_by_xpath(WDESkypeMenuPRDXPath)
	time.sleep(2)
	WDESkypeMenuPRDElement.click()
	
	time.sleep(1)
	LogAndPrint(LoginLoggerObject, "ClickWDESkypeMenu end")
	
	return 0

def LocateAWindowByTitle(WindowTitle):

	'''
	Checking if WindowTitle is present
	Loooping until found or reached 100 attempts

	'''

	LogAndPrint(LoginLoggerObject, "LocateAWindowByTitle start")

	ExitCode = None
	AttemptsCounter = 0
	MaxAttempts = 150

	ExeFolderPath = os.path.realpath(os.path.join(my_location,"exe"))
	CheckWindowExePath = os.path.realpath(os.path.join(ExeFolderPath, "CheckWindow.exe"))

	while ExitCode !=0 and AttemptsCounter < MaxAttempts:
		child = subprocess.Popen([CheckWindowExePath, WindowTitle], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

		for line in child.stdout.readlines():
			child.wait()
			# Outputs title and handle
			#LogAndPrint(LoginLoggerObject, line)
			ExitCode=child.returncode

		time.sleep(5)
		AttemptsCounter = AttemptsCounter + 1
		LogAndPrint(LoginLoggerObject, "Attempt " + str(AttemptsCounter))
		LogAndPrint(LoginLoggerObject, "ExitCode: " + str(ExitCode))

	if (AttemptsCounter == MaxAttempts and ExitCode !=0):
		LogAndPrint(LoginLoggerObject, "MaxAttempts reached: " + str(AttemptsCounter) + "/" + str(MaxAttempts))
		LogAndPrint(LoginLoggerObject, "LocateAWindowByTitle end")
		exit(1)
	else:
		LogAndPrint(LoginLoggerObject, "Window \"{0}\" found, proceed".format(WindowTitle))
		time.sleep(3)
	
	LogAndPrint(LoginLoggerObject, "LocateAWindowByTitle end")

	return 0

def LocateWindowByTitleNew(WindowTitle):
	
	if not WindowTitle:
		LogAndPrint(LoginLoggerObject, "LocateWindowByTitle(): No WindowTitle is supplied")
		exit(1)

	ExeFolderPath = os.path.realpath(os.path.join(my_location,"exe"))
	CheckWindowExePath = os.path.realpath(os.path.join(ExeFolderPath, "CheckWindow.exe"))

	child = subprocess.Popen([CheckWindowExePath, WindowTitle], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

	rc = child.poll()

	while (True and rc == None):
		output = child.stdout.readline()
		if output == '' and child.poll() is not None:
			break
		if output:
			LogAndPrint(LoginLoggerObject, output.strip().decode())

		rc = child.poll()
		LogAndPrint(LoginLoggerObject, "RC: {0}".format(rc))

	LogAndPrint(LoginLoggerObject, "LocateWindowByTitleNew end")

	return 0

def ProcessWDE(RequestedFunction):

	'''
	Clicks remote window buttons
	
	RequestedFunction = [ 'LogInToSkype', 'LogInToWDE', 'SetAtDeskWDE' ]

	'''

	LogAndPrint(LoginLoggerObject, "ProcessWDE start: {0}".format(RequestedFunction))
	
	time.sleep(2)

	LogAndPrint(LoginLoggerObject, "Starting exe file...")
	ExeFolderPath = os.path.realpath(os.path.join(my_location,"exe"))
	ProcessWDEExePath = os.path.realpath(os.path.join(ExeFolderPath, "ProcessWDE.exe"))

	child = subprocess.Popen([ProcessWDEExePath, RequestedFunction], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	# I can traverse exe output to Python and log in if necessary in the future

	'''
	for line in child.stdout.readlines():
		child.wait()
		# Outputs title and handle
		LogAndPrint(LoginLoggerObject, line)
		ExitCode=child.returncode
	'''

	rc = child.poll()
	
	#rcstring = "RC: " + str(rc)
	#LogAndPrint(LoginLoggerObject, rcstring)


	while True and (rc == None or rc == 1):
		output = child.stdout.readline()
		if output == '' and child.poll() is not None:
			break
		if output:
			LogAndPrint(LoginLoggerObject, output.strip().decode())

		rc = child.poll()

		#rcstring = "RC: " + str(rc)
		#LogAndPrint(LoginLoggerObject, rcstring)

	time.sleep(2)

	LogAndPrint(LoginLoggerObject, "ProcessWDE end: {0}".format(RequestedFunction))

	return 0


# CONSTANTS
my_location  = os.path.realpath(os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))))
config_location = os.path.join(my_location , "tmp", "creds.txt")

my_parser = ConfigParser()
my_parser.read(config_location)

okta_login = my_parser.get("Credentials","User")
okta_password = my_parser.get("Credentials","Pass")
win_auth_key = my_parser.get("Credentials","AuthKey")

#win_auth_file_name = "winauth_code.txt"

# MAIN IS HERE

LoginLoggerObject = InitLogger()

#VideoHandlerInstance = InitCapture()
#StartVideoCapture(VideoHandlerInstance)

[driver,standard_wait] = InitDriver()

# Handle OKTA
LoginToOkta(win_auth_key)
OktaButtonsArray = ParseOktaButtons()

# Connect TO VPN button
ClickOktaButtonByName(OktaButtonsArray, "US-West VPN (Redlands Tech Support)")

# Waiting for Pulse page to load, better replace with EC Wait
LogAndPrint(LoginLoggerObject, "Sleeping...")
time.sleep(15)

# Switch to second tab is necessary 
second_tab = driver.window_handles[1]
driver.switch_to.window(second_tab)
time.sleep(2)
driver.refresh()
time.sleep(2)

LogAndPrint(LoginLoggerObject, "Sleeping...end")

GoToXenApp()
time.sleep(2)
LoginToXenApp()
time.sleep(5)

ClickWDESkypeMenu()

WindowTitle = "Support Services - \\\\Remote"
LocateAWindowByTitle(WindowTitle)

time.sleep(5)

ProcessWDE("LogInToSkype")
time.sleep(5)

ProcessWDE("LogInToWDE")
time.sleep(5)

ProcessWDE("SetAtDeskWDE")

time.sleep(5)
#StopVideoCapture(VideoHandlerInstance)