# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
from threading import Thread
import time
import io
#import edgetpu.detection.engine
import numpy as np
 
class PiVideoStream:
	def __init__(self):
		self.camera = PiCamera()
		self.camera.resolution = (320, 320)
		self.camera.framerate = 24
		self.rawCapture = PiRGBArray(self.camera, size=(320, 320))
		self.camera.start_preview(fullscreen=False, layer=0, window=(0, 0, 320, 320))
		time.sleep(2) #camera warm-up
		self.stream = self.camera.capture_continuous(self.rawCapture, format="bgr", use_video_port=True)
		#self.rgbCapture = bytearray(self.camera.resolution[0] * self.camera.resolution[1] * 3)

		self.frame = None
		self.stopped = False

	def start(self):
		Thread(target=self.update, args=()).start()
		return self

	def update(self):
		#self.stream = io.BytesIO()
		#self.camera.capture(self.stream, use_video_port=True, format='rgb')
		#self.stream.truncate()
		#self.stream.seek(0)
		#self.stream.readinto(self.rgbCapture)
		for f in self.stream:
			self.frame = io.BytesIO(f.array)
			self.input = np.frombuffer(self.frame.getvalue(), dtype=np.uint8)
			#self.rawCapture.truncate(0)
		#self.input = np.frombuffer(self.stream.getvalue(), dtype=np.uint8)
		#self.stream.close()
		if self.stopped:
			self.stream.close()
			self.rbgCapture.close()
			self.camera.close()
			return

	def read(self):
		return self.input

	def stop(self):
		# indicate that the thread should be stopped
		self.stopped = True
