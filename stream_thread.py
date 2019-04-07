import io
import time
import threading
import picamera
import pi3d

# Create a pool of image processors
done = False
lock = threading.Lock()
pool = []

class ImageProcessor(threading.Thread):
    def __init__(self):
        super(ImageProcessor, self).__init__()
        self.stream = io.BytesIO()
        self.event = threading.Event()
        self.terminated = False
        self.start()

    def run(self):
        # This method runs in a separate thread
        global done
        while not self.terminated:
            if self.event.wait(1):
                try:
                    self.stream.seek(0)
                    # Read the image and do some processing on it
                    #Image.open(self.stream)
                    #...
                    #...
                    # Set done to True if you want the script to terminate
                    # at some point
                    #done=True
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
            processor = pool.pop()
        yield processor.stream
        processor.event.set()

with picamera.PiCamera() as camera:
	keybd = pi3d.Keyboard()
	pool = [ImageProcessor() for i in range (4)]
	camera.resolution = (320, 320)
	# Set the framerate appropriately; too fast and the image processors
	# will stall the image pipeline and crash the script
	camera.framerate = 24
	camera.start_preview(fullscreen=False, layer=0, window=(0, 0, 320, 320))
	time.sleep(2)
	camera.capture_sequence(streams(), use_video_port=True)
	while DISPLAY.loop_running():
		if keybd.read() == 27:
			keybd.close()
			camera.close()
			while pool:
				with lock:
					processor = pool.pop()
				processor.terminated = True
				processor.join()
			break

# Shut down the processors in an orderly fashion
#while pool:
#    with lock:
#        processor = pool.pop()
#    processor.terminated = True
#    processor.join()
