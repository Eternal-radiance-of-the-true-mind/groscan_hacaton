import cv2

GRAYSCALE_MODE = False
HOSTEL_STREAM = True

cv2.namedWindow("Pioneer View", cv2.WINDOW_NORMAL)
cv2.namedWindow("Point1 0°", cv2.WINDOW_NORMAL)
cv2.namedWindow("Point1 90°", cv2.WINDOW_NORMAL)
cv2.namedWindow("Point1 180°", cv2.WINDOW_NORMAL)
cv2.namedWindow("Point1 270°", cv2.WINDOW_NORMAL)

# подключение к rtsp потоку (как запустить проигрывание видео с коптера смотри в README)
if HOSTEL_STREAM:
    rtsp_stream = cv2.VideoCapture("http://158.58.130.148/mjpg/video.mjpg")
    point1_original = cv2.imread("imgs/chair-90.png", cv2.IMREAD_GRAYSCALE if GRAYSCALE_MODE else cv2.IMREAD_COLOR)  # 0439.png
else:
    rtsp_stream = cv2.VideoCapture("rtsp://127.0.0.1:8554/stream6")
    point1_original = cv2.imread("imgs/0439.png", cv2.IMREAD_GRAYSCALE if GRAYSCALE_MODE else cv2.IMREAD_COLOR)  # 0439.png
point1_original_w, point1_original_h = (point1_original.shape[0], point1_original.shape[1])

# поворот искомой картинки (4 раза по 90 градусов)
point1_rotated = []
for angle in range(0, 4):
    if angle == 0:
        point1_rotated.append((point1_original, point1_original_w, point1_original_h))
    else:
        center1_x, center1_y = (point1_original_w // 2, point1_original_h // 2)
        # print(point1_original.shape, center1_x, center1_y)
        M = cv2.getRotationMatrix2D((center1_x, center1_y), angle*90, 1.0)
        point1 = cv2.warpAffine(point1_original, M, (point1_original_w, point1_original_h))
        point1_w, point1_h = (point1.shape[0], point1.shape[1])
        point1_rotated.append((point1, point1_w, point1_h))

# работа с видео потоком, перебор повернутых изображений в видео-потоке
while True:
    ret, frame = rtsp_stream.read()
    if GRAYSCALE_MODE:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    for angle, (point1, point1_w, point1_h) in enumerate(point1_rotated):
        result = cv2.matchTemplate(frame, point1, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        if max_loc:
            (x, y) = max_loc
            cv2.rectangle(frame, (x, y), (x + point1_w, y + point1_h), (0, 0, 255), 2)
        cv2.imshow("Point1 {}°".format(angle*90), result)
    if ret:
        cv2.imshow("Pioneer View", frame)
        cv2.waitKey(1)
    else:
        print("unable to open camera")
        break
rtsp_stream.release()

cv2.destroyAllWindows()
