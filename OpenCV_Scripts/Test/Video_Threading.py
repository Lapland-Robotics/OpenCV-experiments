# Threading some video capture etc....
# HK, LapinAMK

import cv2 as cv                       # OpenCV
from threading import Thread, Lock     # Python threading
import time


# Threads
class capture_video_class:
   # Initialize
   def __init__(self, CAMERA, input_height, input_width):
       #Initialize video capturing
       self.video_capture = cv.VideoCapture(CAMERA)
       if not self.video_capture.isOpened(): # if video_captured.isOpen == 0 :
           print ("Cannot open Camera")
           exit()
       (self.capture_OK, self.captured_frame) = self.video_capture.read()
       #Shape function return image rows, columns and channels (if color image)
       self.height, self.width, self.color = self.captured_frame.shape
       # Check resolution and change it if needed
       if self.height == input_height:
          print ("Resolution OK: ", self.width, "x", self.height)
       else:
          print ("Resolution: ", self.width, "x", self.height,"  Changing Resolution...")
          # Set the video resolution 
          self.video_capture.set(cv.CAP_PROP_FRAME_WIDTH, input_width)
          self.video_capture.set(cv.CAP_PROP_FRAME_HEIGHT, input_height)
          # Check resolution again
          (self.capture_OK, self.captured_frame) = self.video_capture.read()
          self.height, self.width, self.color = self.captured_frame.shape
          if self.height == input_height:
             print ("Resolution OK: ",  self.width, "x", self.height)
          else:
             print ("Unable to change Resolution")
             exit()
       self.started = False
       self.read_lock = Lock()
       # Start thread
   def start(self):
       print ("Starting capture thread")
       self.running = True
       # Create thread
       self.thread = Thread(target=self.capture, args=())
       self.thread.start()
       return self
   # Running Capture (threaded)
   def capture(self):
       while self.running and self.capture_OK == True:
            # Acquire read thread lock
            self.read_lock.acquire()
            # Read frame
            (self.capture_OK, self.captured_frame) = self.video_capture.read()
            
            self.read_lock.release()
            time.sleep(0.0333)
   # update captured frame for main function "read"
   def read(self) :
       self.read_lock.acquire()
       frame = self.captured_frame.copy()
       self.read_lock.release()
       return frame
   # Stop the thread 
   def stop(self):
       print ("Stopping capture thread")
       self.running = False
       self.thread.join()
   def __exit__(self, exc_type, exc_value, traceback) :
       self.video_capture.release()


