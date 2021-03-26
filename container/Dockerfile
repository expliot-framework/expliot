FROM python:3.8.8-alpine3.13
LABEL maintainer="Fabian Affolter <fabian@affolter-engineering.ch>"
LABEL version="0.9.7"
LABEL description="Expliot - Internet Of Things Security Testing and \
Exploitation Framework"

ENV LANG C.UTF-8

RUN apk add --no-cache \
        make \
        python3 \
        git \
        glib-dev \
        gcc \
        libstdc++ \
        g++ \
        python3-dev

RUN mkdir -p /usr/src/app

WORKDIR /usr/src/app

ADD . /usr/src/app

RUN python3 setup.py install

ENTRYPOINT expliot
