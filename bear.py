import cv2
import numpy as np

THRESHOLD = 0.80  # степень правдоподобности 80% и выше

cv2.namedWindow("Pioneer View", cv2.WINDOW_NORMAL)
cv2.namedWindow("Point1 0°", cv2.WINDOW_NORMAL)
cv2.namedWindow("Point1 90°", cv2.WINDOW_NORMAL)
cv2.namedWindow("Point1 180°", cv2.WINDOW_NORMAL)
cv2.namedWindow("Point1 270°", cv2.WINDOW_NORMAL)

map = cv2.imread("imgs/bear.png")
point1_original = cv2.imread("imgs/bear-small.png")
# point1_mask = cv2.imread("imgs/bear-small-mask.png")
# проверяем, что размеры картинок совпадают, и они являются квадратами, иначе методы поворота не работают
# (поворот выполняется за пределы картинки, если центр вращения - центр прямоугольника)
assert point1_original.shape[1] == point1_original.shape[0]
# assert point1_mask.shape[1] == point1_mask.shape[0]
# assert point1_original.shape[0] == point1_mask.shape[0]
# в shape при загрузке картинки идёт сначала ширина, а потом высота
point1_original_w, point1_original_h = (point1_original.shape[1], point1_original.shape[0])
point1_size = (point1_original_w, point1_original_h)
center1_x, center1_y = (point1_original_w // 2, point1_original_h // 2)

# поворот искомой картинки (4 раза по 90 градусов)
point1_rotated = []
for angle in range(0, 4):
    # создаём матрицу поворота
    M = cv2.getRotationMatrix2D((center1_x, center1_y), angle*90, 1.0)
    # вычисляем размеры повёрнутой картинки (так и не удалось повернуть прямоугольник)
    dsize = (point1_size[0], point1_size[1])
    # поворачиваем картинку и маску
    point1 = cv2.warpAffine(point1_original, M, dsize)
    # mask1 = cv2.warpAffine(point1_mask, M, dsize)
    # вычисляем размеры повёрнутой картинки (у квадратов они одинаковые)
    point1_w, point1_h = (point1.shape[1], point1.shape[0])
    assert point1_original_w == point1_w
    # assert point1_w == mask1.shape[1]
    print(angle*90, 'wh', point1_w, point1_h, 'dsize', dsize, 'shape', point1.shape, 'center', center1_x, center1_y)
    point1_rotated.append((point1.copy(), point1_w, point1_h))  # , mask1.copy()
    # del mask1
    del point1
    del M

frame = map
for angle, (point1, point1_w, point1_h) in enumerate(point1_rotated):  #, mask1
    result = cv2.matchTemplate(frame, point1, cv2.TM_CCOEFF_NORMED)  #, mask1
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    if max_val >= THRESHOLD:
        if max_loc:
            (x, y) = max_loc
            cv2.rectangle(frame, (x, y), (x + point1_w-1, y + point1_h-1), (0, 0, 255), 5)
            cv2.rectangle(result, (x, y), (x + point1_w-1, y + point1_h-1), (255, 255, 255), 1)
    cv2.imshow("Point1 {}°".format(angle*90), result)
    print(angle, min_val, max_val, min_loc, max_loc)
cv2.imshow("Pioneer View", frame)
cv2.waitKey()

cv2.destroyAllWindows()
