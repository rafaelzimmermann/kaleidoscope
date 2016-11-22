import os
import cv2
import math
import numpy as np
from image_color import rect_median_color, median_color, resize
from os import listdir
from os.path import isfile, join

def load_files_rgb(path, img_list):
    files_rgb = []
    for img_path in img_list:
        img_path = os.path.join(path, img_path.strip())
        if img_path == '/images/DSCF2282.JPG':
            continue
        img = cv2.imread(img_path)
        X = img.shape[1]
        Y = img.shape[0]
        print "X", X, "Y", Y
        if X > Y:
            rgb = median_color(img)
            files_rgb.append((img_path, getIntFromRGB(rgb)))
    return files_rgb


def getIntFromRGB(rgb):
    red = rgb[0].astype(np.int64)
    green = rgb[1].astype(np.int64)
    blue = rgb[2].astype(np.int64)
    RGBint = (red<<16) + (green<<8) + blue
    return RGBint

def find_best_fit(rgb, files_rgb):
    current = None
    for file_rgb in files_rgb:
        # print rgb, file_rgb
        current = file_rgb
        if file_rgb[1] >= rgb:
            break
    files_rgb.remove(current)
    print len(files_rgb)
    return current[0]

def create_mosaic(img_path, files_rgb, thumb_width, thumb_width_count):
    img_target = cv2.imread(img_path)
    img_target_width = img_target.shape[1]
    img_target_height = img_target.shape[0]

    ratio = img_target_width/float(img_target_height)
    thumb_height = thumb_width / ratio
    ratio = thumb_width / float(thumb_height)

    thumb_height_count = int(thumb_width_count / ratio)
    img_part_width = img_target_width / thumb_width_count
    img_part_height = img_target_height / thumb_height_count

    lines = []
    for i in range(0, thumb_width_count - 1):
        line = None
        for j in range(1, thumb_height_count):
            x = i * img_part_width
            y = j * img_part_height
            rect_rgb = getIntFromRGB(rect_median_color(img_target, x, x + img_part_width, y, y + img_part_height))
            rect_best_fit = find_best_fit(rect_rgb, files_rgb)
            resized = resize(cv2.imread(rect_best_fit), thumb_width, thumb_height)
            if line is None:
                line = resized
            else:
                line = np.concatenate((line, resized), axis=1)
        lines.append(line)
    final_img = None
    for line in lines:
        if final_img is None:
            final_img = line
        else:
            final_img = np.concatenate((final_img, line), axis=0)
    cv2.imwrite('/images/out.png', final_img)

def get_files(path):
    return [f for f in listdir(path) if isfile(join(path, f)) and f.upper().endswith("JPG")]

def main():
    files_rgb = sorted(load_files_rgb('/images', get_files('/images')), key=lambda x: x[1])
    print files_rgb
    # magic('/images/IMG_3355.jpg', files_rgb, 4, 400)
    create_mosaic('/images/IMG_3355.jpg', files_rgb, 400, 70)

if __name__ == '__main__':
    main()
