import cv2
from cv2 import Mat

import sys
import numpy as np
import vlc
import time


def extract_image(source_mat: Mat, x, y, width, height):
    # обрезка изображения
    extracted = source_mat[x:width + x, y:height + y]
    return extracted


def resize_image(source_mat: Mat, width, height):
    # изменение размера изображения
    resize = cv2.resize(source_mat, (width, height))
    return resize


def change_color_space(source_mat: Mat, color):
    # Изменение цветного простанства с BGR
    changed_image = cv2.cvtColor(source_mat, color)
    return changed_image


def blur_image(source_mat: Mat, x, y):
    # Создание размытия изображения
    blur = cv2.blur(source_mat, (x, y))
    return blur


def bright_image(source_mat: Mat, contrast, bright):
    # Изменение яркости и экспозиции изображения
    bright_contrast = cv2.convertScaleAbs(source_mat, beta=bright, alpha=contrast)
    return bright_contrast



def binary_image(source_mat: Mat, min_v: tuple, max_v: tuple):
    # Переворматирование в изображение  с двоичной матрицей
    binary_images = cv2.inRange(source_mat, min_v, max_v)
    return binary_images


def count_pixel(binary_source: Mat):
    count = cv2.countNonZero(binary_source)
    return count


def trackbar_changed(value):
    pass



def mouse_cliked(event, x, y, flags, params):
    global source_mouse
    if event == cv2.EVENT_LBUTTONDOWN:
        B = source_mouse[y, x][0]
        G = source_mouse[y, x][1]
        R = source_mouse[y, x][2]
        B_min, G_min, R_min, B_max, G_max, R_max = B - 30, R - 30, G - 30, B + 30, R + 30, G + 30

        if B < 30:
            B_min = 0
        if G < 30:
           G_min = 0
        if R < 30:
            R_min = 0

        if B_max > 255:
            B_max = 255
        if G_max > 255:
            G_max = 255
        if R_max > 255:
            R_max = 255

        cv2.setTrackbarPos('Bmin', 'binary', B_min)
        cv2.setTrackbarPos('Gmin', 'binary', G_min)
        cv2.setTrackbarPos('Rmin', 'binary', R_min)
        cv2.setTrackbarPos('Bmax', 'binary', B_max)
        cv2.setTrackbarPos('Gmax', 'binary', G_max)
        cv2.setTrackbarPos('Rmax', 'binary', R_max)


def set_threshold_values(capture):
    global source_mouse

    success, source = capture.read()

    source_mouse = source
    cv2.imshow('binary', source)
    cv2.createTrackbar('Bmin', 'binary', 0, 255, trackbar_changed)
    cv2.createTrackbar('Gmin', 'binary', 0, 255, trackbar_changed)
    cv2.createTrackbar('Rmin', 'binary', 0, 255, trackbar_changed)
    cv2.createTrackbar('Bmax', 'binary', 0, 255, trackbar_changed)
    cv2.createTrackbar('Gmax', 'binary', 0, 255, trackbar_changed)
    cv2.createTrackbar('Rmax', 'binary', 0, 255, trackbar_changed)

    cv2.namedWindow('source')
    cv2.setMouseCallback('source', mouse_cliked)
    while True:
        success, source = capture.read()
        source_mouse = source

        Bmin = cv2.getTrackbarPos('Bmin', 'binary')
        Rmin = cv2.getTrackbarPos('Rmin', 'binary')
        Bmax = cv2.getTrackbarPos('Bmax', 'binary')
        Gmin = cv2.getTrackbarPos('Gmin', 'binary')
        Gmax = cv2.getTrackbarPos('Gmax', 'binary')
        Rmax = cv2.getTrackbarPos('Rmax', 'binary')

        binary = binary_image(source, (Bmin, Gmin, Rmin),  (Bmax, Gmax, Rmax))
        mask = cv2.bitwise_and(source, source, mask=binary)

        cv2.imshow('mask', mask)
        cv2.imshow('source', source)
        cv2.imshow('binary', binary)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


def set_bright_conrtast_image(capture):
    success, source = capture.read()

    cv2.imshow('bright_contrast_image', source)
    cv2.createTrackbar('bright', 'bright_contrast_image', 0, 255, trackbar_changed)
    cv2.createTrackbar('contrast', 'bright_contrast_image', 0, 255, trackbar_changed)

    while True:
        success, source = capture.read()

        bright = cv2.getTrackbarPos('bright', 'bright_contrast_image')
        contrast = cv2.getTrackbarPos('contrast', 'bright_contrast_image')


        bright_contrast = bright_image(source, bright, contrast)

        cv2.imshow('source', source)
        cv2.imshow('bright_contrast_image', bright_contrast)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break



def image_concare1(sourse, object1):
    result = cv2.matchTemplate(sourse, object1, cv2.TM_SQDIFF)

    y, x = np.unravel_index(np.argsort(result.reshape(-1,)),
            result.shape)
    coords = np.column_stack((x[:2], y[:2]))
    print(coords)


def image_concare2(sourse, object1):
    result = cv2.matchTemplate(sourse, object1, cv2.TM_SQDIFF)

    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    print(min_val, max_val, min_loc, max_loc)

    # Рисуем выделение
    x, y = min_loc

    trows, tcols = object1.shape[:2]

    cv2.rectangle(sourse, (x, y), (x + tcols, y + trows), (0, 0, 255), 2)

    cv2.imshow('source', sourse)

    cv2.waitKey(0)


def test():
    file = "/home/galina/Workspace/распознавание картинок/video.mp4"  # путь к файлу с картинкой
    percent = 20
    cap = cv2.VideoCapture(file)
    player = vlc.MediaPlayer(file)
    player.play()
    while (cap.isOpened()):
        ret, frame = cap.read()
        width = int(frame.shape[1] * percent / 1)
        height = int(frame.shape[0] * percent / 1)
        dim = (width, height)
        frame_re = cv2.resize(frame, dim)
        cv2.imshow('frame', frame_re)
        time.sleep(1)
        player.video_take_snapshot(0, '.snapshot.tmp.png', 0, 0)
        if cv2.waitKey(33) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
