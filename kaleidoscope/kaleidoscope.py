import os
import cv2
import math
import numpy as np
from image_color import rect_median_color, median_color

files_rgb = []

def load_files_rgb(img_list):
    for img_path in open(img_list):
        base = '/home/spike/workspace/kaleidoscope/kaleidoscope/imgs/'
        img_path = os.path.join(base,img_path.strip())
        img = cv2.imread(img_path)
        rgb = median_color(img)
        files_rgb.append((img_path, getIntFromRGB(rgb)))


def getIntFromRGB(rgb):
    red = rgb[0].astype(np.int64)
    green = rgb[1].astype(np.int64)
    blue = rgb[2].astype(np.int64)
    RGBint = (red<<16) + (green<<8) + blue
    return RGBint

def magic(img_path, p):
    img = cv2.imread(img_path)
    X = img.shape[1]
    Y = img.shape[0]
    r = X/float(Y)
    y = int(math.sqrt(p/float(r)))
    x = p/y
    print p, r, x, y
    xi = 0
    yi = 0
    while xi + x < X:
        print xi + x, X
        while yi + y < Y:
            # print xi, yi, x, y, X, Y
            print rect_median_color(img, xi, xi + x, yi, yi + y)
            yi += y
        xi += x
        yi = 0

def main():
    load_files_rgb('img_list_head.txt')
    print files_rgb
    sorted(files_rgb, key=lambda x: x[1])
    print files_rgb
    magic('test.jpg', 1000)

if __name__ == '__main__':
    main()
