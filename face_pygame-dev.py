"""Edge TPU Face detection with bounding boxes and scores via Picamera stream - AUTHOR: Andrew Craton 03/2019"""

import argparse
import io
import time
import sys
import pygame
import pygame.camera
import numpy as np
import picamera
import picamera.array
from picamera.array import PiRGBArray
from PIL import Image
import edgetpu.detection.engine
import os

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
	max_obj = 10
	max_fps = 30
	engine = edgetpu.detection.engine.DetectionEngine(args.model)

	pygame.init()
	clock = pygame.time.Clock()
	pygame.display.set_caption('Face Detection')
	screen = pygame.display.set_mode((mdl_dims, mdl_dims), pygame.DOUBLEBUF|pygame.HWSURFACE)

	camera = picamera.PiCamera()
	camera.resolution = (mdl_dims, mdl_dims)
	camera.framerate = max_fps

	pygame.font.init()
	fnt_sz = 18
	myfont = pygame.font.SysFont('Arial', fnt_sz)
	x1, x2, x3, x4, x5 = 0, 50, 50, 0, 0
	y1, y2, y3, y4, y5 = 50, 50, 0, 0, 50
	z = 5
	last_tm = time.time()
	i = 0
	results = None
	fps = "00.0 fps"
	N = 10

	rgb = bytearray(camera.resolution[0] * camera.resolution[1] * 3)
	#rawCapture = PiRGBArray(camera, size=camera.resolution)
	#stream = camera.capture_continuous(rawCapture, format="rgb", use_video_port=True)
	while True:
		clock.tick(max_fps)
	#with picamera.array.PiRGBArray(camera, size=(mdl_dims, mdl_dims)) as stream: 
	#for foo in camera.capture_continuous(stream, use_video_port=True, format='rgb'):
	#for f in stream:

		#frame = io.BytesIO(f.array)
		#frame_buf_val = np.frombuffer(frame.getvalue(), dtype=np.uint8)
		#results = engine.DetectWithInputTensor(frame_buf_val, top_k=10)
		#rawCapture.truncate(0)

		stream = io.BytesIO()
		camera.capture(stream, use_video_port=True, format='rgb')
		stream.seek(0)
		stream.readinto(rgb)
		frame_val = np.frombuffer(stream.getvalue(), dtype=np.uint8)
		start_ms = time.time()
		results = engine.DetectWithInputTensor(frame_val, top_k=max_obj)
		elapsed_ms = time.time() - start_ms
		
		img = pygame.image.frombuffer(rgb[0:
		(camera.resolution[0] * camera.resolution[1] * 3)],
		camera.resolution, 'RGB')

		#stream.close()#
		#img = cam.get_image()
		#img = pygame.transform.scale(img,(320,320))
		#img_arr = pygame.surfarray.array3d(img)
		#screen.blit(img, (0,0))
		
		i += 1
		if i > N:
			tm = time.time()
			fps = "{:5.1f}FPS".format(i / (tm - last_tm))
			fps_fnt = myfont.render(fps, True, (255,255,255))
			fps_width = fps_fnt.get_rect().width
			screen.blit(fps_fnt,((mdl_dims / 2) - (fps_width / 2), 20))
			i = 0
			last_tm = tm

		if img:
			screen.blit(img, (0,0))
		elapsed_ms = time.time() - start_ms
		#if img:
			#screen.blit(img, (0,0))
			#pygame.display.update()
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
				ms = "(%d) %s%.2fms" % (num_obj, "faces detected in ", elapsed_ms*1000)
				fnt_class_score = myfont.render(class_score, True, (0,0,255))
				fnt_class_score_width = fnt_class_score.get_rect().width
				screen.blit(fnt_class_score,(x1, y1-fnt_sz))
				fnt_ms = myfont.render(ms, True, (255,255,255))
				fnt_ms_width = fnt_ms.get_rect().width
				screen.blit(fnt_ms,((mdl_dims / 2) - (fnt_ms_width / 2), 0))
				bbox_rect = pygame.draw.rect(screen, (0,255,0), (x1, y1, rect_width, rect_height), 4)
				#pygame.display.update(bbox_rect)
		else:
			ms = "%s %.2fms" % ("No faces detected in", elapsed_ms*1000)
			fnt_ms = myfont.render(ms, True, (255,0,0))
			fnt_ms_width = fnt_ms.get_rect().width
			screen.blit(fnt_ms,((mdl_dims / 2) - (fnt_ms_width / 2), 0))

		for event in pygame.event.get():
			keys = pygame.key.get_pressed()
			if(keys[pygame.K_ESCAPE] == 1):
				#cam.stop()
				#pygame.quit()
				camera.close()
				pygame.display.quit()
				sys.exit()

		pygame.display.update()
				

if __name__ == '__main__':
	main()