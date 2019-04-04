# import the necessary packages
from __future__ import print_function
from imutils.video.pivideostream import PiVideoStream
from imutils.video import FPS
from picamera.array import PiRGBArray
from picamera import PiCamera
import argparse
import imutils
import time
import pi3d
import tkinter
import numpy as np
import io
import edgetpu.detection.engine
from threading import Thread

# construct the argument parse and parse the arguments
parser = argparse.ArgumentParser()
parser.add_argument(
'--model', help='File path of Tflite model.', required=False)
parser.add_argument(
'--dims', help='Model input dimension', required=True)
args = parser.parse_args()
mdl_dims = int(args.dims)
max_obj = 5
engine = edgetpu.detection.engine.DetectionEngine(args.model)

root = tkinter.Tk()
screen_W = root.winfo_screenwidth()
screen_H = root.winfo_screenheight()
preview_W = mdl_dims
preview_H = mdl_dims
preview_mid_X = int(screen_W/2 - preview_W/2)
preview_mid_Y = int(screen_H/2 - preview_H/2)

pi3d_display = pi3d.Display.create(preview_mid_X, preview_mid_Y, w=preview_W, h=preview_H, layer=1) #, frames_per_$
pi3d_display.set_background(0.0, 0.0, 0.0, 0.0) # transparent
pi3d_CAMERA = pi3d.Camera(is_3d=False)
linshader = pi3d.Shader('mat_flat')
txtshader = pi3d.Shader("uv_flat")
font = pi3d.Font("fonts/FreeSans.ttf", font_size=20, color=(255, 255, 0, 255)) 

x1=x2=x3=x4=x5=y1=y2=y3=y4=y5=z= 1
bbox = pi3d.Lines(vertices=[[x1,y1,z], [x2,y2,z], [x3,y3,z], [x4,y4,z], [x5,y5,z]], line_width=2)
bbox.set_shader(linshader)

fps = "000.00FPS"
N = 100
fps_txt = pi3d.String(camera=pi3d_CAMERA, is_3d=False, font=font, string=fps, x=0, y=preview_H/2 - 150, z=1.0)
fps_txt.set_shader(txtshader)
last_tm = time.time()
fps_cnt = 0

stream = PiVideoStream().start()
#stream.rawCapture = bytearray(stream.camera.resolution[0] * stream.camera.resolution[1] * 3)
#_, width, height, channels = engine.get_input_tensor_shape()
#stream.camera.capture_continuous(stream.rawCapture, format="rgb", use_video_port=True)

#rgb = bytearray(stream.camera.resolution[0] * stream.camera.resolution[1] * 3)
_, width, height, channels = engine.get_input_tensor_shape()
stream.camera.start_preview(fullscreen=False, layer=0, window=(preview_mid_X, preview_mid_Y, preview_W, preview_H))
time.sleep(2.0)
keybd = pi3d.Keyboard()

try:
    while pi3d_display.loop_running():
        #frame = io.BytesIO()
        frame = stream.read()
        print(frame.shape)
        #frame = imutils.resize(frame, width=mdl_dims)
        #print(frame.shape)
        #time.sleep(0.5)
        #stream.readinto(rgb)
        #input = np.frombuffer(stream.getvalue(), dtype=np.uint8)
        #input = frame.getvalue()
        input = frame.reshape((width * height * channels))
        #input = np.frombuffer(frame.getvalue(), dtype=np.uint8)
        results = engine.DetectWithInputTensor(input, top_k=max_obj)
        fps_txt.draw()
        fps_cnt += 1
        if fps_cnt > N:
            tm = time.time()
            fps = "{:6.2f}FPS".format(fps_cnt / (tm - last_tm))
            fps_txt.quick_change(fps)
            fps_cnt = 0
            last_tm = tm
        #if results:
        #    num_obj = 0
        #    for obj in results:
        #        num_obj = num_obj + 1
        #    for obj in results:
        #        bbox = obj.bounding_box.flatten().tolist()
        #        score = round(obj.score,2)
        #        bbox_x1 = round(bbox[0] * mdl_dims)
        #        bbox_y1 = round(bbox[1] * mdl_dims)
        #        bbox_x2 = round(bbox[2] * mdl_dims)
        #        bbox_y2 = round(bbox[3] * mdl_dims)
        #        x1, x2, x3, x4, x5, y1, y2, y3, y4, y5 = bbox_calc(bbox_x1, bbox_y1, bbox_x2, bbox_y2, mdl_dims)
        #        bbox = pi3d.Lines(vertices=[[x1,y1,z], [x2,y2,z], [x3,y3,z], [x4,y4,z], [x5,y5,z]], line_width=2)
        #        bbox.draw()

        if keybd.read() == 27:
            break
finally:
    keybd.close()
    stream.stop()
    #camera.stop_preview()
    #camera.close()
