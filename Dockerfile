FROM apsl/thumbor

RUN mkdir /images

VOLUME /images

ADD kaleidoscope /usr/local/kaleidoscope
