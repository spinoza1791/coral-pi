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
import picamera.array
import argparse
import time
import threading
from math import cos, sin, radians

parser = argparse.ArgumentParser()
parser.add_argument(
  '--model', help='File path of Tflite model.', required=False)
parser.add_argument(
  '--dims', help='Model input dimension', required=False)
args = parser.parse_args()

#Set all input params equal to the input dimensions expected by the model
mdl_dims = int(args.dims) #dims must be a factor of 32 for picamera resolut$

root = tkinter.Tk()
screen_W = root.winfo_screenwidth()
screen_H = root.winfo_screenheight()
preview_W = mdl_dims
preview_H = mdl_dims
preview_mid_X = int(screen_W/2 - preview_W/2)
preview_mid_Y = int(screen_H/2 - preview_H/2)

max_obj = 10
max_fps = 24
engine = edgetpu.detection.engine.DetectionEngine(args.model)

CAMW, CAMH = 320, 320
NBYTES = CAMW * CAMH * 3
npa = np.zeros((CAMH, CAMW, 4), dtype=np.uint8)
npa[:,:,3] = 255
new_pic = False

# Create a pool of image processors
done = False
lock = threading.Lock()
pool = []

class ImageProcessor(threading.Thread):
    def __init__(self):
        super(ImageProcessor, self).__init__()
        self.stream = io.BytesIO()
        self.event = threading.Event()
        self.terminated = False
        self.start()

    def run(self):
        # This method runs in a separate thread
        global done, npa, new_pic, CAMH, CAMW, NBYTES
        while not self.terminated:
            # Wait for an image to be written to the stream
            if self.event.wait(1):
                try:
                    if self.stream.tell() >= NBYTES:
                      self.stream.seek(0)
                      # python2 doesn't have the getbuffer() method
                      #bnp = np.fromstring(self.stream.read(NBYTES),
                      #              dtype=np.uint8).reshape(CAMH, CAMW, 3)
                      bnp = np.array(self.stream.getbuffer(),
                                    dtype=np.uint8).reshape(CAMH, CAMW, 3)
                      npa[:,:,0:3] = bnp
                      new_pic = True
                except Exception as e:
                  print(e)
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


def start_capture(): # has to be in yet another thread as blocking
  global CAMW, CAMH, pool
  with picamera.PiCamera() as camera:
    pool = [ImageProcessor() for i in range(3)]
    camera.resolution = (CAMW, CAMH)
    camera.framerate = 30
    camera.start_preview(fullscreen=False, layer=0, window=(0, 0, 320, 320))
    time.sleep(2)
    camera.capture_sequence(streams(), format='rgb', use_video_port=True)

t = threading.Thread(target=start_capture)
t.start()

while not new_pic:
    time.sleep(0.1)

########################################################################
DISPLAY = pi3d.Display.create(0, 0, w=preview_W, h=preview_H, layer=1, frames_per_second=max_fps)
DISPLAY.set_background(0.0, 0.0, 0.0, 0.0) # transparent
txtshader = pi3d.Shader("uv_flat")
linshader = pi3d.Shader('mat_flat')

# Fetch key presses
mykeys = pi3d.Keyboard()
mymouse = pi3d.Mouse(restrict=False)
mymouse.start()

#CAMERA = pi3d.Camera.instance()
CAMERA = pi3d.Camera(is_3d=False)

dist = [-4.0, -4.0, -4.0]
rot = 0.0
tilt = 0.0

while DISPLAY.loop_running():
  k = mykeys.read()
  if k >-1:
    if k==ord('w'):
      dist = [i + 0.02 for i in dist]
    if k==ord('s'):
      dist = [i - 0.02 for i in dist]
    elif k==27:
      mykeys.close()
      DISPLAY.destroy()
      break

# Shut down the processors in an orderly fashion
while pool:
  done = True
  with lock:
    processor = pool.pop()
  processor.terminated = True
  processor.join()
