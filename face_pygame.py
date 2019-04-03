"""Edge TPU Face detection with bounding boxes and scores via Picamera stream - AUTHOR: Andrew Craton 03/2019"""

import argparse
import io
import time
import pygame
import numpy as np
import picamera
from PIL import Image
import edgetpu.detection.engine

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
      '--model', help='File path of Tflite model.', required=True)
    parser.add_argument(
      '--dims', help='Model input dimension', required=True)
    args = parser.parse_args()

    #Set all input params equal to the input dimensions expected by the model
    mdl_dims = int(args.dims) #dims must be a factor of 32 for picamera resolution to work

    #Set max num of objects you want to detect per frame
    max_obj = 20
    engine = edgetpu.detection.engine.DetectionEngine(args.model)
    pygame.init()
    pygame.display.set_caption('Face Detection')
    screen = pygame.display.set_mode((mdl_dims, mdl_dims), pygame.DOUBLEBUF|pygame.HWSURFACE)
    pygame.font.init()
    fnt_sz = 18
    myfont = pygame.font.SysFont('Arial', fnt_sz)

    camera = picamera.PiCamera()
    #Set camera resolution equal to model dims
    camera.resolution = (mdl_dims, mdl_dims)
    rgb = bytearray(camera.resolution[0] * camera.resolution[1] * 3)
    camera.framerate = 30
    _, width, height, channels = engine.get_input_tensor_shape()

    x1, x2, x3, x4, x5 = 0, 50, 50, 0, 0
    y1, y2, y3, y4, y5 = 50, 50, 0, 0, 50
    z = 5
    last_tm = time.time()
    i = 0

    exitFlag = True
    while(exitFlag):
        for event in pygame.event.get():
             #Quit all if mouse btn pushed
             if(event.type is pygame.MOUSEBUTTONDOWN or 
                event.type is pygame.QUIT):
                 exitFlag = False

        stream = io.BytesIO()
        start_ms = time.time()
        camera.capture(stream, use_video_port=True, format='rgb')
        elapsed_ms = time.time() - start_ms
        stream.seek(0)
        stream.readinto(rgb)
        input = np.frombuffer(stream.getvalue(), dtype=np.uint8)
        #Inference
        results = engine.DetectWithInputTensor(input, top_k=max_obj)
        stream.close()
        img = pygame.image.frombuffer(rgb[0:
        (camera.resolution[0] * camera.resolution[1] * 3)],
        camera.resolution, 'RGB')

        if img:
             screen.blit(img, (0,0))
             if results:
                  num_obj = 0
                  for obj in results:
                       num_obj = num_obj + 1
                  for obj in results:
                       bbox = obj.bounding_box.flatten().tolist()
                       score = round(obj.score,2)
                       x1 = round(bbox[0] * mdl_dims)
                       y1 = round(bbox[1] * mdl_dims)
                       x2 = round(bbox[2] * mdl_dims)
                       y2 = round(bbox[3] * mdl_dims)
                       rect_width = x2 - x1
                       rect_height = y2 - y1
                       class_score = "%.2f" % (score)
                       fnt_class_score = myfont.render(class_score, True, (0,0,255))
                       fnt_class_score_width = fnt_class_score.get_rect().width
                       screen.blit(fnt_class_score,(x1, y1-fnt_sz))
                       ms = "(%d) %s%.2fms" % (num_obj, "faces detected in ", elapsed_ms*1000)
                       fnt_ms = myfont.render(ms, True, (255,255,255))
                       fnt_ms_width = fnt_ms.get_rect().width
                       screen.blit(fnt_ms,((mdl_dims / 2) - (fnt_ms_width / 2), 0))
                       pygame.draw.rect(screen, (0,0,255), (x1, y1, rect_width, rect_height), 2)
             else:
                  ms = "%s %.2fms" % ("No faces detected in", elapsed_ms*1000)
                  fnt_ms = myfont.render(ms, True, (255,0,0))
                  fnt_ms_width = fnt_ms.get_rect().width
                  screen.blit(fnt_ms,((mdl_dims / 2) - (fnt_ms_width / 2), 0))

        pygame.display.update()

    pygame.display.quit()

if __name__ == '__main__':
    main()
