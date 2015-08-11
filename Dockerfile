FROM ubuntu:14.04
MAINTAINER Andrey Beletsky "andrey@vr2.net"
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE systori.settings.docker

RUN apt-get update
RUN apt-get install -y git python3-pip python-pip python-dev locales mercurial
RUN apt-get install -y postgresql-contrib postgresql-server-dev-all
RUN apt-get install -y python3-lxml python3-dev libyaml-dev

RUN mkdir /systori

RUN mkdir -p /root/.ssh
ADD ./docker/id_rsa /root/.ssh/id_rsa
RUN chmod 600 /root/.ssh/id_rsa
RUN ssh-keygen -t rsa -f /etc/ssh/ssh_host_rsa_key
RUN ssh-keygen -t dsa -f /etc/ssh/ssh_host_dsa_key
RUN ssh-keyscan github.com >> /root/.ssh/known_hosts
RUN ssh-keyscan bitbucket.org >> /root/.ssh/known_hosts

RUN locale-gen "en_US.UTF-8"
RUN locale-gen "de_DE.UTF-8"
RUN dpkg-reconfigure locales
ENV LANG en_US.UTF-8
ENV LC_ALL en_US.UTF-8

WORKDIR /systori/
ADD ./ /systori/
# RUN pip3 install --upgrade pip
RUN pip3 install -r ./requirements/dev.pip
RUN pip2 install Fabric
