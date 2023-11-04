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
