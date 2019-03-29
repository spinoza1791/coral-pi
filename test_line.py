from __future__ import absolute_import, division, print_function, unicode_literals
import pi3d
import math
import numpy as np
from picamera.array import PiRGBArray
import picamera
import time
from pi3d.constants import GL_LINE_LOOP
import tkinter
import argparse
import io
import edgetpu.detection.engine

root = tkinter.Tk()
screen_W = root.winfo_screenwidth()
screen_H = root.winfo_screenheight()
preview_W = 320
preview_H = 320
preview_mid_X = int(screen_W/2 - preview_W/2)
preview_mid_Y = int(screen_H/2 - preview_H/2)


traject_list = np.array([[i*0.1, i*0.1, i*0.1] for i in range(1000)])
#traject_list = np.array([1000], [3])

print("traject_list shape =", traject_list.shape)

#DISPLAY = pi3d.Display.create(x=50, y=50)
DISPLAY = pi3d.Display.create(preview_mid_X, preview_mid_Y, w=preview_W, h=preview_H, layer=1, frames_per_second=30, samples=4)
DISPLAY.set_background(0.0, 0.0, 0.0, 0.0) # transparent

keybd = pi3d.Keyboard()
tracksh = pi3d.Shader("mat_flat")
track = pi3d.Lines(vertices=traject_list, material=(1.0,0.0,1.0), z=5.0, line_width=4) #, closed=True)
track.set_shader(tracksh)

j = 0.0
while DISPLAY.loop_running():
    track.draw()
    #traject_list[:20,:] = np.array([[i**2 * 0.001212, 2 - (i+j)*0.15, i*0.1] for i in range(20)])
    traject_list[20,:] = np.array([50, 0, 0])
    #traject_list[19,:] = np.array([50, 50, 0])
    #traject_list[20:,:] = traject_list[19,:]
    #print("traject_list mod shape =", traject_list.shape)
    #j += 0.01
    track.buf[0].re_init(traject_list)
    # at the moment can't re init until *after* the init done on first draw()
    if keybd.read() == 27:
        break

keybd.close()
DISPLAY.destroy
