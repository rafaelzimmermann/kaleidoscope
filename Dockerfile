FROM lsiobase/ffmpeg:bin as binstage
FROM lsiobase/ubuntu:bionic
FROM jjanzic/docker-python3-opencv


WORKDIR /app

RUN mkdir /images
VOLUME /images

# COPY requirements.txt /app
#
# RUN pip3 install -r requirements.txt

ADD . /app

CMD [ "python3", "kaleidoscope/kaleidoscope.py" ]
