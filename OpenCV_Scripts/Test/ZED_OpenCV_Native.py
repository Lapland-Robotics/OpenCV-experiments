# Created by HK, LapinAMK
# 
# Partial code Copy Righted "Copyright (c) 2018, STEREOLABS." https://github.com/stereolabs/zed-opencv-native
#'''
# Here we captur images from single stereo ZED camera and create calbirated left and right images.
# And some filter test same time.
#'''

import numpy as np   # numpy arrays in use
import os            # user path etc...
import time          # calculating processing time
import cv2 as cv     # OpenCV
from ZED2_Calibration import init_calibration  # Initialize ZED2 camera calibration

# Use specific camera in specific USB3 port.
CAMERA = "/dev/v4l/by-path/platform-3610000.xhci-usb-0:3.2:1.0-video-index0"

# Serian number from "specific" camera
CAMERA_SRN = "29027952"

#Path to where ZED camera calibration is
CALIB_PATH = "/OpenCV_Scripts/ZED2_Calibrations/"

#ZED2 Resolutions (height, width): "2K" = [1242, 4416] / "FHD" = [1080, 3840] / "HD" = [720, 2560] / "VGA" = [376, 1344]
# Terms 2K, FHD, HD and VGA comes from ZED2 Calibration files 
#NOTE! Width includes both left and right images
SET_RESOLUTION = "HD" #

# For programming lovers: resolution set
def switch_resolution (SET_RESOLUTION):
  switcher = {
     "2K": [1242, 4416],
     "FHD": [1080, 3840],
     "HD": [720, 2560],
     "VGA": [376, 1344]
    }
  return switcher.get(SET_RESOLUTION, [0,0])


#Initialize video capturing
video_capture = cv.VideoCapture(CAMERA)
if not video_capture.isOpened(): # if video_captured.isOpen == 0 :
  print ("Cannot open Camera")
  exit()

#Read one frame for resolution check  # capture_OK = boolean, True when captured and False when not captured, captured_frame = captured frame array
capture_OK, captured_frame = video_capture.read()

#Shape function return image rows, columns and channels (if color image)
height, width, color = captured_frame.shape

# Check resolution and change it if needed
if height == switch_resolution(SET_RESOLUTION)[0]:
  print ("Resolution OK: ", width, "x", height)
else:
  print ("Resolution: ", width, "x", height,"  Changing Resolution...")
  # Set the video resolution 
  video_capture.set(cv.CAP_PROP_FRAME_WIDTH, switch_resolution(SET_RESOLUTION)[1])
  video_capture.set(cv.CAP_PROP_FRAME_HEIGHT, switch_resolution(SET_RESOLUTION)[0])
  # Check resolution again
  capture_OK, captured_frame = video_capture.read()
  height, width, color = captured_frame.shape
  if height == switch_resolution(SET_RESOLUTION)[0]:
    print ("Resolution OK: ",  width, "x", height)
  else:
    print ("Unable to change Resolution")
    exit()

# Left and Right images real width
real_width = width/2

# Load calibration file and calculate calibration parameters
calibration_file = os.path.expanduser("~") + CALIB_PATH + 'SN' + CAMERA_SRN + '.conf'
print (calibration_file)
if os.path.isfile(calibration_file) :
  print("Calibration file found. Loading...")
  # Call call "Calibration" function from ZED2_Calibration.py
  camera_matrix_left, camera_matrix_right, map_left_x, map_left_y, map_right_x, map_right_y = init_calibration(calibration_file, real_width, height, SET_RESOLUTION)
else:
  print("Calibration file NOT found!")
  exit(1)

# Variables for calculatin processing time
time_now = 0
time_previous = 0

# For scaling
#scale = 0.5

#gpu_frame is "Base storage class for GPU memory with reference counting." https://docs.opencv.org/4.5.3/d0/d60/classcv_1_1cuda_1_1GpuMat.html
gpu_frame = cv.cuda_GpuMat()

#All used arrays need to be GpuMat().......
gpu_map_left_x = cv.cuda_GpuMat(map_left_x)
gpu_map_left_y = cv.cuda_GpuMat(map_left_y)
gpu_map_right_x = cv.cuda_GpuMat(map_right_x)
gpu_map_right_y = cv.cuda_GpuMat(map_right_y)

#print ("Width",int(real_width))

while capture_OK == True :
  #calculate processing time
  time_now = time.time()
  fps = 1/(time_now-time_previous)
  time_previous = time_now

  # Read frame
  capture_OK, captured_frame = video_capture.read()

  # Load frame to GPU
  gpu_frame.upload(captured_frame)

  # Divide image to left and right / return_value = cv.cuda_GpuMat.adjustROI(dtop, dbottom, dleft, dright)
  #left_raw = gpu_frame.adjustROI(int(0),int(0),int(0),int(real_width))
  right_raw = gpu_frame.adjustROI(int(0),int(0),int(-real_width),int(0))

  #resized = cv.cuda.resize(gpu_frame, (int(1280 * scale), int(720 * scale)))
  #luv = cv.cuda.cvtColor(left, cv.COLOR_BGR2LUV)
  #hsv = cv.cuda.cvtColor(left, cv.COLOR_BGR2HSV)
  #gray = cv.cuda.cvtColor(left, cv.COLOR_BGR2GRAY)
  
  # Calibrate images
  #left = cv.cuda.remap(left_raw, gpu_map_left_x, gpu_map_left_y, interpolation=cv.INTER_LINEAR)
  right = cv.cuda.remap(right_raw, gpu_map_right_x, gpu_map_right_y, interpolation=cv.INTER_LINEAR)

  # download new image(s) from GPU to CPU (cv.cuda_GpuMat -> numpy.ndarray)
  #resized = resized.download()

  # CPU canny edge
  #left_canny = cv.Canny(left.download(), 10, 255)
  right_canny = cv.Canny(right.download(), 10, 255)
  
  # GPU binary threshold 
  #thresh = cv.cuda.threshold(gray, 50, 255, cv.THRESH_BINARY)
  #thresh = thresh[1].download()
  #luv = luv.download()
  #hsv = hsv.download()
  #gray = gray.download()
  #left = left.download()
  #right = right.download()

  # Put FPS overlay to image
  #right = cv.putText(right, "FPS:{:.2f}".format(fps),(5, 15), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv.LINE_AA)
  right_canny = cv.putText(right_canny, "FPS:{:.2f}".format(fps),(5, 15), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv.LINE_AA)


  # Draw images
  #cv.imshow("Left", left)
  #cv.imshow("Right", right)
  #cv.imshow("hsv", hsv)
  #cv.imshow("gray", gray)
  #cv.imshow("tresh", thresh)
  #cv.imshow("Left canny", left_canny)
  cv.imshow("Right canny", right_canny)

  if cv.waitKey(30) >= 0 :
     break

exit(0)

if __name__ == "__main__":
    main()  
