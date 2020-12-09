import os
import sys


def deduplicate(dir_path: str):
    hashcodes = {}
    with open(f'{dir_path}/hashcodes') as _f:
        for line in _f:
            parts = line.split(';')
            file_path = parts[0].replace('/images', dir_path)
            hashcode = parts[2]
            if hashcode in hashcodes:
                try:
                    os.remove(file_path)
                    print(f'Deleted: {file_path}')
                except FileNotFoundError:
                    print(f'Not found: {file_path}')
            else:
                hashcodes[hashcode] = file_path
    print('Done')


if __name__ == '__main__':
    deduplicate(sys.argv[1])
