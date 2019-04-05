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
		self.rgbCapture = PiRGBArray(self.camera, size=self.camera.resolution * 3)
		#self.rgbCapture = bytearray(self.camera.resolution[0] * self.camera.resolution[1] * 3)
		self.camera.start_preview(fullscreen=False, layer=0, window=(0, 0, 320, 320))
		self.time.sleep(2.0)
		#self.stream = io.BytesIO()
		self.stream = self.camera.capture_continuous(self.rgbCapture,
			format="rgb", use_video_port=True)
		#self.picamera.array.PiRGBArray(camera) as self.stream
		#self.camera.capture(self.stream, use_video_port=True, format='rgb', resize=(320, 320))
		self.input = None
		self.stopped = False

	def start(self):
		Thread(target=self.update, args=()).start()
		return self

	def update(self):
		#self.camera.capture(stream, use_video_port=True, format='rgb', resize=(320, 320))
            	self.stream.seek(0)
            	self.stream.readinto(self.rgbCapture)
		self.stream.truncate()
		self.input = np.frombuffer(self.stream.getvalue(), dtype=np.uint8)
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
