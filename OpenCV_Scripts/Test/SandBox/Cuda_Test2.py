import cv2 as cv
CAMERA1 = "/dev/v4l/by-path/platform-3610000.xhci-usb-0:3.2:1.0-video-index0"
vod = cv.VideoCapture(CAMERA1)



scale = 0.5

gpu_frame = cv.cuda_GpuMat()

while True :
    ret, frame = vod.read()
    gpu_frame.upload(frame)
    resized = cv.cuda.resize(gpu_frame, (int(1280 * scale), int(720 * scale)))
    
    luv = cv.cuda.cvtColor(resized, cv.COLOR_BGR2LUV)
    #print ("1")
    hsv = cv.cuda.cvtColor(resized, cv.COLOR_BGR2HSV)
    gray = cv.cuda.cvtColor(resized, cv.COLOR_BGR2GRAY)
    
    # download new image(s) from GPU to CPU (cv2.cuda_GpuMat -> numpy.ndarray)
    resized = resized.download()
    luv = luv.download()
    hsv = hsv.download()
    gray = gray.download()

    cv.imshow("luv", luv)
    cv.imshow("hsv", hsv)
    cv.imshow("gray", gray)

    if cv.waitKey(30) >= 0 :
            break

exit(0)

if __name__ == "__main__":
    main()
