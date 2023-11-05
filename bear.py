import cv2
import numpy as np

THRESHOLD = 0.80  # степень правдоподобности 80% и выше
RESIZE_PERCENT = 0.13  # размер уменьшения и увеличения фрагментов во время поиска

cv2.namedWindow("Pioneer View", cv2.WINDOW_NORMAL)
cv2.namedWindow("Point1", cv2.WINDOW_NORMAL)
cv2.namedWindow("Point2", cv2.WINDOW_NORMAL)

map = cv2.imread("imgs/bear-reduced.png")
# настройки поиска элементов на карте
point1_original = cv2.imread("imgs/bear-point1.png")
point2_original = cv2.imread("imgs/bear-point2.png")
points_original = [
    (1, point1_original),  # первая точка и ей соответствующий маркер
    (2, point2_original)   # вторая точка и ей соответствующий маркер
]

#  список всех модифицированных фрагментов
point_rotated = []
# перебор всех элементов и подготовка фрагментов к поиску на карте
for (point_number, point_original) in points_original:
    # проверяем, что размеры картинок совпадают, и они являются квадратами, иначе методы поворота не работают
    # (поворот выполняется за пределы картинки, если центр вращения - центр прямоугольника)
    assert point_original.shape[1] == point_original.shape[0]
    # в shape при загрузке картинки идёт сначала ширина, а потом высота
    point_original_w, point_original_h = (point_original.shape[1], point_original.shape[0])
    center_x, center_y = (point_original_w // 2, point_original_h // 2)
    # поворот искомой картинки (4 раза по 90 градусов)
    for angle in range(0, 4):
        # создаём матрицу поворота
        M = cv2.getRotationMatrix2D((center_x, center_y), angle*90, 1.0)
        # вычисляем размеры повёрнутой картинки (так и не удалось повернуть прямоугольник)
        dsize = (point_original_w, point_original_h)
        # поворачиваем картинку и маску
        point = cv2.warpAffine(point_original, M, dsize)
        # вычисляем размеры повёрнутой картинки (у квадратов они одинаковые)
        point_w, point_h = (point.shape[1], point.shape[0])
        assert point_original_w == point_w
        # print(angle*90, 'wh', point_w, point_h, 'dsize', dsize, 'shape', point.shape, 'center', center_x, center_y)
        # добавление повернутых изображений в список
        point_rotated.append((
            point_number,
            angle*90,
            point.copy(), point_w, point_h,
            1.0))
        # теперь ресайзим изображения (уменьшаем)
        dsize = (int((1.0-RESIZE_PERCENT)*point_original_w), int((1.0-RESIZE_PERCENT)*point_original_h))
        point_reduced = cv2.resize(point, dsize)
        point_rotated.append((
            point_number,
            angle*90,
            point_reduced.copy(), dsize[0], dsize[1],
            1.0-RESIZE_PERCENT))
        # увеличиваем
        dsize = (int((1.0 + RESIZE_PERCENT) * point_original_w), int((1.0 + RESIZE_PERCENT) * point_original_h))
        point_enlarged = cv2.resize(point, dsize)
        point_rotated.append((
            point_number,
            angle * 90,
            point_enlarged.copy(), dsize[0], dsize[1],
            1.0+RESIZE_PERCENT))
        # удаляем скопированные объекты
        del point_enlarged
        del point_reduced
        del point
        del M

frame = map
# составляем все версии всех найденных правдопободных сравнений
versions = []
for (point_number, angle, point, point_w, point_h, resize) in point_rotated:
    result = cv2.matchTemplate(frame, point, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    # print(point_number, angle, min_val, max_val, min_loc, max_loc, resize)
    if max_val >= THRESHOLD:
        if max_loc:
            versions.append((
                point_number,
                result,
                min_val, max_val, min_loc, max_loc,
                angle, point_w, point_h, resize))
# если объекты найдены
if versions:
    for (point_number, _, min_val, max_val, min_loc, max_loc, angle, _, _, resize) in versions:
        print('version:', point_number, angle, min_val, max_val, min_loc, max_loc, resize)
    # составляем список правдоподобных точек, в которых мы находимся
    point_numbers = set([v[0] for v in versions])
    # сортируем список в порядке уменьшения правдоподобности
    print('points:', point_numbers, [(x[0],x[3]) for x in versions])
    versions.sort(key=lambda x: x[3], reverse=True)
    print('points:', point_numbers, [(x[0],x[3]) for x in versions], 'best:', versions[0][0])
    # перебираем все правдоподобные точки
    for point_number in point_numbers:
        # берём первый наиболее правдоподобный элемент в отсортированном списке
        # (хотя можно перебрать их все)
        # Внимание! в этом списке м.б. несколько версий одной и той же точки (напр., после ресайза)
        (_,
         result,
         min_val, max_val, min_loc, max_loc,
         angle, point_w, point_h,
         resize) = next((v for v in versions if v[0] == point_number), None)
        # выводим результат
        (x, y) = max_loc
        cv2.rectangle(frame, (x, y), (x + point_w-1, y + point_h-1), (0, 0, 255), 5)
        cv2.rectangle(result, (x, y), (x + point_w-1, y + point_h-1), (255, 255, 255), 1)
        cv2.imshow("Point{}".format(point_number), result)
del versions

cv2.imshow("Pioneer View", frame)
cv2.resizeWindow("Pioneer View", 800, 600)
cv2.waitKey()

cv2.destroyAllWindows()
