from datetime import datetime

import cv2
import hashlib
import numpy as np
import multiprocessing
import os

from image_util import rect_median_color, dominant_color, resize, get_dimension, get_ratio
from pathlib import Path
from progressbar import ProgressBar
from typing import List

INPUT_DIR = '/images'
HASHCODE_CHECKPOINT = INPUT_DIR + '/hashcodes'
CHECKPOINT = INPUT_DIR + '/checkpoint'

BUF_SIZE = 65536
NUM_OF_THREADS = 10


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


def get_hash(file: str) -> FileInfo:
    md5 = hashlib.md5()
    with open(file, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            md5.update(data)
    return FileInfo(file, 0, "{0}".format(md5.hexdigest()))


def get_file_rgb(path, img_path, hash_code):
    if not os.path.isfile(img_path):
        print(img_path)
    img_path = os.path.join(path, img_path.strip())
    img = cv2.imread(img_path)
    x = img.shape[1]
    y = img.shape[0]
    if x > y:
        rgb = dominant_color(img)
        file_info = FileInfo(img_path, get_int_from_rgb(rgb), hash_code)
        return file_info


def load_files_hash(file_list: List[str]) -> List[FileInfo]:
    print("Loading checksum")
    print(f"cpu count {multiprocessing.cpu_count()}")

    if os.path.isfile(HASHCODE_CHECKPOINT):
        return load_checkpoint(HASHCODE_CHECKPOINT)
    pool = multiprocessing.Pool(multiprocessing.cpu_count())
    pbar = ProgressBar()
    results = []
    for _f in pbar(file_list):
        results.append(pool.apply_async(get_hash, (_f,)))
    result = []
    pbar = ProgressBar()
    with open(HASHCODE_CHECKPOINT, 'w+') as hashcode_checkpoint:
        for future in pbar(results):
            file_info = future.get()
            if file_info.hashcode:
                result.append(file_info)
                hashcode_checkpoint.write(str(file_info))
                hashcode_checkpoint.write('\n')
    return result


def load_files_rgb(path, img_list, current_files_info: List[FileInfo]) -> List[FileInfo]:
    print("loading file info")

    if os.path.isfile(CHECKPOINT):
        return load_checkpoint(CHECKPOINT)

    files_rgb = []
    files_hash_code = {}
    for file_info in current_files_info:
        files_rgb.append(file_info)
        files_hash_code[file_info.hashcode] = True

    partial_file_info = load_files_hash(img_list)

    results = []

    with open(CHECKPOINT, 'w+') as checkpoint:
        pbar = ProgressBar()
        for file_info in pbar(partial_file_info):
            if file_info.hashcode in files_hash_code:
                continue
            files_hash_code[file_info.hashcode] = True
            file_info = get_file_rgb(path, file_info.path, file_info.hashcode)
            if file_info and str(file_info):
                files_rgb.append(file_info)
                checkpoint.write(str(file_info))
                checkpoint.write('\n')
                results.append(file_info)
    print("")
    return results


def get_int_from_rgb(rgb):
    red = rgb[0].astype(np.int64)
    green = rgb[1].astype(np.int64)
    blue = rgb[2].astype(np.int64)
    rgb_int = (red << 16) + (green << 8) + blue
    return rgb_int


def find_best_fit(rgb, files_rgb: List[FileInfo]) -> str:
    low = 0
    high = len(files_rgb) - 1
    mid = 0
    while low <= high:
        mid = (high + low) // 2
        if files_rgb[mid].median_rgb < rgb:
            low = mid + 1
        elif files_rgb[mid].median_rgb > rgb:
            high = mid - 1
        else:
            return files_rgb.pop(mid).path
    return files_rgb.pop(mid).path


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
    save_mosaic(f'/images/out-{datetime.now().strftime("%Y%m%d%H%M%S")}.png', lines)


def get_files(path):
    result = []
    print("Listing files:")
    for file_path in Path(path).rglob('*.jpg'):
        result.append(str(file_path))
    for file_path in Path(path).rglob('*.jpeg'):
        result.append(str(file_path))
    for file_path in Path(path).rglob('*.JPG'):
        result.append(str(file_path))
    for file_path in Path(path).rglob('*.png'):
        result.append(str(file_path))
    return result


def load_checkpoint(path: str):
    files_rgb = []
    if os.path.isfile(path):
        with open(path, 'r') as checkpoint:
            for line in checkpoint:
                files_rgb.append(FileInfo.from_str(line))
    return files_rgb


def main(target_image: str):
    print(f"Target Image: {target_image}")
    if not target_image:
        return
    files_rgb = load_checkpoint(CHECKPOINT)
    print(len(files_rgb))
    if len(files_rgb) == 0:
        print("No checkpoint found")
    files = get_files('/images')
    print(f"{len(files)} images")
    files_info = load_files_rgb('/images', files, files_rgb)
    print("")
    print("sorting by color")
    files_rgb = sorted(files_info, key=lambda x: x.median_rgb)
    create_mosaic(f'{INPUT_DIR}/{target_image}', files_rgb, 100, 70)


if __name__ == '__main__':
    main(os.environ['TARGET_IMAGE'])
