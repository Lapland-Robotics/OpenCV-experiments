# Calculate camera calibration parameters. Idea/Source from https://github.com/stereolabs/zed-opencv-native
# and it is Copy Righted "Copyright (c) 2018, STEREOLABS."
# Edited by HK

import numpy as np   # numpy arrays in use
import configparser  # parse calibration file
import cv2 as cv     # OpenCV 

  ################################################################################################################
def init_calibration(calibration_file, real_width, height, SET_RESOLUTION) :  
  cameraMatrix_left = cameraMatrix_right = map_left_y = map_left_x = map_right_y = map_right_x = np.array([])

  config = configparser.ConfigParser()
  config.read(calibration_file)
  T_ = np.array([-float(config['STEREO']['Baseline'] if 'Baseline' in config['STEREO'] else 0),
                   float(config['STEREO']['TY_'+SET_RESOLUTION] if 'TY_'+SET_RESOLUTION in config['STEREO'] else 0),
                   float(config['STEREO']['TZ_'+SET_RESOLUTION] if 'TZ_'+SET_RESOLUTION in config['STEREO'] else 0)])


  left_cam_cx = float(config['LEFT_CAM_'+SET_RESOLUTION]['cx'] if 'cx' in config['LEFT_CAM_'+SET_RESOLUTION] else 0)
  left_cam_cy = float(config['LEFT_CAM_'+SET_RESOLUTION]['cy'] if 'cy' in config['LEFT_CAM_'+SET_RESOLUTION] else 0)
  left_cam_fx = float(config['LEFT_CAM_'+SET_RESOLUTION]['fx'] if 'fx' in config['LEFT_CAM_'+SET_RESOLUTION] else 0)
  left_cam_fy = float(config['LEFT_CAM_'+SET_RESOLUTION]['fy'] if 'fy' in config['LEFT_CAM_'+SET_RESOLUTION] else 0)
  left_cam_k1 = float(config['LEFT_CAM_'+SET_RESOLUTION]['k1'] if 'k1' in config['LEFT_CAM_'+SET_RESOLUTION] else 0)
  left_cam_k2 = float(config['LEFT_CAM_'+SET_RESOLUTION]['k2'] if 'k2' in config['LEFT_CAM_'+SET_RESOLUTION] else 0)
  left_cam_p1 = float(config['LEFT_CAM_'+SET_RESOLUTION]['p1'] if 'p1' in config['LEFT_CAM_'+SET_RESOLUTION] else 0)
  left_cam_p2 = float(config['LEFT_CAM_'+SET_RESOLUTION]['p2'] if 'p2' in config['LEFT_CAM_'+SET_RESOLUTION] else 0)
  left_cam_p3 = float(config['LEFT_CAM_'+SET_RESOLUTION]['p3'] if 'p3' in config['LEFT_CAM_'+SET_RESOLUTION] else 0)
  left_cam_k3 = float(config['LEFT_CAM_'+SET_RESOLUTION]['k3'] if 'k3' in config['LEFT_CAM_'+SET_RESOLUTION] else 0)

  right_cam_cx = float(config['RIGHT_CAM_'+SET_RESOLUTION]['cx'] if 'cx' in config['RIGHT_CAM_'+SET_RESOLUTION] else 0)
  right_cam_cy = float(config['RIGHT_CAM_'+SET_RESOLUTION]['cy'] if 'cy' in config['RIGHT_CAM_'+SET_RESOLUTION] else 0)
  right_cam_fx = float(config['RIGHT_CAM_'+SET_RESOLUTION]['fx'] if 'fx' in config['RIGHT_CAM_'+SET_RESOLUTION] else 0)
  right_cam_fy = float(config['RIGHT_CAM_'+SET_RESOLUTION]['fy'] if 'fy' in config['RIGHT_CAM_'+SET_RESOLUTION] else 0)
  right_cam_k1 = float(config['RIGHT_CAM_'+SET_RESOLUTION]['k1'] if 'k1' in config['RIGHT_CAM_'+SET_RESOLUTION] else 0)
  right_cam_k2 = float(config['RIGHT_CAM_'+SET_RESOLUTION]['k2'] if 'k2' in config['RIGHT_CAM_'+SET_RESOLUTION] else 0)
  right_cam_p1 = float(config['RIGHT_CAM_'+SET_RESOLUTION]['p1'] if 'p1' in config['RIGHT_CAM_'+SET_RESOLUTION] else 0)
  right_cam_p2 = float(config['RIGHT_CAM_'+SET_RESOLUTION]['p2'] if 'p2' in config['RIGHT_CAM_'+SET_RESOLUTION] else 0)
  right_cam_p3 = float(config['RIGHT_CAM_'+SET_RESOLUTION]['p3'] if 'p3' in config['RIGHT_CAM_'+SET_RESOLUTION] else 0)
  right_cam_k3 = float(config['RIGHT_CAM_'+SET_RESOLUTION]['k3'] if 'k3' in config['RIGHT_CAM_'+SET_RESOLUTION] else 0)

  R_zed = np.array([float(config['STEREO']['RX_'+SET_RESOLUTION] if 'RX_' + SET_RESOLUTION in config['STEREO'] else 0),
                      float(config['STEREO']['CV_'+SET_RESOLUTION] if 'CV_' + SET_RESOLUTION in config['STEREO'] else 0),
                      float(config['STEREO']['RZ_'+SET_RESOLUTION] if 'RZ_' + SET_RESOLUTION in config['STEREO'] else 0)])

  R, _ = cv.Rodrigues(R_zed)
  cameraMatrix_left = np.array([[left_cam_fx, 0, left_cam_cx],
                         [0, left_cam_fy, left_cam_cy],
                         [0, 0, 1]])

  cameraMatrix_right = np.array([[right_cam_fx, 0, right_cam_cx],
                          [0, right_cam_fy, right_cam_cy],
                          [0, 0, 1]])

  distCoeffs_left = np.array([[left_cam_k1], [left_cam_k2], [left_cam_p1], [left_cam_p2], [left_cam_k3]])

  distCoeffs_right = np.array([[right_cam_k1], [right_cam_k2], [right_cam_p1], [right_cam_p2], [right_cam_k3]])

  T = np.array([[T_[0]], [T_[1]], [T_[2]]])
  R1 = R2 = P1 = P2 = np.array([])

  R1, R2, P1, P2 = cv.stereoRectify(cameraMatrix1=cameraMatrix_left,
                                       cameraMatrix2=cameraMatrix_right,
                                       distCoeffs1=distCoeffs_left,
                                       distCoeffs2=distCoeffs_right,
                                       R=R, T=T,
                                       flags=cv.CALIB_ZERO_DISPARITY,
                                       alpha=0,
                                       imageSize=(int(real_width), int(height)),
                                       newImageSize=(int(real_width), int(height)))[0:4]
  
  map_left_x, map_left_y = cv.initUndistortRectifyMap(cameraMatrix_left, distCoeffs_left, R1, P1, (int(real_width), int(height)), cv.CV_32FC1)
  map_right_x, map_right_y = cv.initUndistortRectifyMap(cameraMatrix_right, distCoeffs_right, R2, P2, (int(real_width), int(height)), cv.CV_32FC1)

  cameraMatrix_left = P1
  cameraMatrix_right = P2

  return cameraMatrix_left, cameraMatrix_right, map_left_x, map_left_y, map_right_x, map_right_y

  ################################################################################################################
