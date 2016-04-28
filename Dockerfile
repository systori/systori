FROM ubuntu:16.04

RUN apt-key adv --fetch-keys http://dl.google.com/linux/linux_signing_key.pub && \
    echo 'deb http://storage.googleapis.com/download.dartlang.org/linux/debian stable main' \
    > /etc/apt/sources.list.d/dart.list

RUN apt-get update && apt-get install -y \
    curl \
    dart \
    git \
    language-pack-de \
    libpq-dev \
    libjpeg-dev \
    libxml2-dev \
    libxslt-dev \
    mercurial \
    python3 \
    python3-pip \
    unzip

RUN pip3 install fabric3 psycopg2 lxml

RUN mkdir -p /root/.ssh

ENV PATH /usr/lib/dart/bin:$PATH

WORKDIR /systori
