FROM python:3.6-slim-buster

ARG requirements_file

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED 1

COPY ./requirements /requirements

## WAIT-TOOL FOR CHILD-CONTAINERS, USE IN DOCKER-COMPOSE
ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.6.0/wait /wait

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
    git \
    postgresql-server-dev-all \
    python3-psycopg2 \
    locales \
    gettext \
    build-essential \
    python3-lxml \
    libxml2-dev \
    libxslt-dev \
    dumb-init \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* \
    # && locale-gen en_US.UTF-8 de_DE.UTF-8 \
    && sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen \
    && sed -i -e 's/# de_DE.UTF-8 UTF-8/de_DE.UTF-8 UTF-8/' /etc/locale.gen \
    && locale-gen \
    && chmod +x /wait \
    && python3 -m pip install --disable-pip-version-check --no-cache-dir -r requirements/$requirements_file

ENV DEBIAN_FRONTEND=