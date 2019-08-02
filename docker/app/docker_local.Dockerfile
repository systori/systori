FROM ubuntu:18.04

ARG REQUIREMENTS_FILE
ARG DJANGO_SETTINGS_MODULE
ARG PUSHER_APP_ID
ARG PUSHER_KEY
ARG PUSHER_SECRET
ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y \
    locales \
    git \
    mercurial \
    python3-dev \
    python3-pip \
    python3-lxml \
    libxml2-dev \
    libxslt-dev \
    libpq-dev \ 
    dumb-init && \
    rm -rf /var/lib/apt/lists/*

RUN locale-gen de_DE.UTF-8 && locale-gen en_US.UTF-8

RUN mkdir /root/.ssh/
RUN touch /root/.ssh/known_hosts
RUN ssh-keyscan github.com >>/root/.ssh/known_hosts

COPY ./ /app
WORKDIR /app
COPY ./requirements/app.pip /app/requirements/app.pip
COPY ./requirements/base.pip /app/requirements/base.pip
COPY ./requirements/dev.pip /app/requirements/dev.pip
COPY ./requirements/docker.pip /app/requirements/docker.pip
COPY ./requirements/test.pip /app/requirements/test.pip
RUN pip3 install -r /app/requirements/dev.pip
RUN python3 manage.py collectstatic --noinput
