import sys
import cv2
import numpy as np

def median_color(img):
    average_color_per_row = np.average(img, axis=0)
    return np.average(average_color_per_row, axis=0)

def rect_median_color(img, x0, x1, y0, y1):
    average_color_per_row = np.average(img[y0:y1, x0:x1], axis=0)
    return np.average(average_color_per_row, axis=0)

def resize(img, width, height):
    return cv2.resize(img, (100, 50)) 

if __name__ == '__main__':
    # print median_color(sys.argv[1])
    print ""
    img = cv2.imread(sys.argv[1])
    print rect_median_color(img, 0, 100, 0, 100)
