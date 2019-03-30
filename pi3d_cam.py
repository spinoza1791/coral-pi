#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals
from picamera.array import PiRGBArray
import picamera
import time
import pi3d
from pi3d.constants import GL_LINE_LOOP
import tkinter
import numpy as np
import argparse
import io
import edgetpu.detection.engine

def bbox_calc(bbox_x1, bbox_y1, bbox_x2, bbox_y2, mdl_dims):
    #Left - X1
    x1=x4=x5= int(bbox_x1 - mdl_dims/2)
    #Right - X2
    x2=x3 = int(bbox_x2 - mdl_dims/2)
    #Upper - Y1
    y1=y2=y5 = int(-bbox_y1 + mdl_dims/2)
    #Lower - Y2
    y3=y4 = int(-bbox_y2 + mdl_dims/2)
    z = 1
    bbox_vertices = [[x1,y1,z], [x2,y2,z], [x3,y3,z], [x4,y4,z]] #, [x5,y5,z]]
    #return x1, x2, x3, x4, x5, y1, y2, y3, y4, y5
    return bbox_vertices

def main():
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
    engine = edgetpu.detection.engine.DetectionEngine(args.model)

    root = tkinter.Tk()
    screen_W = root.winfo_screenwidth()
    screen_H = root.winfo_screenheight()
    preview_W = 320
    preview_H = 320
    preview_mid_X = int(screen_W/2 - preview_W/2)
    preview_mid_Y = int(screen_H/2 - preview_H/2)

    #Set fps as low as needed (<=60) to prevent CPU usage
    DISPLAY = pi3d.Display.create(preview_mid_X, preview_mid_Y, w=preview_W, h=preview_H, layer=1, frames_per_second=60)
    DISPLAY.set_background(0.0, 0.0, 0.0, 0.0) # transparent
    keybd = pi3d.Keyboard()
    txtshader = pi3d.Shader("uv_flat")
    linshader = pi3d.Shader('mat_flat')
    CAMERA = pi3d.Camera(is_3d=False)
    font = pi3d.Font("fonts/FreeMono.ttf", font_size=30, color=(0, 255, 0, 255)) # blue green 1.0 alpha
    x1=x2=x3=x4=x5=y1=y2=y3=y4=y5=z= 1
    bbox_vertices = [[x1,y1,z], [x2,y2,z], [x3,y3,z], [x4,y4,z]] #, [x5,y5,z]]
    #bbox = pi3d.Lines(vertices=[[x1,y1,z], [x2,y2,z], [x3,y3,z], [x4,y4,z], [x5,y5,z]], line_width=4)
    bbox = pi3d.Lines(vertices=bbox_vertices, material=(1.0,0.8,0.05), closed=True, line_width=4) 
    bbox.set_shader(linshader)
    fps = "00.00FPS"
    N = 100
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
        camera.framerate = 40
        #rgb = bytearray(camera.resolution[0] * camera.resolution[1] * 3)
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
                #Inference magic happens here
                results = engine.DetectWithInputTensor(input, top_k=max_obj)
                elapsed_ms = time.time() - start_ms
                ms = str(int(elapsed_ms*1000))+"ms"
                #if DISPLAY.loop_running():
                start_all_ms = time.time()
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
                        bbox = obj.bounding_box.flatten().tolist()
                        score = round(obj.score,2)
                        bbox_x1 = round(bbox[0] * mdl_dims)
                        bbox_y1 = round(bbox[1] * mdl_dims)
                        bbox_x2 = round(bbox[2] * mdl_dims)
                        bbox_y2 = round(bbox[3] * mdl_dims)
                        #x1, x2, x3, x4, x5, y1, y2, y3, y4, y5 = bbox_calc(bbox_x1, bbox_y1, bbox_x2, bbox_y2, mdl_dims)
                        bbox_vertices = bbox_calc(bbox_x1, bbox_y1, bbox_x2, bbox_y2, mdl_dims)
                        #bbox.re_init(vertices=bbox_vertices, material=(1.0,0.8,0.05), closed=True, line_width=4)
                        #bbox = pi3d.Lines(vertices=[[x1,y1,z], [x2,y2,z], [x3,y3,z], [x4,y4,z], [x5,y5,z]], line_width=3)
                        bbox = pi3d.Lines(vertices=bbox_vertices, material=(1.0,0.8,0.05), closed=True, line_width=4)
                        bbox.draw()
                        
                if keybd.read() == 27:
                    break
        finally:
            keybd.close()
            DISPLAY.destroy()
            camera.close()

if __name__ == '__main__':
    main()





