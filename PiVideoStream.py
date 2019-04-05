# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
from threading import Thread
import time
import io
 
class PiVideoStream:
	def __init__(self):
		self.camera = PiCamera()
		#self.rbgCapture = PiRGBArray(self.camera, size=(320, 320))
		self.rbgCapture = bytearray(320 * 320 * 3)
		#self.stream = self.camera.capture_continuous(self.rbgCapture,
		#	format="rgb", use_video_port=True)
		with self.picamera.array.PiRGBArray(camera, size=(mdl_dims, mdl_dims)) as stream:
			self.stream = self.camera.capture(self.rbgCapture, use_video_port=True, format='rgb')
		self.frame = None
		self.stopped = False

	def start(self):
		Thread(target=self.update, args=()).start()
		return self

	def update(self):
		# keep looping infinitely until the thread is stopped
		for f in self.stream:
			# grab the frame from the stream and clear the stream in
			# preparation for the next frame
			self.frame = f.array
			#self.frame.seek(0)
			self.frame.readinto(self.rbgCapture)
			#self.rbgCapture.truncate(0)
			# if the thread indicator variable is set, stop the thread
			# and resource camera resources
			if self.stopped:
				self.stream.close()
				self.rbgCapture.close()
				self.camera.close()
				return

	def read(self):
		# return the frame most recently read
		#return self.frame
		return self.rbgCapture

	def stop(self):
		# indicate that the thread should be stopped
		self.stopped = True
