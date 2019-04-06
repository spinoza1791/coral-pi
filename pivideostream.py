from picamera.array import PiRGBArray
from picamera import PiCamera
from threading import Thread
import time
import io
import edgetpu.detection.engine
import numpy as np
import pi3d
 
class PiVideoStream:
	def __init__(self):
		self.model_path = "/home/pi/python-tflite-source/edgetpu/test_data/mobilenet_ssd_v2_face_quant_postprocess_edgetpu.tflite"
		self.engine = edgetpu.detection.engine.DetectionEngine(self.model_path)
		self.camera = PiCamera()
		self.camera.resolution = (320, 320)
		self.camera.framerate = 24
		self.rawCapture = PiRGBArray(self.camera, size=(320, 320))
		#self.rawCapture = bytearray(camera.resolution[0] * camera.resolution[1] *)
		self.camera.start_preview(fullscreen=False, layer=0, window=(0, 0, 320, 320))
		time.sleep(2) #camera warm-up
		#self.stream = self.camera.capture_continuous(self.rawCapture, format="bgr", use_video_port=True)
		self.frame = None
		self.frame_buf_val = None
		self.output = None
		self.stopped = False

	def start(self):
		Thread(target=self.update, daemon=True, args=()).start()
		return self

	def update(self):
		#self.stream.seek(0)
		#self.stream.readinto(self.rawCapture)
		self.stream = camera.capture(self.rawCapture, use_video_port=True, format='bgr')
		self.rawCapture.seek(0)
		self.stream.readinto(self.rawCapture)
		for f in self.stream:
			self.frame = io.BytesIO(f.array)
			self.frame_buf_val = np.frombuffer(self.frame.getvalue(), dtype=np.uint8)
			self.output = self.engine.DetectWithInputTensor(self.frame_buf_val, top_k=10)
			#self.rawCapture.truncate()
		self.stream.close()
		if self.stopped:
			self.stream.close()
			self.rawCapture.close()
			self.camera.close()
			return

	def read(self):
		return self.output
	
	def get_elapsed(self):
		return self.elapsed_ms

	def stop(self):
		self.stopped = True
