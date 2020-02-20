from PIL import Image, ImageGrab, ImageDraw
from threading import Thread
from logger.mylogger import MyLogger
from datetime import datetime
from datetime import date

import threading
import time
import os
import glob
import win32gui
import ctypes
import imageio
import moviepy.editor as mp

ctypes.windll.user32.SetProcessDPIAware() # for DPI scaling


class VideoHandler(Thread):

    def __init__(self):

        self.StartTime = time.time()

        self.MyLocation   = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        self.OutputFolder = os.path.realpath(os.path.join(self.MyLocation, "output"))
        self.LoggerObject = MyLogger("Capture_")
        #self._daemonic = True
        
        self.LogNoPrint("VideoHandler: capture start (init)")
        self.CaptureTimeout = 240


        self.Capture = True
        Thread.__init__(self, name="VideoHandler Thread One")

    def LogNoPrint(self, Message):
        self.LoggerObject.LogNoPrint(Message)

    def run(self,delaySec=1/5):

        """capture and save screenshot(s)"""

        if not os.path.exists(self.OutputFolder):
            os.mkdir(self.OutputFolder)

        for fname in glob.glob("{0}/*.jpg".format(self.OutputFolder)):
            os.remove(fname)

        imCursor = Image.open(os.path.join(self.MyLocation,'cursor.png'))

        n = 0

        while self.Capture:

            if time.time() - self.StartTime > self.CaptureTimeout:
                self.LogNoPrint("Stopping capture: time reached: {0}".format(round(time.time() - self.StartTime),1))
                break

            #self.LogNoPrint("Capture: {0} Self: {1}".format(self.Capture, self))
            n = n + 1
            im   = ImageGrab.grab()
            draw = ImageDraw.Draw(im)
            draw.text( (0, 0), datetime.now().strftime("%d-%m-%y__%H-%M-%S")[:19] )
            curX,curY=win32gui.GetCursorPos()
            im.paste(imCursor,box=(curX,curY),mask=imCursor)
            fname="output/%.02f.jpg"%time.time()
            self.LogNoPrint("saving [%s] (%d)"%(fname,n+1))
            im.save(os.path.join(self.MyLocation, fname))
            if delaySec:
                time.sleep(delaySec)

    def convert(self):

        self.LogNoPrint("VideoHandler : convert start")

        self.CurrentTimeForConvert = datetime.now().strftime("%d-%m-%y__%H-%M-%S")[:19]
        
        InFile  = os.path.join(self.OutputFolder, "movie_{0}.gif".format(self.CurrentTimeForConvert))
        OutFile = os.path.join(self.OutputFolder, "movie_{0}.mp4".format(self.CurrentTimeForConvert))
        filenames = os.listdir(self.OutputFolder)

        try:
            with imageio.get_writer(InFile, mode='I') as writer:
                for filename in filenames:
                    image = imageio.imread(os.path.join(self.OutputFolder,filename))
                    writer.append_data(image)
        except Exception as e:
            print("Gif forming failed")
            print(e)

        clip = mp.VideoFileClip(InFile)
        clip.write_videofile(OutFile)

        for fname in glob.glob("{0}/*.jpg".format(self.OutputFolder)):
            os.remove(fname)

        self.LogNoPrint("VideoHandler : convert done")

    def stop(self):
        self.LogNoPrint("VideoHandler: capture stop")
        self.Capture = False
        self.convert()



