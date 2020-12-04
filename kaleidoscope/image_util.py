import sys
import cv2
import numpy as np


def median_color(img):
    average_color_per_row = np.average(img, axis=0)
    return np.average(average_color_per_row, axis=0)


def rect_median_color(img, x, y, w, h):
    x = int(x)
    y = int(y)
    w = int(w)
    h = int(h)
    average_color_per_row = np.average(img[y: y + h, x: x + w], axis=0)
    return np.average(average_color_per_row, axis=0)


def get_dimension(img):
    """
    Return width, height of image
    """
    return img.shape[1], img.shape[0]


def get_ratio(img_width, img_height):
    return img_width/float(img_height)


def resize(img, width, height):
    return cv2.resize(img, (int(width), int(height)))


if __name__ == '__main__':
    # print median_color(sys.argv[1])
    print("")
    img = cv2.imread(sys.argv[1])
    print(rect_median_color(img, 0, 100, 0, 100))
