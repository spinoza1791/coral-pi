#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals
from picamera.array import PiRGBArray
import picamera
import time
import pi3d
import math
from pi3d.constants import GL_LINE_LOOP
import tkinter
import numpy as np
import argparse
import io
import edgetpu.detection.engine
#def main():
parser = argparse.ArgumentParser()
parser.add_argument(
  '--model', help='File path of Tflite model.', required=True)
parser.add_argument(
  '--dims', help='Model input dimension', required=True)
args = parser.parse_args()

#Set all input params equal to the input dimensions expected by the model
mdl_dims = int(args.dims) #dims must be a factor of 32 for picamera resolut$

#Set max num of objects you want to detect per frame
max_obj = 5
max_fps = 40
engine = edgetpu.detection.engine.DetectionEngine(args.model)

root = tkinter.Tk()
screen_W = root.winfo_screenwidth()
screen_H = root.winfo_screenheight()
preview_W = 320
preview_H = 320
preview_mid_X = int(screen_W/2 - preview_W/2)
preview_mid_Y = int(screen_H/2 - preview_H/2)

#Set fps as low as needed (<=60) to prevent CPU usage
DISPLAY = pi3d.Display.create(preview_mid_X, preview_mid_Y, w=preview_W, h=preview_H, layer=1, frames_per_second=max_fps)
DISPLAY.set_background(0.0, 0.0, 0.0, 0.0) # transparent
keybd = pi3d.Keyboard()
txtshader = pi3d.Shader("uv_flat")
linshader = pi3d.Shader('mat_flat')
CAMERA = pi3d.Camera(is_3d=False)
font = pi3d.Font("fonts/FreeMono.ttf", font_size=30, color=(0, 255, 0, 255)) # blue green 1.0 alpha
x1=x2=x3=x4=x5=y1=y2=y3=y4=y5=z= 1
bbox_vertices = [[x1,y1,z], [x2,y2,z], [x3,y3,z], [x4,y4,z]] 
#bbox = pi3d.Lines(vertices=[[x1,y1,z], [x2,y2,z], [x3,y3,z], [x4,y4,z]], line_width=4)
bbox = pi3d.Lines(vertices=bbox_vertices, material=(1.0,0.8,0.05), closed=True, line_width=4) 
bbox.set_shader(linshader)
#fps = "00.00FPS"
#N = 10
#fps_txt = pi3d.String(camera=CAMERA, is_3d=False, font=font, string=fps, x=0, y=preview_H/2 - 10, z=1.0)
#fps_txt.set_shader(txtshader)
elapsed_ms = 1/1000
ms = "00ms"
ms_txt = pi3d.String(camera=CAMERA, is_3d=False, font=font, string=ms, x=0, y=preview_H/2 - 30, z=1.0)
ms_txt.set_shader(txtshader)
bbox_time = pi3d.String(camera=CAMERA, is_3d=False, font=font, string=ms, x=0, y=preview_H/2 - 10, z=1.0)
bbox_time.set_shader(txtshader)   
#last_tm = time.time()
#i = 0
t_mat = [[1.0, 0.0, 0.0], # translation matrix
         [0.0, 1.0, 0.0],
         [0.0, 0.0, 1.0]]
r_mat = [[1.0, 0.0, 0.0], # rotation matrix
         [0.0, 1.0, 0.0],
         [0.0, 0.0, 1.0]]
s_mat = [[1.0, 0.0, 0.0], # scale matrix - all three start out as 'identity' matrices
         [0.0, 1.0, 0.0],
         [0.0, 0.0, 1.0]]

def bbox_calc(bbox_x1, bbox_y1, bbox_x2, bbox_y2, mdl_dims):
    #Left - X1
    x1=x4 = int(bbox_x1 - mdl_dims/2)
    #Right - X2
    x2=x3 = int(bbox_x2 - mdl_dims/2)
    #Upper - Y1
    y1=y2 = int(-bbox_y1 + mdl_dims/2)
    #Lower - Y2
    y3=y4 = int(-bbox_y2 + mdl_dims/2)
    z = 1
    bbox_vertices = [[x1,y1,z], [x2,y2,z], [x3,y3,z], [x4,y4,z]]
    return bbox_vertices

