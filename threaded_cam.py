#!/usr/bin/python3
from __future__ import absolute_import, division, print_function, unicode_literals
import pi3d
import math
import tkinter
import numpy as np
import io
import edgetpu.detection.engine
from imutils.video.pivideostream import PiVideoStream
from picamera.array import PiRGBArray
from picamera import PiCamera
import argparse
import imutils
import time

parser = argparse.ArgumentParser()
parser.add_argument(
  '--model', help='File path of Tflite model.', required=False)
parser.add_argument(
  '--dims', help='Model input dimension', required=True)
args = parser.parse_args()

#Set all input params equal to the input dimensions expected by the model
mdl_dims = int(args.dims) #dims must be a factor of 32 for picamera resolut$

#Set max num of objects you want to detect per frame
max_obj = 10
max_fps = 24
#engine = edgetpu.detection.engine.DetectionEngine(args.model)

root = tkinter.Tk()
screen_W = root.winfo_screenwidth()
screen_H = root.winfo_screenheight()
preview_W = mdl_dims
preview_H = mdl_dims
preview_mid_X = int(screen_W/2 - preview_W/2)
preview_mid_Y = int(screen_H/2 - preview_H/2)

DISPLAY = pi3d.Display.create(preview_mid_X, preview_mid_Y, w=preview_W, h=preview_H, layer=1, frames_per_second=max_fps)
DISPLAY.set_background(0.0, 0.0, 0.0, 0.0) # transparent
keybd = pi3d.Keyboard()
txtshader = pi3d.Shader("uv_flat")

CAMERA = pi3d.Camera(is_3d=False)
font = pi3d.Font("fonts/FreeMono.ttf", font_size=30, color=(0, 255, 0, 255)) # blue green 1.0 alpha

elapsed_ms = 1/1000
ms = "00ms"
ms_txt = pi3d.String(camera=CAMERA, is_3d=False, font=font, string=ms, x=0, y=preview_H/2 - 30, z=1.0)
ms_txt.set_shader(txtshader)

stream = PiVideoStream().start()
stream.camera.resolution = (320, 320)
stream.camera.framerate = max_fps
stream.camera.start_preview(fullscreen=False, layer=0, window=(preview_mid_X, preview_mid_Y, preview_W, preview_H))
time.sleep(2.0)
 
# loop over some frames...this time using the threaded stream
try: 
	while DISPLAY.loop_running():
		start_ms = time.time() 
		frame = stream.read()
		elapsed_ms = time.time() - start_ms           
		ms = str(int(elapsed_ms*100000))+"ms"
		#ms_txt.draw()
		#ms_txt.quick_change(ms)
		if keybd.read() == 27:
			break
			
finally:
	keybd.close()
	DISPLAY.destroy()
	stream.close()
