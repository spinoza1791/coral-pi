#!/usr/bin/python3
from __future__ import absolute_import, division, print_function, unicode_literals
import pi3d
import math
import tkinter
import numpy as np
import io
import edgetpu.detection.engine
import imutils
from imutils.video.pivideostream import PiVideoStream
from picamera.array import PiRGBArray
import picamera
import argparse
import time
import threading

parser = argparse.ArgumentParser()
parser.add_argument(
  '--model', help='File path of Tflite model.', required=False)
parser.add_argument(
  '--dims', help='Model input dimension', required=False)
args = parser.parse_args()

# Create a pool of image processors
done = False
lock = threading.Lock()
pool = []

class ImageProcessor(threading.Thread):
	def __init__(self):
		super(ImageProcessor, self).__init__()
		self.rawCapture = bytearray(320 * 320 * 3)
		self.stream = io.BytesIO()
		self.event = threading.Event()
		self.terminated = False
		self.start()

def run(self):
	# This method runs in a separate thread
	global done
	while not self.terminated:
		if self.event.wait(1):
			try:
				self.stream.seek(0)
				self.stream.readinto(self.rawCapture)
				self.input_frame = np.frombuffer(self.stream.getvalue(), dtype=np.uint8)
				#self.stream.truncate(0)
				self.result = self.engine.DetectWithInputTensor(self.input_frame, top_k=10)
				# Read the image and do some processing on it
				#Image.open(self.stream)
				#...
				#...
				# Set done to True if you want the script to terminate
				# at some point
				#done=True
			finally:
				# Reset the stream and event
				self.stream.seek(0)
				self.stream.truncate()
				self.event.clear()
				# Return ourselves to the pool
				with lock:
					pool.append(self)

def streams():
    while not done:
        with lock:
            if pool:
                processor = pool.pop()
            else:
                processor = None
        if processor:
            yield processor.stream
            processor.event.set()
        else:
            # When the pool is starved, wait a while for it to refill
            time.sleep(0.1)

#Set all input params equal to the input dimensions expected by the model
mdl_dims = int(args.dims) #dims must be a factor of 32 for picamera resolut$

#Set max num of objects you want to detect per frame
max_obj = 10
max_fps = 24
engine = edgetpu.detection.engine.DetectionEngine(args.model)

root = tkinter.Tk()
screen_W = root.winfo_screenwidth()
screen_H = root.winfo_screenheight()
preview_W = mdl_dims
preview_H = mdl_dims
preview_mid_X = int(screen_W/2 - preview_W/2)
preview_mid_Y = int(screen_H/2 - preview_H/2)

DISPLAY = pi3d.Display.create(0, 0, w=preview_W, h=preview_H, layer=1, frames_per_second=max_fps)
DISPLAY.set_background(0.0, 0.0, 0.0, 0.0) # transparent
keybd = pi3d.Keyboard()
txtshader = pi3d.Shader("uv_flat")
linshader = pi3d.Shader('mat_flat')

CAMERA = pi3d.Camera(is_3d=False)
font = pi3d.Font("fonts/FreeMono.ttf", font_size=30, color=(0, 255, 0, 255)) # blue green 1.0 alpha

elapsed_ms = 1000
ms = str(elapsed_ms)
ms_txt = pi3d.String(camera=CAMERA, is_3d=False, font=font, string=ms, x=0, y=preview_H/2 - 30, z=1.0)
ms_txt.set_shader(txtshader)

fps = "00.0 fps"
N = 10
fps_txt = pi3d.String(camera=CAMERA, is_3d=False, font=font, string=fps, x=0, y=preview_H/2 - 10, z=1.0)
fps_txt.set_shader(txtshader)

X_OFF = np.array([0, 0, -1, -1, 0, 0, 1, 1])
Y_OFF = np.array([-1, -1, 0, 0, 1, 1, 0, 0])
X_IX = np.array([0, 1, 1, 1, 1, 0, 0, 0])
Y_IX = np.array([0, 0, 0, 1, 1, 1, 1, 0])
verts = [[0.0, 0.0, 1.0] for i in range(8 * max_obj)] # need a vertex for each end of each side 
bbox = pi3d.Lines(vertices=verts, material=(1.0,0.8,0.05), closed=False, strip=False, line_width=4) 
bbox.set_shader(linshader)

i = 0
last_tm = time.time()

with picamera.PiCamera() as camera:
	keybd = pi3d.Keyboard()
	pool = [ImageProcessor() for i in range (4)]
	camera.resolution = (320, 320)
	# Set the framerate appropriately; too fast and the image processors
	# will stall the image pipeline and crash the script
	camera.framerate = 24
	camera.start_preview(fullscreen=False, layer=0, window=(0, 0, 320, 320))
	time.sleep(2)
	camera.capture_sequence(streams(), use_video_port=True)
	while DISPLAY.loop_running():
		print("display running")
		fps_txt.draw()
		ms_txt.draw()
		ms = str(elapsed_ms*1000)
		ms_txt.quick_change(ms)
		i += 1
		if i > N:
			tm = time.time()
			fps = "{:5.1f}FPS".format(i / (tm - last_tm))
			fps_txt.quick_change(fps)
			i = 0
			last_tm = tm
		#results = thread.read()
		if results:
			num_obj = 0
			for obj in results:
				num_obj = num_obj + 1   
				buf = bbox.buf[0] # alias for brevity below
				buf.array_buffer[:,:3] = 0.0;
				for j, obj in enumerate(results):
					coords = (obj.bounding_box - 0.5) * [[1.0, -1.0]] * mdl_dims # broadcasting will fix the arrays size differences
					score = round(obj.score,2)
					ix = 8 * j
					buf.array_buffer[ix:(ix + 8), 0] = coords[X_IX, 0] + 2 * X_OFF
					buf.array_buffer[ix:(ix + 8), 1] = coords[Y_IX, 1] + 2 * Y_OFF
				buf.re_init(); # 
				bbox.draw() # i.e. one draw for all boxes
		if keybd.read() == 27:
			break

# Shut down the processors in an orderly fashion
while pool:
    with lock:
        processor = pool.pop()
    processor.terminated = True
    processor.join()
