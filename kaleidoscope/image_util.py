import cv2
import numpy as np


def dominant_color(img):
    pixels = np.float32(img.reshape(-1, 3))

    n_colors = 1
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, .1)
    flags = cv2.KMEANS_RANDOM_CENTERS

    _, labels, palette = cv2.kmeans(pixels, n_colors, None, criteria, 10, flags)
    _, counts = np.unique(labels, return_counts=True)

    indices = np.argsort(counts)[::-1]
    return np.uint8(palette[indices[0]])


def rect_median_color(img, x, y, w, h):
    x = int(x)
    y = int(y)
    w = int(w)
    h = int(h)
    return dominant_color(img[y: y + h, x: x + w])


def get_dimension(img):
    """
    Return width, height of image
    """
    return img.shape[1], img.shape[0]


def get_ratio(img_width, img_height):
    return img_width/float(img_height)


def resize(img, width, height):
    return cv2.resize(img, (int(width), int(height)))

