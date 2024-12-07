from imutils.video import VideoStream
import imutils
import time
import cv2
import threading
from threading import Event

outputFrame = None
lock = threading.Lock()
vs = None
cam_status = 'off'

def controll_camera(status):
	global cam_status
	cam_status = status	

def detect_motion(frameCount, stop_event):
	global vs, outputFrame, lock
	vs = VideoStream(0).start()
	time.sleep(1.0)
	global cam_status
	while not stop_event.is_set():
		frame = vs.read()
		if frame is None:
			print("Frame is None, waiting for a valid frame...")
			time.sleep(0.1)  # Chờ một lúc để tránh tiêu tốn CPU
			continue
			# Copy frame nếu frame hợp lệ
		
		# Đảm bảo thread dừng khi cam_status là "off" hoặc có yêu cầu dừng từ stop_event
		if cam_status != 'on':
			break

		try:
			with lock:
				outputFrame = frame.copy()
		except AttributeError as e:
			print(f"Error copying frame: {e}")
			break
	print('Close Camera')
	vs.stop()
	time.sleep(2)

def generate():
	global outputFrame, lock
	while True:
		with lock:
			if outputFrame is None:
				continue
			(flag, encodedImage) = cv2.imencode(".jpg", outputFrame)
			if not flag:
				continue
		yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
			bytearray(encodedImage) + b'\r\n')