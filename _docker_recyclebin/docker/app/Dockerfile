FROM ubuntu:18.04

ARG RLEXTRA_ACCESS_TOKEN

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
        libxslt-dev && \
    rm -rf /var/lib/apt/lists/*

RUN locale-gen de_DE.UTF-8 && locale-gen en_US.UTF-8

RUN mkdir /root/.ssh/
RUN touch /root/.ssh/known_hosts
RUN ssh-keyscan github.com >> /root/.ssh/known_hosts

RUN git clone https://elmcrest:$RLEXTRA_ACCESS_TOKEN@github.com/systori/rlextra.git

RUN pip3 install --upgrade pip
COPY ./requirements/docker.pip /docker.pip
RUN pip3 install -r docker.pip

COPY ./ /app
WORKDIR /app
RUN pip3 install .

# RUN apt-get install wget

# WORKDIR /
#RUN wget -nv https://storage.googleapis.com/dart-archive/channels/stable/release/latest/linux_packages/dart_1.24.3-1_amd64.deb
#RUN dpkg -i dart_1.24.3-1_amd64.deb
# RUN wget -nv https://storage.googleapis.com/dart-archive/channels/stable/release/1.24.3/sdk/dartsdk-linux-x64-release.zip
# RUN unzip dartsdk-linux-x64-release.zip
# WORKDIR /app/systori/dart/
# RUN /dart-sdk/bin/pub get
# RUN /dart-sdk/bin/pub build
# WORKDIR /app

RUN python3 manage.py collectstatic --noinput
