# import the necessary packages
from __future__ import print_function
from imutils.video.pivideostream import PiVideoStream
from picamera.array import PiRGBArray
from picamera import PiCamera
import argparse
import imutils
import time
import tkinter

root = tkinter.Tk()
screen_W = root.winfo_screenwidth()
screen_H = root.winfo_screenheight()
preview_W = 320
preview_H = 320
preview_mid_X = int(screen_W/2 - preview_W/2)
preview_mid_Y = int(screen_H/2 - preview_H/2)

stream = PiVideoStream().start()
stream.camera.resolution = (320, 320)
stream.camera.framerate = 24
stream.camera.start_preview(fullscreen=False, layer=0, window=(preview_mid_X, preview_mid_Y, preview_W, preview_H))
time.sleep(2.0)
 
# loop over some frames...this time using the threaded stream
while True:
	frame = stream.read()
 
# do a bit of cleanup
stream.stop()
