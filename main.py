# функции с работой камеры дрона в ВM
import time

import cv2
from functions import vision

def start():
    capture = cv2.VideoCapture(0)

    capture.set(4, 640)  # x
    capture.set(3, 480)  # y

    # vision.test()

    # sourse1 = cv2.imread("/home/galina/Workspace/распознавание картинок/big.png")
    # object1 = cv2.imread("/home/galina/Workspace/распознавание картинок/small.png")
    # vision.image_concare1(sourse1, object1)
    # vision.image_concare2(sourse1, object1)

    # vision.set_threshold_values(capture)
    # vision.set_bright_conrtast_image(capture)

    while True:
        success, source = capture.read()
        # xy - точка отсчета, x1y1 - точка конца
        extracted = vision.extract_image(source, 0, 0, 600, 400)
        # xy = до скольки пикселей уменьшаем
        resized = vision.resize_image(source, 200, 400)
        changed_image = vision.change_color_space(source, cv2.COLOR_BGR2HSV)
        blur = vision.blur_image(source, 20, 20)
        binary = vision.binary_image(source, (127, 127, 127),  (255, 255, 255))

        cv2.imshow('binary', binary)
        cv2.imshow('blur', blur)
        cv2.imshow('extracted', extracted)
        cv2.imshow('resized', resized)
        cv2.imshow('changed_image', changed_image)
        # cv2.imshow('object1', object1)
        # cv2.imshow('source1', sourse1)
        cv2.imshow('source', source)


        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    capture.release()
    cv2.destroyAllWindows()



if __name__ == '__main__':
    start()
