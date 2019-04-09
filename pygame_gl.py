import argparse
import io
import time
import numpy as np
import picamera
import picamera.array
from PIL import Image
import edgetpu.detection.engine
import pygame
from pygame.locals import *
import os

from OpenGL.GL import *
from OpenGL.GLU import *

os.environ['SDL_VIDEO_CENTERED'] = '1'

verticies = (
    (1, -1, -1),
    (1, 1, -1),
    (-1, 1, -1),
    (-1, -1, -1),
    (1, -1, 1),
    (1, 1, 1),
    (-1, -1, 1),
    (-1, 1, 1)
    )

edges = (
    (0,1),
    (0,3),
    (0,4),
    (2,1),
    (2,3),
    (2,7),
    (6,3),
    (6,4),
    (6,7),
    (5,1),
    (5,4),
    (5,7)
    )


def Cube():
    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glVertex3fv(verticies[vertex])
    glEnd()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
    '--model', help='File path of Tflite model.', required=False)
    parser.add_argument(
    '--dims', help='Model input dimension', required=False)
    args = parser.parse_args()
    mdl_dims = int(args.dims)
    
    pygame.init()
    #display = (800,600)
    #pygame.display.set_mode(display, DOUBLEBUF|OPENGL)
    display = pygame.display.set_mode((mdl_dims, mdl_dims), DOUBLEBUF|OPENGLBLIT)
    camera = picamera.PiCamera()
    camera.resolution = (mdl_dims, mdl_dims)
    rgb = bytearray(camera.resolution[0] * camera.resolution[1] * 3)
    
    #gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)
    #glTranslatef(0.0,0.0, -5)
          
    exitFlag = True
    while(exitFlag):
        for event in pygame.event.get():
            keys = pygame.key.get_pressed()
            if(keys[pygame.K_ESCAPE] == 1):
                exitFlag = False         
        img = pygame.image.frombuffer(rgb[0:
        (camera.resolution[0] * camera.resolution[1] * 3)],
        camera.resolution, 'RGB')
        if img:
            display.blit(img, (0,0))
        glRotatef(1, 3, 1, 1)
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        Cube()
        pygame.display.flip()
        pygame.time.wait(10)


main()
