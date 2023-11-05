# Эксперименты с RTSP

## Подготовка

Ищем в Google 'public RTSP stream camera'. Находим например такой вариант: http://158.58.130.148/mjpg/video.mjpg Проверяем в браузере, что поток идёт. Желательно, чтобы в видео потоке были различные фрагменты, раскиданные по экрану (например кресла в гостинице, источники освещения и т.п. для ориентации... видео с пляжа без ориентиров не подойдёт).

Устанавливаем программу специализирующуюся на проигрывании видео в различных форматах:

```bash
sudo apt install vlc
```

Открываем меню Медиа | "Открыть URL..." | вставляем найденную ссылку.

Проверяем, что ~~rtsp модуль~~ opencv для python установлен:

```bash
python3
>>> import cv2
>>> Ctrl+D

# sudo apt install python3-opencv
```

Если ошибки нет, то продолжаем, если появилась ошибка, то устанавливаем модуль (см. последнюю строку).

Далее проверяем, что поддержка ffmpeg имеется в opencv, потому как на некоторых платформах это может быть и не так. Выполняем команду:

```bash
python3 -c "import cv2; print(cv2.getBuildInformation())"
```

И ищем строку `FFMPEG: YES`. Если написано `NO`, то на этом этапе можно заканчивать... или искать другой способ работы с rtsp потоком.

Теперь проверяем, что rtsp-поток идёт и воспроизводится с помощью python-а:

```python
#!/bin/python3
import cv2
vcap = cv2.VideoCapture("http://158.58.130.148/mjpg/video.mjpg")

while (1):
  ret, frame = vcap.read()
  cv2.imshow('VIDEO', frame)
  cv2.waitKey(1)

exit(0)
```

После запуска на экране должно появиться окно с видео потоком, если да, то всё в порядке, продолжаем.

Примечание: в письме от Геоскан-а упоминается неактуальная ссылка на документацию. Вот тут можно узнать технические характеристики по дрону Пионер: https://www.geoscan.ru/ru/products/pioneer/copter Но в документации по программированию упоминается не Python, а Lua... так что из полезных сведений остаётся ознакомиться только с комплектацией дрона (похож на Клевер).

Также конвертируем набор картинок в видео-файл:

```bash
sudo apt install rename
rename 's|image_|image_00|' image_?.jpg  # image_x.jpg -> image_00x.jpg
rename 's|image_|image_0|' image_??.jpg  # image_xx.jpg -> image_0xx.jpg
rename 's|image_|image_0|' image_???.jpg  # image_xxx.jpg -> image_0xxx.jpg

ffmpeg -f image2 -framerate 3 -i image_%04d.jpg -s 1280x720 video_3fps.avi
ffmpeg -f image2 -framerate 6 -i image_%04d.jpg -s 1280x720 video_6fps.avi
# сформируются 2 видео-файла с разной скоростью воспроизведения (3 и 6 кадров/сек)

# проверить воспроизведение:
vlc video_6fps.avi
```

Для трансляции видео файла в режиме тестового rstp-потока (и тренировке программированию "в условиях приближенных к реальным"), надо запустить сформированный поток в диска, для этого по ссылке https://github.com/prabhakar-sivanesan/OpenCV-rtsp-server/blob/master/stream.py копируем текст и сохраняем его в файл `rtsp-server.py`, а файл https://github.com/prabhakar-sivanesan/OpenCV-rtsp-server/blob/master/open_rtsp.py сохраняем в `rtsp-play.py`, предварительно поменяв строку с адресом на `rtsp://127.0.0.1:8554/stream6`:

```bash
# установка необходимых программ
sudo apt install libgirepository1.0-dev
sudo apt install gir1.2-gst-rtsp-server-1.0
sudo apt install libgstreamer1.0-0 gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly gstreamer1.0-libav gstreamer1.0-tools gstreamer1.0-x gstreamer1.0-alsa gstreamer1.0-gl gstreamer1.0-gtk3 gstreamer1.0-qt5 gstreamer1.0-pulseaudio
sudo apt install libglib2.0-dev libgstrtspserver-1.0-dev gstreamer1.0-rtsp

# запуск сервера
python3 rtsp-server.py --device_id video_6fps.avi --fps 6 --image_width 1280 --image_height 720 --port 8554 --stream_uri /stream6 &

# запуск проигрывания
python3 rtsp-play.py
```

Изредка сервер с rtsp-потоком падает/зависает, его можно убить вот так:

```bash
ps -e | grep "python" | sed 's|^ *||' | cut -d' ' -f1 | xargs kill
```

В результате будут убиты все python-ы, которые запустил пользователь

## Программирование

После пары-тройки часов экспериментов и упражнений с картинками, а также потоком из гостиницы и с транслированным видео с коптера был получен первый вариант алгоритма, в котором константами можно настроить поведение и входной поток:

### Поиск кресла по картинке

Кресло, участвующее в эксперименте:

Большая картинка:


<img src="https://raw.githubusercontent.com/Galina-Basargina/groscan_hacaton/main/imgs/hostel.png">

