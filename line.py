#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals

#import demo
import pi3d
import random
    
DISPLAY = pi3d.Display.create(x=50, y=50)
CAMERA = pi3d.Camera()

#shape = pi3d.Sphere(z=5.0) # try other shapes: Sphere, Torus, Cylinder, Helix etc
#shape = pi3d.Lines(z=2.0, vertices=[(i * 0.01, 0.5, 0.5) for i in range(50)], closed=True)
shape = pi3d.Plane(z=5.0)
x, y, z = shape.position(x, y ,z)

""" The light shader works fine for "solid" objects, i.e. for drawing
triangles, but isn't what you want generally for lines and points. Try
swapping the shaders over below.

Also see what the effect is of using a texture mapping shader such as uv_flat
which will need the alternative tex and set_draw_details lines to be
activated.

The "strip" argument to Shape.set_line_width() determines whether GL_LINES
or GL_LINE_STRIP will be used. Try swapping it to True. Try the same when
shape is a pi3d.Cuboid or pi3d.Sprite. The "closed" argument will use
GL_LINE_LOOP and add a final leg returning to the start.
"""
shader = pi3d.Shader('mat_light')
#shader = pi3d.Shader('mat_flat')
#shader = pi3d.Shader('uv_flat') #NB this will need the texture lines below to be uncommented

shape.set_shader(shader)
shape.set_material((1.0, 0.7, 0.1))
#tex = pi3d.Texture('techy2.png')
#shape.set_draw_details(shader, [tex])

""" An alternative use of lines is provided by the pi3d.Lines class.
Try swapping the line above that creates the shape object (8 for 9).
"""

mykeys = pi3d.Keyboard()
i=0
while DISPLAY.loop_running():
  shape.draw()
  shape.position(x+i, y, z)
  if i < 100:
    i = i + 1
  else:
    i = 0
  #shape.rotateIncY(0.21)
  #shape.rotateIncX(0.1)

  key = mykeys.read()
  if key==27:
    mykeys.close()
    DISPLAY.destroy()
    break
  elif key == ord('p'): # swap to points
    shape.set_point_size(40)
  elif key == ord('l'): # swap to lines
    shape.set_line_width(4, strip=False, closed=False)
  elif key == ord('t'): # swap to triangles
    shape.set_line_width(0)

mykeys.close()
DISPLAY.destroy()
