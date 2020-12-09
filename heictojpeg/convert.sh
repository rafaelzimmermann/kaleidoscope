#!/bin/bash

set -x

files=$(ls *.{HEIC,heic})

for f in $files
do
  heif-convert $f $f.jpg
done