def mat_vec_mult(mat, vec):
  """ apply a matrix to a vector and return a modified vector
  """
  return [mat[0][0] * vec[0] + mat[0][1] * vec[1] + mat[0][2] * vec[2],
          mat[1][0] * vec[0] + mat[1][1] * vec[1] + mat[1][2] * vec[2],
          mat[2][0] * vec[0] + mat[2][1] * vec[1] + mat[2][2] * vec[2]]

def refresh_vertices(shape, old_verts):
  new_verts = []  # start off with a new list of vectors to keep the original ones 'clean'
  for v in old_verts:
    new_v = mat_vec_mult(s_mat, [v[0], v[1], 1.0]) # i.e. x, y, 1.0 to match 3x3 matrix
    new_v = mat_vec_mult(r_mat, new_v) # then multiply by rotation matrix
    new_v = mat_vec_mult(t_mat, new_v) # then by translation
    new_verts.append(new_v) # finally add this to the new list of vectors
    shape.set_2d_location(
  shape.re_init(vertices=new_verts) # finally update the vertex locations

with picamera.PiCamera() as camera:
    camera.resolution = (preview_W, preview_H)
    camera.framerate = max_fps
    rgb = PiRGBArray(camera, size=camera.resolution * 3)
    _, width, height, channels = engine.get_input_tensor_shape()
    camera.start_preview(fullscreen=False, layer=0, window=(preview_mid_X, preview_mid_Y, preview_W, preview_H))
    try:
        while DISPLAY.loop_running():
            stream = io.BytesIO()
            camera.capture(stream, use_video_port=True, format='rgb')
            stream.truncate()
            stream.seek(0)
            input = np.frombuffer(stream.getvalue(), dtype=np.uint8)
            stream.close()
            start_ms = time.time()
            results = engine.DetectWithInputTensor(input, top_k=max_obj)
            elapsed_ms = time.time() - start_ms
            ms = str(int(elapsed_ms*1000))+"ms"
            ms_txt.draw()
            ms_txt.quick_change(ms)                
            #fps_txt.draw()
            #i += 1
            #if i > N:
            #    tm = time.time()
            #    fps = "{:6.2f}FPS".format(i / (tm - last_tm))
            #    fps_txt.quick_change(fps)
            #    i = 0
            #    last_tm = tm
            if results:
                #start_ms = time.time()
                num_obj = 0
                for obj in results:
                    num_obj = num_obj + 1
                for obj in results:
                    bbox = obj.bounding_box.flatten().tolist()
                    score = round(obj.score,2)
                    bbox_x1 = round(bbox[0] * mdl_dims)
                    bbox_y1 = round(bbox[1] * mdl_dims)
                    bbox_x2 = round(bbox[2] * mdl_dims)
                    bbox_y2 = round(bbox[3] * mdl_dims)
                    bbox_vertices = bbox_calc(bbox_x1, bbox_y1, bbox_x2, bbox_y2, mdl_dims)
                    #bbox.re_init(vertices=bbox_vertices, material=(1.0,0.8,0.05), closed=True, line_width=4)
                    #bbox = pi3d.Lines(vertices=bbox_vertices, material=(1.0,0.8,0.05), closed=True, line_width=4)
                    refresh_vertices(bbox, bbox_vertices)
                    bbox.draw()
                    elapsed_ms = time.time() - start_ms
                    ms = str(int(elapsed_ms*1000))+"ms"
                    bbox_time.draw()
                    bbox_time.quick_change(ms) 

            if keybd.read() == 27:
                break
    finally:
        keybd.close()
        DISPLAY.destroy()
        camera.close()

#if __name__ == '__main__':
 #   main()





