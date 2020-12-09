INPUT_DIR ?= "${PWD}/images"
TARGET_IMAGE ?= "input.jpg"

.PHONY: build
build:
	docker build . -t kaleidoscope:latest

.PHONY: run
run: build
	docker run -e TARGET_IMAGE=$(TARGET_IMAGE) -v $(INPUT_DIR):/images kaleidoscope:latest


.PHONY: convert-heic
convert-heic:
	docker build heictojpeg -t heictojpeg:latest
	docker run -v $(INPUT_DIR):/images heictojpeg:latest