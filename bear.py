import cv2
import numpy as np

THRESHOLD = 0.80  # степень правдоподобности 80% и выше
RESIZE_PERCENT = 0.13

cv2.namedWindow("Pioneer View", cv2.WINDOW_NORMAL)
cv2.namedWindow("Point1", cv2.WINDOW_NORMAL)

map = cv2.imread("imgs/bear-enlarged.png")
point1_original = cv2.imread("imgs/bear-small.png")
# проверяем, что размеры картинок совпадают, и они являются квадратами, иначе методы поворота не работают
# (поворот выполняется за пределы картинки, если центр вращения - центр прямоугольника)
assert point1_original.shape[1] == point1_original.shape[0]
# в shape при загрузке картинки идёт сначала ширина, а потом высота
point1_original_w, point1_original_h = (point1_original.shape[1], point1_original.shape[0])
center1_x, center1_y = (point1_original_w // 2, point1_original_h // 2)

# поворот искомой картинки (4 раза по 90 градусов)
point1_rotated = []
for angle in range(0, 4):
    # создаём матрицу поворота
    M = cv2.getRotationMatrix2D((center1_x, center1_y), angle*90, 1.0)
    # вычисляем размеры повёрнутой картинки (так и не удалось повернуть прямоугольник)
    dsize = (point1_original_w, point1_original_h)
    # поворачиваем картинку и маску
    point1 = cv2.warpAffine(point1_original, M, dsize)
    # вычисляем размеры повёрнутой картинки (у квадратов они одинаковые)
    point1_w, point1_h = (point1.shape[1], point1.shape[0])
    assert point1_original_w == point1_w
    print(angle*90, 'wh', point1_w, point1_h, 'dsize', dsize, 'shape', point1.shape, 'center', center1_x, center1_y)
    # добавление повернутых изображений в список
    point1_rotated.append((angle*90, point1.copy(), point1_w, point1_h, 1.0))
    # теперь ресайзим изображения (уменьшаем)
    dsize = (int((1.0-RESIZE_PERCENT)*point1_original_w), int((1.0-RESIZE_PERCENT)*point1_original_h))
    print(dsize)
    point1_reduced = cv2.resize(point1, dsize)
    point1_rotated.append((angle*90, point1_reduced.copy(), dsize[0], dsize[1], 1.0-RESIZE_PERCENT))
    # увеличиваем
    dsize = (int((1.1 + RESIZE_PERCENT) * point1_original_w), int((1.1 + RESIZE_PERCENT) * point1_original_h))
    print(dsize)
    point1_enlarged = cv2.resize(point1, dsize)
    point1_rotated.append((angle * 90, point1_enlarged.copy(), dsize[0], dsize[1], 1.0+RESIZE_PERCENT))
    # удаляем скопированные объекты
    del point1_reduced
    del point1
    del M


frame = map
# составляем все версии всех найденных правдопободных сравнений
versions = []
for (angle, point1, point1_w, point1_h, resize) in point1_rotated:
    result = cv2.matchTemplate(frame, point1, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    # print(angle, min_val, max_val, min_loc, max_loc, resize)
    if max_val >= THRESHOLD:
        if max_loc:
            versions.append((
                result,
                min_val, max_val, min_loc, max_loc,
                angle, point1_w, point1_h, resize))
# если объекты найдены
if versions:
    # сортируем список в порядке уменьшения правдоподобности
    versions.sort(key=lambda x: x[2], reverse=True)
    # берём первый наиболее правдоподобный элемент (хотя можно перебрать их все)
    (result,
     min_val, max_val, min_loc, max_loc,
     angle, point1_w, point1_h, resize) = versions[0]
    # выводим результат
    (x, y) = max_loc
    cv2.rectangle(frame, (x, y), (x + point1_w-1, y + point1_h-1), (0, 0, 255), 5)
    cv2.rectangle(result, (x, y), (x + point1_w-1, y + point1_h-1), (255, 255, 255), 1)
    cv2.imshow("Point1", result)
del versions

cv2.imshow("Pioneer View", frame)
cv2.resizeWindow("Pioneer View", 800, 600)
cv2.waitKey()

cv2.destroyAllWindows()
