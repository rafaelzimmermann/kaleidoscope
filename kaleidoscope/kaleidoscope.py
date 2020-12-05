import hashlib
import os
from typing import List

import cv2
import numpy as np
from pathlib import Path
from progressbar import ProgressBar
from image_util import rect_median_color, dominant_color, resize, get_dimension, get_ratio

CHECKPOINT = '/images/checkpoint'
INPUT_DIR = '/images'
INPUT_FILE = '/images/IMG_5961.JPG'
BUF_SIZE = 65536


class FileInfo:
    def __init__(self, path: str, median_rgb: int, hashcode: str):
        self.path = path
        self.median_rgb = median_rgb
        self.hashcode = hashcode

    def __str__(self):
        return f'{self.path};{self.median_rgb};{self.hashcode}'

    def __repr__(self):
        return str(self)

    @staticmethod
    def from_str(value: str):
        parts = value.split(';')
        return FileInfo(parts[0], int(parts[1]), parts[2])


def get_hash(file: str) -> str:
    md5 = hashlib.md5()
    with open(file, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            md5.update(data)
    return "{0}".format(md5.hexdigest())


def load_files_rgb(path, img_list, current_files_info: List[FileInfo]) -> List[FileInfo]:
    print("loading file info")
    files_rgb = []
    files_hash_code = {}
    path_processed = {}
    for file_info in current_files_info:
        files_rgb.append(file_info)
        files_hash_code[file_info.hashcode] = True
        path_processed[file_info.path] = True
    pbar = ProgressBar()
    with open(CHECKPOINT, 'w+') as checkpoint:
        for img_path in pbar(img_list):
            if img_path in path_processed:
                continue
            hash_code = get_hash(img_path)
            if hash_code in files_hash_code:
                continue
            files_hash_code[hash_code] = True
            img_path = os.path.join(path, img_path.strip())
            img = cv2.imread(img_path)
            x = img.shape[1]
            y = img.shape[0]
            if x > y:
                rgb = dominant_color(img)
                file_info = FileInfo(img_path, get_int_from_rgb(rgb), hash_code)
                files_rgb.append(file_info)
                checkpoint.write(str(file_info))
                checkpoint.write('\n')
            del img
    print("")
    return files_rgb


def get_int_from_rgb(rgb):
    red = rgb[0].astype(np.int64)
    green = rgb[1].astype(np.int64)
    blue = rgb[2].astype(np.int64)
    rgb_int = (red << 16) + (green << 8) + blue
    return rgb_int


def find_best_fit(rgb, files_rgb: List[FileInfo]) -> str:
    current = None
    for file_rgb in files_rgb:
        current = file_rgb
        if file_rgb.median_rgb >= rgb:
            break
    files_rgb.remove(current)
    return current.path


def calc_thumb_height_count(thumb_width, thumb_height, thumb_width_count, img_target_width, img_target_height):
    mosaic_width = thumb_width * thumb_width_count
    mosaic_height = (mosaic_width * img_target_height) / img_target_width
    return int(mosaic_height / thumb_height)


def create_mosaic_lines(files_rgb: List[FileInfo], img_target, thumb_width, thumb_height, thumb_width_count,
                        thumb_height_count, img_part_width, img_part_height):
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


def create_mosaic(img_path, files_rgb: List[FileInfo], thumb_width, thumb_width_count):
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
    print("Listing files:")
    for file_path in Path(path).rglob('*.jpg'):
        _f = str(file_path)
        result.append(_f)
    return result


def create_checkpoint(files_rgb: List[FileInfo]):
    print("creating checkpoint")
    with open(CHECKPOINT, 'w+') as checkpoint:
        for file_info in files_rgb:
            checkpoint.write(str(file_info))
            checkpoint.write('\n')


def load_checkpoint():
    files_rgb = []
    if os.path.isfile(CHECKPOINT):
        with open(CHECKPOINT, 'r') as checkpoint:
            for line in checkpoint:
                files_rgb.append(FileInfo.from_str(line))
    return files_rgb


def main():
    files_rgb = load_checkpoint()
    print(len(files_rgb))
    if len(files_rgb) == 0:
        print("No checkpoint found")
    files = get_files('/images')
    print("files listed")
    files_info = load_files_rgb('/images', files, files_rgb)
    print("")
    print("sorting by color")
    files_rgb = sorted(files_info, key=lambda x: x.median_rgb)
    create_mosaic(INPUT_FILE, files_rgb, 100, 70)


if __name__ == '__main__':
    main()
