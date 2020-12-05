FROM lsiobase/ffmpeg:bin as binstage
FROM lsiobase/ubuntu:bionic
FROM jjanzic/docker-python3-opencv


WORKDIR /app

RUN mkdir /images
VOLUME /images

# COPY requirements.txt /app
#

ADD . /app

RUN pip3 install -r requirements.txt


CMD [ "python3", "kaleidoscope/kaleidoscope.py" ]
