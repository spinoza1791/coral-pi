#!/usr/bin/python3
from __future__ import absolute_import, division, print_function, unicode_literals
from picamera.array import PiRGBArray
import picamera
import time
import pi3d
import math
import tkinter
import numpy as np
import argparse
import io
import edgetpu.detection.engine

parser = argparse.ArgumentParser()
parser.add_argument(
  '--model', help='File path of Tflite model.', required=True)
parser.add_argument(
  '--dims', help='Model input dimension', required=True)
args = parser.parse_args()

#Set all input params equal to the input dimensions expected by the model
mdl_dims = int(args.dims) #dims must be a factor of 32 for picamera resolut$

#Set max num of objects you want to detect per frame
max_obj = 20
max_fps = 40
engine = edgetpu.detection.engine.DetectionEngine(args.model)

root = tkinter.Tk()
screen_W = root.winfo_screenwidth()
screen_H = root.winfo_screenheight()
preview_W = 320
preview_H = 320
preview_mid_X = int(screen_W/2 - preview_W/2)
preview_mid_Y = int(screen_H/2 - preview_H/2)

DISPLAY = pi3d.Display.create(preview_mid_X, preview_mid_Y, w=preview_W, h=preview_H, layer=1, frames_per_second=max_fps)
DISPLAY.set_background(0.0, 0.0, 0.0, 0.0) # transparent
keybd = pi3d.Keyboard()
txtshader = pi3d.Shader("uv_flat")
linshader = pi3d.Shader('mat_flat')
CAMERA = pi3d.Camera(is_3d=False)
font = pi3d.Font("fonts/FreeMono.ttf", font_size=30, color=(0, 255, 0, 255)) # blue green 1.0 alpha
Z = 1.0
bbox_vertices = [[-0.5, 0.5, Z], [0.5, 0.5, Z],
                 [0.5, -0.5, Z], [-0.5, -0.5, Z]] # sides 1.0 x 1.0
bbox = pi3d.Lines(vertices=bbox_vertices, material=(1.0,0.8,0.05), closed=True, line_width=4) 
bbox.set_shader(linshader)
fps = "00.00FPS"
N = 10
fps_txt = pi3d.String(camera=CAMERA, is_3d=False, font=font, string=fps, x=0, y=preview_H/2 - 10, z=1.0)
fps_txt.set_shader(txtshader)
elapsed_ms = 1/1000
ms = "00ms"
ms_txt = pi3d.String(camera=CAMERA, is_3d=False, font=font, string=ms, x=0, y=preview_H/2 - 30, z=1.0)
ms_txt.set_shader(txtshader)
last_tm = time.time()
i = 0

with picamera.PiCamera() as camera:
    camera.resolution = (preview_W, preview_H)
    camera.framerate = max_fps
    rgb = PiRGBArray(camera, size=camera.resolution * 3)
    _, width, height, channels = engine.get_input_tensor_shape()
    camera.start_preview(fullscreen=False, layer=0, window=(preview_mid_X, preview_mid_Y, preview_W, preview_H))
    try:
        stream = io.BytesIO()
        while DISPLAY.loop_running():
            camera.capture(stream, use_video_port=True, format='rgb')
            stream.truncate()
            stream.seek(0)
            input = np.frombuffer(stream.getvalue(), dtype=np.uint8)
            start_ms = time.time()
            results = engine.DetectWithInputTensor(input, top_k=max_obj)
            elapsed_ms = time.time() - start_ms
            ms = str(int(elapsed_ms*1000))+"ms"
            ms_txt.draw()
            ms_txt.quick_change(ms)                
            fps_txt.draw()
            i += 1
            if i > N:
                tm = time.time()
                fps = "{:6.2f}FPS".format(i / (tm - last_tm))
                fps_txt.quick_change(fps)
                i = 0
                last_tm = tm
            if results:
                num_obj = 0
                for obj in results:
                    num_obj = num_obj + 1
                for obj in results:
                    coords = (obj.bounding_box - 0.5) * [[1.0, -1.0]] * mdl_dims # broadcasting will fix the arrays size differences
                    score = round(obj.score,2)
                    (x_scale, y_scale) = coords[1] - coords[0] # will result in 1D array then cast to tuple
                    (x_mid, y_mid) = coords.mean(axis=0) # again will result in tuple
                    bbox.scale(x_scale, y_scale, 1.0)
                    bbox.position(x_mid, y_mid, Z)
                    bbox.draw()

            if keybd.read() == 27:
                break
        stream.close()
    finally:
        keybd.close()
        DISPLAY.destroy()
        camera.close()
