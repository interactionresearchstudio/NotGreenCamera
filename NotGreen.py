import cv2
import json
import time
import datetime
import numpy as np

# configuration file
config = json.load(open("config.json"))
# end of configuration file

# window
cv2.namedWindow("Output")
# end of window

# camera
capture = cv2.VideoCapture(0)
capture.set(3, 320)
capture.set(4, 240)
if capture.isOpened():
    rval, frame = capture.read()
else:
    rval = False
time.sleep(config["camera_warmup"])
# end of camera

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
while rval:
    # new frame
    rval, image = capture.read()
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

    # wait for keys
    key = cv2.waitKey(10)
    if key == ord("p") and pictureTaken is False:
        takePicture(output)
        lastPictureTaken = time.time()
        pictureTaken = True
    if key == 27:
        break
    # end of loop

# cleanup
cv2.destroyWindow("Output")