Фрагмент:
<img src="https://raw.githubusercontent.com/Galina-Basargina/groscan_hacaton/main/imgs/chair.png">

```python
map_color = cv2.imread("hostel.png")
map_grayscale = cv2.cvtColor(map_color, cv2.COLOR_BGR2GRAY)
point2 = cv2.imread("chair.png", cv2.IMREAD_GRAYSCALE)
#point2 = cv2.imread("chair-90.png")
point2_w, point2_h = point2.shape[::-1]

result = cv2.matchTemplate(map_grayscale, point2, cv2.TM_CCOEFF_NORMED)  # TM_CCOEFF_NORMED
print(result.shape)
min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
print(min_val, max_val, min_loc, max_loc)

# Рисуем выделение
(x, y) = max_loc
cv2.rectangle(map_grayscale, (x, y), (x+point2_w, y+point2_h), (0, 0, 255), 2)

#x, y = min_loc
#trows, tcols = point2.shape[:2]
#cv2.rectangle(map, (x, y), (x + tcols, y + trows), (0, 0, 255), 2)
cv2.imshow('source', map_grayscale)
cv2.imshow('result', result)
cv2.waitKey(0)
```

### Работа с потоком

```python
import cv2

GRAYSCALE_MODE = False
ROTATION_ANGLE = 0
HOSTEL_STREAM = False

cv2.namedWindow("Pioneer View", cv2.WINDOW_NORMAL)
cv2.namedWindow("Point1", cv2.WINDOW_NORMAL)

if HOSTEL_STREAM:
    rtsp_stream = cv2.VideoCapture("http://158.58.130.148/mjpg/video.mjpg")
    point1_original = cv2.imread("chair-90.png", cv2.IMREAD_GRAYSCALE if GRAYSCALE_MODE else cv2.IMREAD_COLOR)  # 0439.png
else:
    rtsp_stream = cv2.VideoCapture("rtsp://127.0.0.1:8554/stream6")
    point1_original = cv2.imread("0439.png", cv2.IMREAD_GRAYSCALE if GRAYSCALE_MODE else cv2.IMREAD_COLOR)  # 0439.png
point1_original_w, point1_original_h = (point1_original.shape[0], point1_original.shape[1])

if ROTATION_ANGLE != 0:
    center1_x, center1_y = (point1_original_w // 2, point1_original_h // 2)
    print(point1_original.shape, center1_x, center1_y)
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
```

Итоговый результат из гостиницы.

 * GRAYSCALE_MODE = False
 * ROTATION_ANGLE = 90
 * HOSTEL_STREAM = True

Фрагмент:
<img src="https://raw.githubusercontent.com/Galina-Basargina/groscan_hacaton/main/imgs/chair-90.png">

Результат: 
<img src="https://raw.githubusercontent.com/Galina-Basargina/groscan_hacaton/main/imgs/hostel_04112023.png" width="100%">

Итоговый результат из видео-потока с коптера.

 * GRAYSCALE_MODE = False
 * ROTATION_ANGLE = 0
 * HOSTEL_STREAM = False

Фрагмент:
<img src="https://raw.githubusercontent.com/Galina-Basargina/groscan_hacaton/main/imgs/0439.png">

Результат: 
<img src="https://raw.githubusercontent.com/Galina-Basargina/groscan_hacaton/main/imgs/haccaton_04112023.png" width="100%">

### Поворот изображений

```python
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
```

Фрагмент (остался тот же самый, повернутый на 90°):
<img src="https://raw.githubusercontent.com/Galina-Basargina/groscan_hacaton/main/imgs/chair-90.png">

Результат (каким-то образом мужчина не помешал обнаружению кресла): 
<img src="https://raw.githubusercontent.com/Galina-Basargina/groscan_hacaton/main/imgs/hostel_05112023-15.png" width="100%">

### Поиск максимального правдоподобия

В процессе исследований выяснилось несколько особенностей, о которых надо помнить:

 * в shape хранится сначала height, а потом width (на вход функций обычно подаётся в другом порядке)
 * ровно повернуть прямоугольник не получилось, т.к. при повороте от исходного центра картинка уезжает за край dst-изображения
 * mask в matchTemplate не работает в сложных методах (поддерживается DIFF, который нам не годится)
 * поэтому все искомые объекты решено сохранять в виде квадратов, иначе их автоматичекий поворот затруднён (а вырезать `4*5*3=60` изображений грустно)
 * искомый квадрат не должен оказываться за пределами видимого дроном изображения, т.е. в кадре должен находится квадрат/объект полностью
 * метод поиска ничего не знает об исходном изображении, поэтому в общем случае искомый объект пусть и неправдоподобный, но будет найден
 * result, который формируется matchTemplate методом уменьшен пропорционально искомой картинке

Чтобы оценить правдоподобность найденного объекта, можно посмотреть на результат функции `minMaxLoc`, например все повёрнутые на 90° варианты искомых фрагментов выдают такую правдоподобность:

```text
0 -0.38854897022247314 0.9999997615814209 (239, 230) (23, 32)
1 -0.3032950460910797 0.31734275817871094 (156, 192) (369, 0)
2 -0.3785737454891205 0.39756810665130615 (100, 74) (319, 187)
3 -0.28990480303764343 0.3153490126132965 (254, 4) (92, 181)
```

