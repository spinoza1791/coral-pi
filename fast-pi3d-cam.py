#!/usr/bin/python3
from __future__ import absolute_import, division, print_function, unicode_literals
import pi3d
import math
import tkinter
import numpy as np
import io
import edgetpu.detection.engine
import picamera
import picamera.array
import argparse
import time
import threading

parser = argparse.ArgumentParser()
parser.add_argument(
  '--model', help='File path of Tflite model.', required=True)
parser.add_argument(
  '--dims', help='Model input dimension', required=True)
args = parser.parse_args()

########################################################################

#Set all input params equal to the input dimensions expected by the model
mdl_dims = int(args.dims) #dims must be a factor of 32/16 for picamera resolution
#engine = edgetpu.detection.engine.DetectionEngine(args.model)

root = tkinter.Tk()
screen_W = root.winfo_screenwidth()
screen_H = root.winfo_screenheight()
preview_W = mdl_dims
preview_H = mdl_dims
preview_mid_X = int(screen_W/2 - preview_W/2)
preview_mid_Y = int(screen_H/2 - preview_H/2)

max_obj = 10
max_fps = 24

DISPLAY = pi3d.Display.create(0, 0, w=preview_W, h=preview_H, layer=1, frames_per_second=max_fps)
DISPLAY.set_background(0.0, 0.0, 0.0, 0.0) # transparent
txtshader = pi3d.Shader("uv_flat")
linshader = pi3d.Shader('mat_flat')

# Fetch key presses
keybd = pi3d.Keyboard()
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
i = 0
last_tm = time.time()

X_OFF = np.array([0, 0, -1, -1, 0, 0, 1, 1])
Y_OFF = np.array([-1, -1, 0, 0, 1, 1, 0, 0])
X_IX = np.array([0, 1, 1, 1, 1, 0, 0, 0])
Y_IX = np.array([0, 0, 0, 1, 1, 1, 1, 0])
verts = [[0.0, 0.0, 1.0] for i in range(8 * max_obj)] # need a vertex for each end of each side 
bbox = pi3d.Lines(vertices=verts, material=(1.0,0.8,0.05), closed=False, strip=False, line_width=4) 
bbox.set_shader(linshader)
results = None
old_results = None
output = None
frame_buf_val= None

########################################################################

NBYTES = mdl_dims * mdl_dims * 3
new_pic = False

# Create a pool of image processors
done = False
lock = threading.Lock()
pool = []

class ImageProcessor(threading.Thread):
    def __init__(self):
        super(ImageProcessor, self).__init__()
        self.engine = edgetpu.detection.engine.DetectionEngine(args.model)
        self.rawCapture = bytearray(320 * 320 * 3)
        self.stream = io.BytesIO()
        self.event = threading.Event()
        self.terminated = False
        self.start()

    def run(self):
        # This method runs in a separate thread
        global done, npa, new_pic, mdl_dims, NBYTES, bbox, X_OFF, Y_OFF, X_IX, Y_IX, verts, bbox
        while not self.terminated:
            # Wait for an image to be written to the stream
            #if self.event.wait(0.01):
            try:
                if self.stream.tell() >= NBYTES:
                  self.stream.seek(0)
                  self.stream.readinto(self.rawCapture)
                  self.input_val = np.frombuffer(self.stream.getvalue(), dtype=np.uint8)
                  self.stream.truncate()
                  self.output = self.engine.DetectWithInputTensor(self.input_val, top_k=10)
                  if self.output:
                    num_obj = 0
                    for obj in self.output:
                  num_obj = num_obj + 1   
                  buf = bbox.buf[0] # alias for brevity below
                  buf.array_buffer[:,:3] = 0.0;
                  for j, obj in enumerate(self.output):
                    coords = (obj.bounding_box - 0.5) * [[1.0, -1.0]] * mdl_dims # broadcasting will fix the arrays size differences
                    score = round(obj.score,2)
                    ix = 8 * j
                    buf.array_buffer[ix:(ix + 8), 0] = coords[X_IX, 0] + 2 * X_OFF
                    buf.array_buffer[ix:(ix + 8), 1] = coords[Y_IX, 1] + 2 * Y_OFF
                  buf.re_init(); # 
                  bbox.draw() # i.e. one draw for all boxes
                  #else:
                  #  results = None
                  #bnp = np.array(self.stream.getbuffer(),
                  #              dtype=np.uint8).reshape(CAMH, CAMW, 3)
                  #npa[:,:,0:3] = bnp
                  #new_pic = True
            except Exception as e:
              print(e)
            finally:
                # Reset the stream and event
                #self.stream.seek(0)
                #self.stream.truncate()
                #self.event.clear()
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


def start_capture(): # has to be in yet another thread as blocking
  global mdl_dims, pool
  with picamera.PiCamera() as camera:
    pool = [ImageProcessor() for i in range(3)]
    camera.resolution = (mdl_dims, mdl_dims)
    camera.framerate = 24
    camera.start_preview(fullscreen=False, layer=0, window=(0, 0, 320, 320))
    time.sleep(2)
    camera.capture_sequence(streams(), format='rgb', use_video_port=True)
    #camera.capture(streams(), use_video_port=True, format='rgb')

t = threading.Thread(target=start_capture)
t.start()

#while not new_pic:
#    time.sleep(0.01)

while DISPLAY.loop_running():
    fps_txt.draw()   
    #ms_txt.draw()
    #ms = str(elapsed_ms*1000)
    #ms_txt.quick_change(ms)
    i += 1
    if i > N:
        tm = time.time()
        fps = "{:5.1f}FPS".format(i / (tm - last_tm))
        fps_txt.quick_change(fps)
        i = 0
        last_tm = tm
    if keybd.read() == 27:
      keybd.close()
      DISPLAY.destroy()
      break

# Shut down the processors in an orderly fashion
while pool:
  done = True
  with lock:
    processor = pool.pop()
  processor.terminated = True
  processor.join()
