# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
from threading import Thread
 
class PiVideoStream:
	def __init__(self):
		# initialize the camera and stream
		self.camera = PiCamera()
	        self.camera.resolution = (320, 320)
		self.camera.framerate = 32
		self.rbgCapture = PiRGBArray(self.camera, size=(320, 320))
		#self.stream = self.camera.capture_continuous(self.rbgCapture,
		#	format="rgb", use_video_port=True)
		self.stream = self.camera.capture(self.rbgCapture, use_video_port=True, format='rgb')
 
		# initialize the frame and the variable used to indicate
		# if the thread should be stopped
		self.frame = None
		self.stopped = False

	def start(self):
		# start the thread to read frames from the video stream

		Thread(target=self.update, args=()).start()
		return self
 
	def update(self):
		# keep looping infinitely until the thread is stopped
		for f in self.stream:
			# grab the frame from the stream and clear the stream in
			# preparation for the next frame
			self.frame = f.array
			self.rbgCapture.truncate(0)
 
			# if the thread indicator variable is set, stop the thread
			# and resource camera resources
			if self.stopped:
				self.stream.close()
				self.rbgCapture.close()
				self.camera.close()
				return
	def read(self):
		# return the frame most recently read
		return self.frame
 
	def stop(self):
		# indicate that the thread should be stopped
		self.stopped = True
