import demo
import pi3d
import math
import numpy as np


traject_list = np.array([[i*0.1, i*0.1, i*0.1] for i in range(1000)])

DISPLAY = pi3d.Display.create(x=50, y=50)

tracksh = pi3d.Shader("mat_flat")
track = pi3d.Lines(vertices=traject_list, material=(1.0,0.0,1.0), z=5.0, line_width=4)
track.set_shader(tracksh)
j = 0.0
while DISPLAY.loop_running():
    track.draw()
    traject_list[:20,:] = np.array([[i**2 * 0.001212, 2 - (i+j)*0.15, i*0.1] for i in range(20)])
    traject_list[20:,:] = traject_list[19,:]
    j += 0.01
    track.buf[0].re_init(traject_list)
    # at the moment can't re init until *after* the init done on first draw()
