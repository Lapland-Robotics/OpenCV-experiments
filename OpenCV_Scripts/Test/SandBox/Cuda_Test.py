import cv2 as cv
#CAMERA1 = "/dev/v4l/by-path/platform-3610000.xhci-usb-0:3.2:1.0-video-index0"
CAMERA1 = "/dev/video0"
vod = cv.VideoCapture(CAMERA1)



scale = 0.5

gpu_frame = cv.cuda_GpuMat()

ret, frame = vod.read()
height, width, poop = frame.shape
print ("Original", frame.shape)
divider = width/-2
print (height)
while True :
    ret, frame = vod.read()
    gpu_frame.upload(frame)
    #retval = cv.cuda_GpuMat.adjustROI(dtop, dbottom, dleft, dright)
    left = gpu_frame.adjustROI(int(0),int(0),int(0),int(divider))
    #resized = cv.cuda.resize(gpu_frame, (int(1280 * scale), int(720 * scale)))
    luv = cv.cuda.cvtColor(left, cv.COLOR_BGR2LUV)
    hsv = cv.cuda.cvtColor(left, cv.COLOR_BGR2HSV)
    gray = cv.cuda.cvtColor(left, cv.COLOR_BGR2GRAY)
    # download new image(s) from GPU to CPU (cv2.cuda_GpuMat -> numpy.ndarray)
    #resized = resized.download()
    # CPU canny edge
    canny = cv.Canny(left.download(), 10, 255)
    # GPU binary threshold 
    thresh = cv.cuda.threshold(gray, 50, 255, cv.THRESH_BINARY)
    thresh = thresh[1].download()
    luv = luv.download()
    hsv = hsv.download()
    gray = gray.download()
    left = left.download()



    cv.imshow("left", left)
    cv.imshow("hsv", hsv)
    cv.imshow("gray", gray)
    cv.imshow("tresh", thresh)
    cv.imshow("canny", canny)


    if cv.waitKey(30) >= 0 :
            break

exit(0)

if __name__ == "__main__":
    main()
