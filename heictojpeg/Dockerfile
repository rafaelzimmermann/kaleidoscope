FROM ubuntu:bionic

RUN apt-get update
RUN apt-get install -y libheif-examples

RUN mkdir /images
WORKDIR /images

ADD . /app

RUN chmod +x /app/convert.sh

CMD [ "/app/convert.sh" ]