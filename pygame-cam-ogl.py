
import sys
import pygame
import pygame.camera
import os

os.environ['SDL_VIDEO_CENTERED'] = '1'

pygame.init()
pygame.camera.init()

screen = pygame.display.set_mode((640,480),0)
cam_list = pygame.camera.list_cameras()
cam = pygame.camera.Camera(cam_list[0],(32,24))
cam.start()

#screen = pygame.camera.Camera("/dev/video0",(640,480))
#cam.start()

while True:
   image1 = screen.get_image()
   image1 = pygame.transform.scale(image1,(640,480))
   screen.blit(image1,(0,0))
   pygame.display.update()
   exitFlag = True
   while(exitFlag):
     for event in pygame.event.get():
         keys = pygame.key.get_pressed()
         if(keys[pygame.K_ESCAPE] == 1):
             exitFlag = False   
