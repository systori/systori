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
RUN ssh-keyscan github.com >> /root/.ssh/known_hosts

COPY ./ /app
WORKDIR /app
RUN pip3 install -r requirements/$REQUIREMENTS_FILE
RUN python3 manage.py collectstatic --noinput
