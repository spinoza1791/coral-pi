"""Edge TPU Face detection with bounding boxes, labels and scores via Pygame stream - AUTHOR: Andrew Craton 03/2019"""

import argparse
import io
import time
import sys
import pygame
import pygame.camera
import pygame.freetype as freetype
import numpy as np
#import picamera
#import picamera.array
#from picamera.array import PiRGBArray
from PIL import Image
import edgetpu.detection.engine
import os

os.environ['SDL_VIDEO_CENTERED'] = '1'

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument(
	  '--model', help='File path of Tflite model.', required=True)
	parser.add_argument(
	  '--labels', help='File path of labels file.', required=False)
	parser.add_argument(
	  '--dims', help='Model input dimension', required=True)
	args = parser.parse_args()
	
	labels_on = False
	if args.labels:
		labels_on = True
		with open(args.labels, 'r') as f:
			pairs = (l.strip().split(maxsplit=1) for l in f.readlines())
			labels = dict((int(k), v) for k, v in pairs)
			

	#Set all input params equal to the input dimensions expected by the model
	mdl_dims = int(args.dims) #dims must be a factor of 32 for picamera resolution to work
	window_scale = 1

	#Set max num of objects you want to detect per frame
	max_obj = 2
	cam_res_x = 480
	cam_res_y = 480
	max_fps = 30
	engine = edgetpu.detection.engine.DetectionEngine(args.model)

	pygame.init()
	pygame.camera.init()
	#screen = pygame.display.set_mode((mdl_dims, mdl_dims), pygame.DOUBLEBUF|pygame.HWSURFACE)
	screen = pygame.display.set_mode((mdl_dims,mdl_dims), pygame.RESIZABLE)
	##pygame.display.set_caption('Face Detection')
	pycam = pygame.camera.Camera("/dev/video0",(cam_res_x,cam_res_y)) #, "RGB")
	pycam.start() 
	#screen.convert()
	clock = pygame.time.Clock()

	##camera = picamera.PiCamera()
	##camera.resolution = (mdl_dims, mdl_dims)
	##camera.framerate = max_fps

	pygame.font.init()
	fnt_sz = 18
	fnt = pygame.font.SysFont('Arial', fnt_sz)
	
	x1, x2, x3, x4, x5 = 0, 50, 50, 0, 0
	y1, y2, y3, y4, y5 = 50, 50, 0, 0, 50
	z = 5
	last_tm = time.time()
	i = 0
	results = None
	fps = "00.0 fps"
	N = 10

	##rgb = bytearray(camera.resolution[0] * camera.resolution[1] * 3)
	#rgb = bytearray(320 * 320 * 3)
	
	#rawCapture = PiRGBArray(camera, size=camera.resolution)
	#stream = camera.capture_continuous(rawCapture, format="rgb", use_video_port=True)
	while True:
	##	clock.tick(max_fps)
	#with picamera.array.PiRGBArray(camera, size=(mdl_dims, mdl_dims)) as stream: 
	#for foo in camera.capture_continuous(stream, use_video_port=True, format='rgb'):
	#for f in stream:
		#start_ms = time.time()
		#frame = io.BytesIO(f.array)
		#frame_buf_val = np.frombuffer(frame.getvalue(), dtype=np.uint8)
		#results = engine.DetectWithInputTensor(frame_buf_val, top_k=10)
		#rawCapture.truncate(0)
		#elapsed_ms = time.time() - start_ms

		##stream = io.BytesIO()
		##camera.capture(stream, use_video_port=True, format='rgb')
		##stream.seek(0)
		##stream.readinto(rgb)
		##frame_val = np.frombuffer(stream.getvalue(), dtype=np.uint8)
		##start_ms = time.time()
		##results = engine.DetectWithInputTensor(frame_val, top_k=max_obj)
		##elapsed_ms = time.time() - start_ms
		
		##img = pygame.image.frombuffer(rgb[0:
		##(camera.resolution[0] * camera.resolution[1] * 3)],
		##camera.resolution, 'RGB')

		img = pycam.get_image()
		img = pygame.transform.scale(img,(mdl_dims,mdl_dims))
		img_arr = pygame.surfarray.pixels3d(img)
		img_arr = np.swapaxes(img_arr,0,1)
		#img_arr = pygame.PixelArray.transpose(img_arr) #requires pygame.PixelArray object
		img_arr = np.ascontiguousarray(img_arr)
		start_ms = time.time()
		frame = io.BytesIO(img_arr)
		frame_buf_val = np.frombuffer(frame.getvalue(), dtype=np.uint8)
		print(frame_buf_val)
		results = engine.DetectWithInputTensor(frame_buf_val, top_k=max_obj)
		#frame.truncate(0)
		elapsed_ms = time.time() - start_ms

		screen = pygame.display.get_surface() #get the surface of the current active display
		resized_x,resized_y = size = screen.get_width(), screen.get_height()
		img = pygame.transform.scale(img,(resized_x, resized_y))
		if img:
			screen.blit(img, (0,0))
		#pygame.surfarray.blit_array(screen, img_arr)
	
		i += 1
		if i > N:
			tm = time.time()
			fps = "{:5.1f}FPS".format(i / (tm - last_tm))
			i = 0
			last_tm = tm

		fps_fnt = fnt.render(fps, True, (255,255,0))
		fps_width = fps_fnt.get_rect().width
		screen.blit(fps_fnt,((mdl_dims / 2 * (resized_x / mdl_dims)) - (fps_width / 2), 20))
		
		if results:
			num_obj = 0
			for obj in results:
				num_obj = num_obj + 1
			for obj in results:
				bbox = obj.bounding_box.flatten().tolist()
				if labels_on:
					label_id = int(round(obj.label_id,1))
					class_label = "%s" % (labels[label_id])
					fnt_class_label = fnt.render(class_label, True, (255,255,255))
					fnt_class_label_width = fnt_class_label.get_rect().width
					screen.blit(fnt_class_label,(x1, y1-fnt_sz))
				score = round(obj.score,2)
				x1 = round((bbox[0] * resized_x) / (bbox[0] * mdl_dims)) 
				y1 = round((bbox[1] * resized_y) / (bbox[1] * mdl_dims))
				x2 = round((bbox[2] * resized_x) / (bbox[2] * mdl_dims)) 
				y2 = round((bbox[3] * resized_y) / (bbox[3] * mdl_dims))
				rect_width = (x2 - x1) 
				rect_height = (y2 - y1) 
				#class_score = "%.2f" % (score)
				#fnt_class_score = fnt.render(class_score, True, (0,0,255))
				#fnt_class_score_width = fnt_class_score.get_rect().width
				#screen.blit(fnt_class_score,(x1, y1-fnt_sz))

				
				ms = "(%d) %s%.2fms" % (num_obj, "objects detected in ", elapsed_ms*1000)
				#camera.annotate_text = "%s %.2f\n%.2fms" % (
				#labels[results[0][0]], results[0][1], elapsed_ms*1000.0)

				fnt_ms = fnt.render(ms, True, (255,255,255))
				fnt_ms_width = fnt_ms.get_rect().width
				screen.blit(fnt_ms,((mdl_dims / 2) - (fnt_ms_width / 2), 0))
				bbox_rect = pygame.draw.rect(screen, (0,255,0), (x1, y1, rect_width, rect_height), 4)

		else:
			ms = "%s %.2fms" % ("No faces detected in", elapsed_ms*1000)
			fnt_ms = fnt.render(ms, True, (255,0,0))
			fnt_ms_width = fnt_ms.get_rect().width
			screen.blit(fnt_ms,((mdl_dims / 2) - (fnt_ms_width / 2), 0))

		for event in pygame.event.get():
			keys = pygame.key.get_pressed()
			if(keys[pygame.K_ESCAPE] == 1):
				pycam.stop()
				#pygame.quit()
				##camera.close()
				pygame.display.quit()
				sys.exit()
			elif event.type == pygame.VIDEORESIZE:
				screen = pygame.display.set_mode((event.w,event.h),pygame.RESIZABLE)
		
		#pygame.display.flip()
		pygame.display.update()
				

if __name__ == '__main__':
	main()