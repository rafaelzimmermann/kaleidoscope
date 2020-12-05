

.PHONY: build
build:
	docker build . -t kaleidoscope:latest

.PHONY: run
run: build
	docker run -v $(PWD)/images:/images kaleidoscope:latest