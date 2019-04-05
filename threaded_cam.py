#!/usr/bin/python3
from __future__ import absolute_import, division, print_function, unicode_literals
import pi3d
import math
import tkinter
import numpy as np
import io
import edgetpu.detection.engine
#from imutils.video.pivideostream import PiVideoStream
#from picamera.array import PiRGBArray
import picamera
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
engine = edgetpu.detection.engine.DetectionEngine(args.model)

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
linshader = pi3d.Shader('mat_flat')

CAMERA = pi3d.Camera(is_3d=False)
font = pi3d.Font("fonts/FreeMono.ttf", font_size=30, color=(0, 255, 0, 255)) # blue green 1.0 alpha

elapsed_ms = 1
ms = "00ms"
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

#thread = PiVideoStream().start()
#thread.camera.resolution = (mdl_dims, mdl_dims)
#thread.camera.framerate = max_fps
#thread.camera.start_preview(fullscreen=False, layer=0, window=(preview_mid_X, preview_mid_Y, preview_W, preview_H))
#time.sleep(1.0)

with picamera.PiCamera() as camera:
    camera.resolution = (preview_W, preview_H)
    camera.framerate = max_fps
    #camera.color_effects = (128,128)
    #bgr = PiRGBArray(camera, size=camera.resolution * 3)
    rgb = bytearray(camera.resolution[0] * camera.resolution[1] * 3)
    #rgb.reshape(rgb * [0.2989, 0.5870, 0.1140]).sum(axis=2).astype(np.uint8)
    #_, width, height, channels = engine.get_input_tensor_shape()
    camera.start_preview(fullscreen=False, layer=0, window=(preview_mid_X, preview_mid_Y, preview_W, preview_H))
    time.sleep(2) #camera warm-up
 
try: 
	while DISPLAY.loop_running():
		stream = io.BytesIO()
		start_ms = time.time() 
		camera.capture(stream, use_video_port=True, format='rgb', resize=(320, 320))
		elapsed_ms = time.time() - start_ms
		stream.seek(0)
		stream.readinto(rgb)
		#stream.truncate(0)
		input = np.frombuffer(stream.getvalue(), dtype=np.uint8)
		results = engine.DetectWithInputTensor(input, top_k=max_obj)
		#thread.update()
		#input = thread.read()
		#if input:
	#		results = engine.DetectWithInputTensor(input, top_k=max_obj)
		#else :
		#	results = None
		elapsed_ms = time.time() - start_ms 
		ms = str(elapsed_ms*1000)+"ms"
		ms_txt.draw()
		ms_txt.quick_change(ms)
		fps_txt.draw()	
		i += 1
		if i > N:
			tm = time.time()
			fps = "{:5.1f}FPS".format(i / (tm - last_tm))
			fps_txt.quick_change(fps)
			i = 0
			last_tm = tm
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
			
finally:
	keybd.close()
	DISPLAY.destroy()
	camera.stop_preview()
	#thread.stop()
