#!/bin/python3

import cv2
vcap = cv2.VideoCapture("http://158.58.130.148/mjpg/video.mjpg")

while (1):
  ret, frame = vcap.read()
  cv2.imshow('VIDEO', frame)
  cv2.waitKey(1)

exit(0)
