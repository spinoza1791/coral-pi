"""Face detection with bounding boxes and scores via Raspberry Pi camera stream."""
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
      '--label', help='File path of label file.', required=False)
    args = parser.parse_args()
   
    #set all input params equal to the input dimensions expected by the model
    mdl_dims = 320 #since face model is 320x320

    engine = edgetpu.detection.engine.DetectionEngine(args.model)
    pygame.init()
    screen = pygame.display.set_mode((mdl_dims, mdl_dims), pygame.DOUBLEBUF|pygame.HWSURFACE)
    pygame.font.init()
    myfont = pygame.font.SysFont('Comic Sans MS', 20)
    ms_x = (mdl_dims/2 - 15)
    ms_y = 10
    camera = picamera.PiCamera()
    camera.resolution = (mdl_dims, mdl_dims)
    rgb = bytearray(camera.resolution[0] * camera.resolution[1] * 3)
    camera.framerate = 40
    _, width, height, channels = engine.get_input_tensor_shape()

    exitFlag = True
    while(exitFlag):
        for event in pygame.event.get():
             if(event.type is pygame.MOUSEBUTTONDOWN or 
                event.type is pygame.QUIT):
                 exitFlag = False

        stream = io.BytesIO()
        camera.capture(stream, use_video_port=True, format='rgb')
        stream.seek(0)
        stream.readinto(rgb)
        input = np.frombuffer(stream.getvalue(), dtype=np.uint8)
        start_ms = time.time()
        #Set top_k = number of objects you want to detect at a time
        results = engine.DetectWithInputTensor(input, top_k=10)
        elapsed_ms = time.time() - start_ms
        stream.close()
        img = pygame.image.frombuffer(rgb[0:
        (camera.resolution[0] * camera.resolution[1] * 3)],
        camera.resolution, 'RGB')
        screen.fill(0)
        if img:
             screen.blit(img, (0,0))
             if results:
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
                       fnt_class_score = myfont.render(class_score, False, (255,255,255))
                       screen.blit(fnt_class_score,(x1, y1-15))
                       ms = "%s%.2fms" % ("face ", elapsed_ms*1000) 
                       fnt_ms = myfont.render(ms, False, (255,255,255)) 
                       screen.blit(fnt_ms,(ms_x, ms_y))
                       pygame.draw.rect(screen, (0,0,255), (x1, y1, rect_width, rect_height), 2)

        pygame.display.update()

    pygame.display.quit()
 
if __name__ == '__main__':
    main()
