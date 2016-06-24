FROM damoti/base:latest

RUN apt-get update && apt-get install -y \
    curl \
    language-pack-de \
    libpq-dev \
    libjpeg-dev \
    libxml2-dev \
    libxslt-dev \
    unzip

RUN pip3 install fabric3 psycopg2 lxml

RUN mkdir -p /root/.ssh && \
    ssh-keyscan github.com >> /root/.ssh/known_hosts && \
    ssh-keyscan bitbucket.org >> /root/.ssh/known_hosts

COPY ./docker_dev/ssh /root/.ssh

COPY ./requirements/ /tmp/requirements
RUN pip3 install -r /tmp/requirements/dev.pip

WORKDIR /systori
COPY ./ /systori/
#RUN pip3 install -r ./requirements/dev.pip
