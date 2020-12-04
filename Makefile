

.PHONY: build
build:
	docker build . -t kaleidoscope:latest

.PHONY: run
run: build
	docker run -v /Volumes/Kaleidoscope/Fotos:/images kaleidoscope:latest