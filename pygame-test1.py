import sys, pygame
import os
import RPi.GPIO as GPIO

from picamera.array import PiRGBArray
from picamera import PiCamera
import cv2
import time
import numpy as np

size = width, height = 320, 320
pygame.init()
screen = pygame.display.set_mode(size)

camera=PiCamera()
camera.resolution=(320,320)
camera.rotation=180
camera.framerate=15
rawCapture=PiRGBArray(camera,size=(320,320))

def stuff_monitor(time_to_detect):
    
    colorLB=(30,100,50)
    colorUB=(70,255,255)    #Set the color range in HSV color mode

    start_time=pygame.time.get_ticks()

    for frame in camera.capture_continuous(rawCapture, format = "bgr", use_video_port = True ):
        if pygame.key.get_pressed()[pygame.K_q]==True:
            menu=1
            stop_flag =1
            cv2.waitKey(1)
            rawCapture.truncate(0)
            cv2.destroyAllWindows()
            break
                    
        image = frame.array
        imageRaw = image.copy()
        pygame.event.pump()
        current_time=pygame.time.get_ticks()

        if current_time-start_time>time_to_detect and time_to_detect!=0:
            cv2.imshow("overlay",image)
            cv2.waitKey(100)
            rawCapture.truncate(0)
            break

        cv2.waitKey(1)
        rawCapture.truncate(0)

while True:
    Clock.tick(tick_val)
    screen.fill(black)
    pygame.display.flip()
