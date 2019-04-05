# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
from threading import Thread
import time
import io
import edgetpu.detection.engine
import numpy as np
 
class PiVideoStream:
	def __init__(self):
		self.camera = PiCamera()
		#self.rbgCapture = PiRGBArray(self.camera, size=(320, 320))
		self.rbgCapture = bytearray(320 * 320 * 3)
		#self.stream = self.camera.capture_continuous(self.rbgCapture,
		#	format="rgb", use_video_port=True)
		with self.picamera.array.PiRGBArray(camera, size=(mdl_dims, mdl_dims)) as self.stream:
			self.camera.capture(self.stream, use_video_port=True, format='rgb')
		self.modelpath = "/home/pi/python-tflite-source/edgetpu/test_data/mobilenet_ssd_v2_face_quant_postprocess_edgetpu.tflite"
		self.engine = self.edgetpu.detection.engine.DetectionEngine(self.modelpath)
		self.frame = None
		self.stopped = False

	def start(self):
		Thread(target=self.update, args=()).start()
		return self

	def update(self):
		self.stream.seek(0)
		self.stream.readinto(self.rbgCapture)
		self.input = np.frombuffer(self.stream.getvalue(), dtype=np.uint8)
		self.results = self.engine.DetectWithInputTensor(self.input, top_k=max_obj)
		if self.stopped:
			self.stream.close()
			self.rbgCapture.close()
			self.camera.close()
			return

	def read(self):
		# return the frame most recently read
		#return self.frame
		return self.results

	def stop(self):
		# indicate that the thread should be stopped
		self.stopped = True
