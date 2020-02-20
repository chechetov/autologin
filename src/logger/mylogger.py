import os
import logging
from datetime import date
from datetime import datetime

class MyLogger(object):

	def __init__(self, LogFileName):

		'''
		Looks for log folder one level upper the package exists 
		Creates if cant fild one

		Expects a file name

		'''
		self.MyLocation = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
		self.LogFolderLocation = os.path.realpath(os.path.join(self.MyLocation, os.pardir, "log"))

		# Cleaning up old logs
		for root, dirs, files in os.walk(self.LogFolderLocation):
			for f in files:
				os.unlink(os.path.join(root, f))
			for d in dirs:
				shutil.rmtree(os.path.join(root,d))


		if not os.path.exists(self.LogFolderLocation):
			os.mkdir(self.LogFolderLocation)

		self.TodayDate   = date.today().strftime("%d-%m-%Y")
		
		self.CurrentTime = datetime.now()
		self.CurrentTimeForPrint = self.CurrentTime.strftime("%H:%M:%S")[:19]
		self.CurrentTimeForLogName = self.CurrentTime.strftime("%H-%M-%S")[:19]

		self.LogFileName = str(LogFileName) + str(self.TodayDate) + "_" + str(self.CurrentTimeForLogName) + ".log"
		self.FullLogFileName = os.path.join(self.LogFolderLocation,self.LogFileName)

		self.LogFileHandler = logging.FileHandler("{0}/{1}".format(self.LogFolderLocation, self.LogFileName))
		self.LogFileFormatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
		self.LogFileHandler.setFormatter(self.LogFileFormatter)
		self.MyLoggerObject = logging.getLogger(LogFileName)
		self.MyLoggerObject.setLevel(logging.INFO)
		self.MyLoggerObject.addHandler(self.LogFileHandler)

		self.MyLoggerObject.info("\nMyLogger: started at {0} in {1} \n".format(self.CurrentTimeForPrint, self.FullLogFileName))
		
		print("\nMyLogger: started at {0} in {1} \n".format(self.CurrentTimeForPrint, self.FullLogFileName))
		
		self.MyLoggerObject.setLevel(logging.INFO)
		
	def LogAndPrint(self, message):
		self.MyLoggerObject.info(message)
		print(message)

	def LogNoPrint(self, message):
		self.MyLoggerObject.info(message)