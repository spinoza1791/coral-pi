"""Edge TPU Face detection with bounding boxes and scores via Picamera stream - AUTHOR: Andrew Craton 03/2019"""

import argparse
import io
import time
import pygame
import numpy as np
import picamera
import picamera.array
from PIL import Image
import edgetpu.detection.engine
import tkinter
import threading
import os

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
last_tm = time.time()
results = None

root = tkinter.Tk()
screen_W = root.winfo_screenwidth()
screen_H = root.winfo_screenheight()
preview_W = mdl_dims
preview_H = mdl_dims
preview_mid_X = int(screen_W/2 - preview_W/2)
preview_mid_Y = int(screen_H/2 - preview_H/2)

#engine = edgetpu.detection.engine.DetectionEngine(args.model)
os.environ['SDL_VIDEO_CENTERED'] = '1'

########################################################################

NBYTES = mdl_dims * mdl_dims * 3
new_pic = False

# Create a pool of image processors
done = False
lock = threading.Lock()
pool = []

class ImageProcessor(threading.Thread):
	def __init__(self):
		#global verts, linshader
		super(ImageProcessor, self).__init__()
		#self.engine = edgetpu.detection.engine.DetectionEngine(args.model)
		self.stream = io.BytesIO()
		self.event = threading.Event()
		self.terminated = False
		self.start()

	def run(self):
		# This method runs in a separate thread
		global done, new_pic, NBYTES, max_obj, results #, start_ms, elapsed_ms, 
		while not self.terminated:
			# Wait for an image to be written to the stream
			if self.event.wait(1):
				try:
					if self.stream.tell() >= NBYTES:
						#start_ms = time.time() 
						self.stream.seek(0)
						#bnp = np.array(self.stream.getbuffer(), dtype=np.uint8).reshape(mdl_dims * mdl_dims * 3)
						self.input_val = np.frombuffer(self.stream.getvalue(), dtype=np.uint8)
						#self.output = self.engine.DetectWithInputTensor(self.input_val, top_k=max_obj)
						results = self.input_val
						#elapsed_ms = time.time() - start_ms
						new_pic = True
				except Exception as e:
					print(e)
				finally:
					# Reset the stream and event
					self.stream.seek(0)
					self.stream.truncate()
					self.event.clear()
					# Return ourselves to the pool
					with lock:
					  pool.append(self)
						
def streams():
	while not done:
		with lock:
			if pool:
				processor = pool.pop()
			else:
				processor = None
		if processor:
			yield processor.stream
			processor.event.set()
		else:
			print("pool starved")
			# When the pool is starved, wait a while for it to refill
			time.sleep(0.1)

def start_capture(): # has to be in yet another thread as blocking
	global mdl_dims, pool, results, screen, start_ms, elapsed_ms, fnt_sz, preview_mid_X, preview_mid_Y, camera, rgb, max_obj
	x1, x2, x3, x4, x5 = 0, 50, 50, 0, 0
	y1, y2, y3, y4, y5 = 50, 50, 0, 0, 50
	z = 5
	pygame.init()
	pygame.display.set_caption('Face Detection')
	screen = pygame.display.set_mode((mdl_dims, mdl_dims), pygame.DOUBLEBUF|pygame.HWSURFACE)
	pygame.font.init()
	fnt_sz = 18
	myfont = pygame.font.SysFont('Arial', fnt_sz)
	x1, x2, x3, x4, x5 = 0, 50, 50, 0, 0
	y1, y2, y3, y4, y5 = 50, 50, 0, 0, 50
	z = 5
	last_tm = time.time()
	i = 0
	with picamera.PiCamera() as camera:
		pool = [ImageProcessor() for i in range(4)]
		camera.resolution = (mdl_dims, mdl_dims)
		rgb = bytearray(camera.resolution[0] * camera.resolution[1] * 3)
		camera.framerate = 24
		with picamera.array.PiRGBArray(camera, size=(mdl_dims, mdl_dims)) as stream:
			start_ms = time.time()
			camera.capture_sequence(streams(), format='rgb', use_video_port=True)
			elapsed_ms = time.time() - start_ms
			#Inference
			results = engine.DetectWithInputTensor(input, top_k=max_obj)
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
						ms = "(%d) %s%.2fms" % (num_obj, "faces detected in ", elapsed_ms*1000)
						fnt_class_score = myfont.render(class_score, True, (0,0,255))
						fnt_class_score_width = fnt_class_score.get_rect().width
						screen.blit(fnt_class_score,(x1, y1-fnt_sz))
						fnt_ms = myfont.render(ms, True, (255,255,255))
						fnt_ms_width = fnt_ms.get_rect().width
						screen.blit(fnt_ms,((mdl_dims / 2) - (fnt_ms_width / 2), 0))
						bbox_rect = pygame.draw.rect(screen, (0,0,255), (x1, y1, rect_width, rect_height), 2)
						#pygame.display.update(bbox_rect)
				else:
					elapsed_ms = time.time() - start_ms
					ms = "%s %.2fms" % ("No faces detected in", elapsed_ms*1000)
					fnt_ms = myfont.render(ms, True, (255,0,0))
					fnt_ms_width = fnt_ms.get_rect().width
					screen.blit(fnt_ms,((mdl_dims / 2) - (fnt_ms_width / 2), 0))
		pygame.display.update()

t = threading.Thread(target=start_capture)
t.start()

while not new_pic:
    time.sleep(0.1)

# Shut down the processors in an orderly fashion
while pool:
	done = True
	with lock:
		processor = pool.pop()
		processor.terminated = True
		processor.join()
		



#camera = picamera.PiCamera()
#Set camera resolution equal to model dims
#camera.resolution = (mdl_dims, mdl_dims)
#rgb = bytearray(camera.resolution[0] * camera.resolution[1] * 3)
#camera.framerate = 40
#_, width, height, channels = engine.get_input_tensor_shape()


#exitFlag = True
#while(exitFlag):
#	for event in pygame.event.get():
#		keys = pygame.key.get_pressed()
#		if(keys[pygame.K_ESCAPE] == 1):
#			pygame.display.quit()
#			camera.close()
#			exitFlag = False
    #with picamera.array.PiRGBArray(camera, size=(mdl_dims, mdl_dims)) as stream:        
        #stream = io.BytesIO()
        #start_ms = time.time()
        #camera.capture(stream, use_video_port=True, format='rgb')
        #elapsed_ms = time.time() - start_ms
        #stream.seek(0)
        #stream.readinto(rgb)
        #stream.truncate() #needed??

        #input = np.frombuffer(stream.getvalue(), dtype=np.uint8)
        #Inference
        #results = engine.DetectWithInputTensor(input, top_k=max_obj)
        #stream.close()                                                                 
 

    #pygame.display.update()

#pygame.display.quit()


