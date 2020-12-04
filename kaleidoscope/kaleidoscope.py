import os
import cv2
import numpy as np
from image_util import rect_median_color, median_color, resize, get_dimension, get_ratio
from os import listdir
from os.path import isfile, join
from pathlib import Path

CHECKPOINT = '/images/checkpoint'
INPUT_DIR = '/images'
INPUT_FILE = '/images/Arthur & Max/Arthur - Newborn Session/A&K_WITKOWSCY_DRICA-100.jpg'


def load_files_rgb(path, img_list):
    files_rgb = []
    for img_path in img_list:
        img_path = os.path.join(path, img_path.strip())
        img = cv2.imread(img_path)
        X = img.shape[1]
        Y = img.shape[0]
        if X > Y:
            rgb = median_color(img)
            files_rgb.append((img_path, get_int_from_rgb(rgb)))
    return files_rgb


def get_int_from_rgb(rgb):
    red = rgb[0].astype(np.int64)
    green = rgb[1].astype(np.int64)
    blue = rgb[2].astype(np.int64)
    rgb_int = (red << 16) + (green << 8) + blue
    return rgb_int


def find_best_fit(rgb, files_rgb):
    current = None
    for file_rgb in files_rgb:
        current = file_rgb
        if file_rgb[1] >= rgb:
            break
    files_rgb.remove(current)
    return current[0]


def calc_thumb_height_count(thumb_width, thumb_height, thumb_width_count, img_target_width, img_target_height):
    mosaic_width = thumb_width * thumb_width_count
    mosaic_height = (mosaic_width * img_target_height) / img_target_width
    return int(mosaic_height / thumb_height)


def create_mosaic_lines(files_rgb, img_target, thumb_width, thumb_height, thumb_width_count, thumb_height_count, img_part_width, img_part_height):
    lines = []
    for i in range(0, thumb_height_count - 1):
        line = None
        for j in range(0, thumb_width_count - 1):
            x = j * img_part_width
            y = i * img_part_height

            rect_rgb = get_int_from_rgb(rect_median_color(img_target, x, y, img_part_width, img_part_height))
            rect_best_fit = find_best_fit(rect_rgb, files_rgb)
            resized = resize(cv2.imread(rect_best_fit), thumb_width, thumb_height)
            if line is None:
                line = resized
            else:
                line = np.concatenate((line, resized), axis=1)
        lines.append(line)
    return lines


def save_mosaic(file_name, lines):
    final_img = None
    for line in lines:
        if final_img is None:
            final_img = line
        else:
            final_img = np.concatenate((final_img, line), axis=0)
    print('Saving')
    cv2.imwrite(file_name, final_img)


def create_mosaic(img_path, files_rgb, thumb_width, thumb_width_count):
    img_target = cv2.imread(img_path)
    img_target_width, img_target_height = get_dimension(img_target)

    ratio = get_ratio(img_target_width, img_target_height)
    thumb_height = thumb_width / 1.33

    thumb_height_count = calc_thumb_height_count(thumb_width, thumb_height, thumb_width_count, img_target_width, img_target_height)
    if len(files_rgb) < thumb_width_count * thumb_height_count:
        print('There is not enough pictures to build the mosaic.')

    print('It will use', str(thumb_width_count * thumb_height_count), 'pictures')

    img_part_width = img_target_width / thumb_width_count
    img_part_height = img_target_height / thumb_height_count
    lines = create_mosaic_lines(files_rgb, img_target, thumb_width, thumb_height, thumb_width_count, thumb_height_count, img_part_width, img_part_height)
    save_mosaic('/images/out.png', lines)


def get_files(path):
    result = []
    for file_path in Path(path).rglob('*.jpg'):
        result.append(str(file_path))
    return result


def create_checkpoint(files_rgb):
    with open(CHECKPOINT, 'w+') as checkpoint:
        for img_path, rgb in files_rgb:
            checkpoint.write(img_path + '^' + str(rgb))
            checkpoint.write('\n')


def load_checkpoint():
    files_rgb = []
    if os.path.isfile(CHECKPOINT):
        with open(CHECKPOINT, 'r') as checkpoint:
            for line in checkpoint:
                img_path, rgb = line.split('^')
                rgb = int(rgb)
                files_rgb.append((img_path, rgb))
    return files_rgb


def main():
    files_rgb = load_checkpoint()
    if len(files_rgb) == 0:
        files_rgb = sorted(load_files_rgb('/images', get_files('/images')), key=lambda x: x[1])
        create_checkpoint(files_rgb)
    else:
        print("CHECKPOINT LOADED")
    # magic('/images/IMG_3355.jpg', files_rgb, 4, 400)
    create_mosaic(INPUT_FILE, files_rgb, 100, 70)


if __name__ == '__main__':
    main()
