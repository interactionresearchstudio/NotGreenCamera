#!/usr/bin/env python
import cv2
import json
import time
import datetime
import numpy as np

# pi specific imports
from picamera.array import PiRGBArray
from picamera import PiCamera
import RPi.GPIO as GPIO
# end of imports

# load configuration file
os.chdir("/home/pi/NotGreen")
config = json.load(open("config.json"))

cv2.namedWindow("Output", cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty("Output", cv2.WND_PROP_FULLSCREEN, 1)

# camera
camera = PiCamera()
camera.resolution = (320,240)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(320,240))
time.sleep(config["camera_warmup"])

# buttons
btn1 = 17
btn2 = 22
btn3 = 23
btn4 = 27
btnShutter = btn1
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(btn1, GPIO.IN, GPIO.PUD_UP)
GPIO.setup(btn2, GPIO.IN, GPIO.PUD_UP)
GPIO.setup(btn3, GPIO.IN, GPIO.PUD_UP)
GPIO.setup(btn4, GPIO.IN, GPIO.PUD_UP)

sensitivity = config["sensitivity"]
lowerGreen = [60 - sensitivity, 100, 50]
upperGreen = [60 + sensitivity, 255, 255]

kernel = np.ones((3,3), np.uint8)

# screen flashing when pic is taken
lastPictureTaken = 0
flashDuration = 0.3
blue = np.zeros((240, 320, 3), np.uint8)
blue[:] = (255,0,0)
pictureTaken = False

def takePicture(picture):
    timestamp = datetime.datetime.now()
    picName = timestamp.strftime('%Y-%m-%d-%H-%M-%S')
    cv2.imwrite(picName + ".jpg", picture)

# main loop
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    # get new frame
    image = frame.array
    # end of new frame

    # convert image to hsv colour space
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    greenMask = cv2.inRange(hsv, np.array(lowerGreen), np.array(upperGreen))
    greenMask = cv2.dilate(greenMask, kernel, iterations = 1)
    everythingElseMask = cv2.bitwise_not(greenMask)
    output = cv2.bitwise_and(image, image, mask = everythingElseMask) 

    if pictureTaken is True:
        currentTime = time.time()
        if currentTime - lastPictureTaken >= flashDuration:
            pictureTaken = False
        else:
            cv2.imshow("Output", blue)
    else:
        cv2.imshow("Output", output)

    if GPIO.input(btnShutter) == False:
        takePicture(output)
        lastPictureTaken = time.time()
        pictureTaken = True

    # clear buffer
    rawCapture.truncate(0)
    key = cv2.waitKey(10)
    # end of loop

# cleanup
cv2.destroyWindow("Output")
