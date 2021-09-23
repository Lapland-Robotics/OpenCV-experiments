import faulthandler; faulthandler.enable()
import sys
import numpy as np
import pyzed.sl as sl
import cv2

import threading
import time
import signal

zed_list = []
left_list = []
#depth_image_zed = []
timestamp_list = []
thread_list = []
stop_signal = False


#############
def signal_handler(signal, frame):
    global stop_signal
    stop_signal=True
    time.sleep(0.5)
    exit()

def grab_run(index):
    global stop_signal
    global zed_list
    global timestamp_list
    global left_list
    #global depth_image_zed

    runtime = sl.RuntimeParameters()
    while not stop_signal:
        err = zed_list[index].grab(runtime)
        if err == sl.ERROR_CODE.SUCCESS:
            zed_list[index].retrieve_image(left_list[index], sl.VIEW.LEFT)
            #zed_list[index].retrieve_measure(depth_image_zed[index], sl.MEASURE.DEPTH)
            timestamp_list[index] = zed_list[index].get_timestamp(sl.TIME_REFERENCE.CURRENT).data_ns
        time.sleep(0.001) #1ms
    zed_list[index].close()
	
def main():
    global stop_signal
    global zed_list
    global left_list
    #global depth_image_zed
    global timestamp_list
    global thread_list
    signal.signal(signal.SIGINT, signal_handler)

    print("Running...")
    init = sl.InitParameters()
    init.camera_resolution = sl.RESOLUTION.HD720 #sl.RESOLUTION.HD1080
    init.camera_fps = 30  # The framerate is lowered to avoid any USB3 bandwidth issues
    init.depth_mode = sl.DEPTH_MODE.PERFORMANCE
    init.coordinate_units = sl.UNIT.MILLIMETER

    #List and open cameras
    Image_list = []
    #Depth_list = []
    last_ts_list = []
    cameras = sl.Camera.get_device_list()
    index = 0
    for cam in cameras:
        init.set_from_serial_number(cam.serial_number)
        Image_list.append("ZED {}".format(cam.serial_number))
        print("Opening {}".format(Image_list[index]))
       # Depth_list.append("ZED {}".format(cam.serial_number))
        print("Opening {}".format(Depth_list[index]))
        zed_list.append(sl.Camera())
        left_list.append(sl.Mat())
      #  depth_image_zed.append(sl.Mat())
        timestamp_list.append(0)
        last_ts_list.append(0)
        status = zed_list[index].open(init)
        if status != sl.ERROR_CODE.SUCCESS:
            print(repr(status))
            zed_list[index].close()
        index = index +1

    #Start camera threads
    for index in range(0, len(zed_list)):
        if zed_list[index].is_opened():
            thread_list.append(threading.Thread(target=grab_run, args=(index,)))
            thread_list[index].start()
    
    #Display camera images
    key = ''
    while key != 113:  # for 'q' key
        for index in range(0, len(zed_list)):
            if zed_list[index].is_opened():
                if (timestamp_list[index] > last_ts_list[index]):
                    cv2.imshow(Image_list[index], left_list[index].get_data())
              #      cv2.imshow(Depth_list[index], depth_image_zed[index].get_data())
        key = cv2.waitKey(10)
    cv2.destroyAllWindows()

    #Stop the threads
    stop_signal = True
    for index in range(0, len(thread_list)):
        thread_list[index].join()

    print("\nFINISH")

if __name__ == "__main__":
    main()