<img src="https://raw.githubusercontent.com/Galina-Basargina/groscan_hacaton/main/imgs/bear_05112023-18.png" width="100%">

### Поиск с поворотами

Вариант поиска с поворотами такой:

```python
import cv2
import numpy as np

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
    if max_loc:
        (x, y) = max_loc
        cv2.rectangle(frame, (x, y), (x + point1_w, y + point1_h), (0, 0, 255), 5)
    cv2.imshow("Point1 {}°".format(angle*90), result)
    print(angle, min_val, max_val, min_loc, max_loc)
cv2.imshow("Pioneer View", frame)
cv2.waitKey()

cv2.destroyAllWindows()
```

Таким образом, детектирование лучшего срабатывания выглядит так:

```python
min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
if max_val >= THRESHOLD:
    if max_loc:
        (x, y) = max_loc
        cv2.rectangle(frame, (x, y), (x + point1_w-1, y + point1_h-1), (0, 0, 255), 5)
        cv2.rectangle(result, (x, y), (x + point1_w-1, y + point1_h-1), (255, 255, 255), 1)
```
<img src="https://raw.githubusercontent.com/Galina-Basargina/groscan_hacaton/main/imgs/bear_05112023-19.png" width="100%">

### Поиск с измененными размерами шаблона

Подвес камеры дрона можно описать как равнобедренный треугольник, его свойства таковы, что при подъеме на 10% размер видимого узибражения тоже увеличится на 10%. Аналогично и для спуска.

Ниже приведены размеры видимых изображений для разных объективов при подвесе в 100 см (расчет см. [тут](https://ru.numberempire.com/isosceles_triangle_calculator.php)):

 * 120° объектив:
   * 311 см карта на высоте 90 см (-10%)
   * 346 см карта на высоте 100 см
   * 381 см карта на высоте 110 см (+10%)
 * 75° объектив:
   * 138 см карта на высоте 90 см (-10%)
   * 153 см карта на высоте 100 см
   * 168 см карта на высоте 110 см (+10%)
 
В реальных условиях камера качается, поэтому размеры изображения меняются в большую или меньшую сторону.

Поэтому в следующем эксперименте будем обрабатывать 13%-ное изменение шаблона.

```python
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
    # print(angle*90, 'wh', point1_w, point1_h, 'dsize', dsize, 'shape', point1.shape, 'center', center1_x, center1_y)
    # добавление повернутых изображений в список
    point1_rotated.append((angle*90, point1.copy(), point1_w, point1_h, 1.0))
    # теперь ресайзим изображения (уменьшаем)
    dsize = (int((1.0-RESIZE_PERCENT)*point1_original_w), int((1.0-RESIZE_PERCENT)*point1_original_h))
    point1_reduced = cv2.resize(point1, dsize)
    point1_rotated.append((angle*90, point1_reduced.copy(), dsize[0], dsize[1], 1.0-RESIZE_PERCENT))
    # увеличиваем
    dsize = (int((1.0 + RESIZE_PERCENT) * point1_original_w), int((1.0 + RESIZE_PERCENT) * point1_original_h))
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
```

Теперь выбран наиболее подходящий вариант:

<img src="https://raw.githubusercontent.com/Galina-Basargina/groscan_hacaton/main/imgs/bear_05112023-20.png" width="100%">

### Поиск нескольких фрагментов одновременно и выбор наиболее правдоподобных

Добавляем новый фрагмент, теперь при поиске их используется два:

<img src="https://raw.githubusercontent.com/Galina-Basargina/groscan_hacaton/main/imgs/bear-point1.png">
<img src="https://raw.githubusercontent.com/Galina-Basargina/groscan_hacaton/main/imgs/bear-point2.png">

```python
import cv2
import numpy as np

THRESHOLD = 0.80  # степень правдоподобности 80% и выше
RESIZE_PERCENT = 0.13

cv2.namedWindow("Pioneer View", cv2.WINDOW_NORMAL)
cv2.namedWindow("Point1", cv2.WINDOW_NORMAL)
cv2.namedWindow("Point2", cv2.WINDOW_NORMAL)

map = cv2.imread("imgs/bear-enlarged.png")
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
```

На экране появятся измерения правдоподобности:

```text
version: 1 0 -0.40340617299079895 0.8048402070999146 (423, 323) (42, 74) 1.0
version: 1 0 -0.3985312581062317 0.9430774450302124 (270, 263) (23, 29) 1.13
version: 2 0 -0.4041024446487427 0.907184898853302 (0, 82) (665, 294) 1.13
points: {1, 2} [(1, 0.8048402070999146), (1, 0.9430774450302124), (2, 0.907184898853302)]
points: {1, 2} [(1, 0.9430774450302124), (2, 0.907184898853302), (1, 0.8048402070999146)] best: 1
```

Результат:

<img src="https://raw.githubusercontent.com/Galina-Basargina/groscan_hacaton/main/imgs/bear_05112023-21.png" width="100%">
