import cv2

GRAYSCALE_MODE = False
ROTATION_ANGLE = 0
HOSTEL_STREAM = True

cv2.namedWindow("Pioneer View", cv2.WINDOW_NORMAL)
cv2.namedWindow("Point1", cv2.WINDOW_NORMAL)

if HOSTEL_STREAM:
    rtsp_stream = cv2.VideoCapture("http://158.58.130.148/mjpg/video.mjpg")
    point1_original = cv2.imread("imgs/chair-90.png", cv2.IMREAD_GRAYSCALE if GRAYSCALE_MODE else cv2.IMREAD_COLOR)  # 0439.png
else:
    rtsp_stream = cv2.VideoCapture("rtsp://127.0.0.1:8554/stream6")
    point1_original = cv2.imread("imgs/0439.png", cv2.IMREAD_GRAYSCALE if GRAYSCALE_MODE else cv2.IMREAD_COLOR)  # 0439.png
point1_original_w, point1_original_h = (point1_original.shape[0], point1_original.shape[1])

if ROTATION_ANGLE != 0:
    center1_x, center1_y = (point1_original_w // 2, point1_original_h // 2)
    #print(point1_original.shape, center1_x, center1_y)
    M = cv2.getRotationMatrix2D((center1_x, center1_y), ROTATION_ANGLE, 1.0)
    point1 = cv2.warpAffine(point1_original, M, (point1_original_w, point1_original_h))
    point1_w, point1_h = (point1.shape[0], point1.shape[1])
    cv2.imshow("Rotated", point1)
else:
    point1 = point1_original
    point1_w, point1_h = point1_original_w, point1_original_h

while True:
    ret, frame = rtsp_stream.read()
    if GRAYSCALE_MODE:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    result = cv2.matchTemplate(frame, point1, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    if max_loc:
        (x, y) = max_loc
        cv2.rectangle(frame, (x, y), (x + point1_w, y + point1_h), (0, 0, 255), 2)
    if ret:
        cv2.imshow("Pioneer View", frame)
        cv2.imshow("Point1", result)
        cv2.waitKey(1)
    else:
        print("unable to open camera")
        break
rtsp_stream.release()

cv2.destroyAllWindows()
