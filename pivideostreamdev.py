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
		self.DISPLAY = pi3d.Display.create(0, 0, w=preview_W, h=preview_H, layer=1, frames_per_second=max_fps)
		self.DISPLAY.set_background(0.0, 0.0, 0.0, 0.0) # transparent
		self.keybd = pi3d.Keyboard()
		self.txtshader = pi3d.Shader("uv_flat")
		self.linshader = pi3d.Shader('mat_flat')
		self.CAMERA = pi3d.Camera(is_3d=False)
		self.font = pi3d.Font("fonts/FreeMono.ttf", font_size=30, color=(0, 255, 0, 255)) # blue green 1.0 alpha
		self.model_path = "/home/pi/python-tflite-source/edgetpu/test_data/mobilenet_ssd_v2_face_quant_postprocess_edgetpu.tflite"
		self.engine = edgetpu.detection.engine.DetectionEngine(self.model_path)
		self.camera = PiCamera()
		self.camera.resolution = (320, 320)
		self.camera.framerate = 24
		#self.rawCapture = PiRGBArray(self.camera, size=(320, 320))
		self.rawCapture = bytearray(self.camera.resolution[0] * self.camera.resolution[1] * 3)
		self.camera.start_preview(fullscreen=False, layer=0, window=(0, 0, 320, 320))
		time.sleep(2) #camera warm-up
		self.stream = io.BytesIO()
		#self.stream = self.camera.capture_continuous(self.rawCapture, format="bgr", use_video_port=True)
		self.frame = None
		self.frame_buf_val = None
		self.output = None
		self.stopped = False
		self.max_obj = 10
		self.X_OFF = np.array([0, 0, -1, -1, 0, 0, 1, 1])
		self.Y_OFF = np.array([-1, -1, 0, 0, 1, 1, 0, 0])
		self.X_IX = np.array([0, 1, 1, 1, 1, 0, 0, 0])
		self.Y_IX = np.array([0, 0, 0, 1, 1, 1, 1, 0])
		self.verts = [[0.0, 0.0, 1.0] for i in range(8 * self.max_obj)] # need a vertex for each end of each side 
		self.bbox = pi3d.Lines(vertices=self.verts, material=(1.0,0.8,0.05), closed=False, strip=False, line_width=4) 
		self.bbox.set_shader(self.linshader)

	def start(self):
		Thread(target=self.update, daemon=True, args=()).start()
		return self

	def update(self):
		self.camera.capture(self.stream, use_video_port=True, format='rgb')
		self.stream.seek(0)
		self.stream.readinto(self.rawCapture)
		self.frame_buf_val = np.frombuffer(self.stream.getvalue(), dtype=np.uint8)
		#self.stream.truncate(0)
		self.output = self.engine.DetectWithInputTensor(self.frame_buf_val, top_k=10)
		if self.output:
			num_obj = 0
			for obj in self.output:
				num_obj = num_obj + 1   
				buf = self.bbox.buf[0] # alias for brevity below
				buf.array_buffer[:,:3] = 0.0;
				for j, obj in enumerate(self.output):
					coords = (obj.bounding_box - 0.5) * [[1.0, -1.0]] * mdl_dims # broadcasting will fix the arrays size differences
					score = round(obj.score,2)
					ix = 8 * j
					buf.array_buffer[ix:(ix + 8), 0] = coords[X_IX, 0] + 2 * self.X_OFF
					buf.array_buffer[ix:(ix + 8), 1] = coords[Y_IX, 1] + 2 * self.Y_OFF
				buf.re_init(); # 
				self.bbox.draw() # i.e. one draw for all boxes
		#self.stream.close()
		#for f in self.stream:
		#	self.frame = io.BytesIO(f.array)
		#	self.frame_buf_val = np.frombuffer(self.frame.getvalue(), dtype=np.uint8)
		#	self.output = self.engine.DetectWithInputTensor(self.frame_buf_val, top_k=10)
		#	self.rawCapture.truncate(0)
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
