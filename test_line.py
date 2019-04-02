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

#traject_list = np.array([[i*0.1, i*0.1, i*0.1] for i in range(1000)])
line_1 = np.arange(90, dtype = 'float64').reshape((30,3))
line_2 = np.arange(90, dtype = 'float64').reshape((30,3))
line_3 = np.arange(90, dtype = 'float64').reshape((30,3))
#line_4 = np.arange(60, dtype = 'float64').reshape((20,3))

#print("traject_list shape =", traject_list.shape)
#print("traject_list dims =", traject_list.ndim)
#print("traject_list size =", traject_list.size)
#print("traject_list dtype =", traject_list.dtype)

#DISPLAY = pi3d.Display.create(x=50, y=50)
DISPLAY = pi3d.Display.create(preview_mid_X, preview_mid_Y, w=preview_W, h=preview_H, layer=1, frames_per_second=30, samples=4)
DISPLAY.set_background(0.0, 0.0, 0.0, 0.0) # transparent

keybd = pi3d.Keyboard()
tracksh = pi3d.Shader("mat_flat")
#vertices_lines = (line_1, line_4)

#track_1 = pi3d.Lines(vertices=[(line_1),(line_4)], material=(1.0,0.0,1.0), z=1.0, line_width=4) #, closed=
track_1 = pi3d.Lines(vertices=line_1, material=(1.0,0.0,1.0), z=1.0, line_width=4)
track_2 = pi3d.Lines(vertices=line_2, material=(1.0,0.2,1.0), z=1.0, line_width=4)
track_3 = pi3d.Lines(vertices=line_3, material=(1.0,0.4,1.0), z=1.0, line_width=4)
#track_4 = pi3d.Lines(vertices=line_4, material=(1.0,0.6,1.0), z=1.0, line_width=4) # , closed=True)

track_1.set_shader(tracksh)
track_2.set_shader(tracksh)
track_3.set_shader(tracksh)
#track_4.set_shader(tracksh)

#j = 0.0
while DISPLAY.loop_running():
    #traject_list[:20,:] = np.array([[i**2 * 0.801212, 2 - (i+j)*0.15, i*0.1] for i in range(20)])
    line_1[:90,:] = np.array([[i*-300, i*0, i*20] for i in range(30)])
    # z = size, x = starting x
    line_2[:90,:] = np.array([[i*0, i*300, i*20] for i in range(30)])
    line_3[:90,:] = np.array([[i*300, i*0, i*20] for i in range(30)])
    #line_4[:50,:] = np.array([[i*10, i*0, i*0] for i in range(20)])
    track_1.buf[0].re_init(line_1)
    track_2.buf[0].re_init(line_2)
    track_3.buf[0].re_init(line_3)
    #track_4.buf[0].re_init(line_4)
    #time.sleep(0.5)
    track_1.draw()
    track_2.draw()
    track_3.draw()
    #track_4.draw()
    #traject_list[21:40,:] = np.array([[i*10, i*100, i*30] for i in range(21, 40)])
    #traject_list[:20,:] = 40, 200, 200 
    #j += 0.01
    #track.buf[0].re_init(traject_list)
    #time.sleep(0.5)
    # at the moment can't re init until *after* the init done on first draw()
    if keybd.read() == 27:
        break

keybd.close()
DISPLAY.destroy
