# to build copy and paste
# docker build -f .\.devcontainer\app\test.Dockerfile --build-arg requirements_file=test.pip -t hub.docker.com/elmcrest/systori:test .
# docker push hub.docker.com/elmcrest/systori:test
FROM docker.pkg.github.com/systori/systori/base:latest

ARG requirements_file

# Avoid warnings by switching to noninteractive
ENV DEBIAN_FRONTEND=noninteractive

COPY ./ /app
WORKDIR /app

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
    fonts-liberation \
    libappindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libnspr4 \
    libnss3 \
    lsb-release \
    xdg-utils \
    libxss1 \
    libdbus-glib-1-2 \
    curl \
    unzip \
    wget \
    ssh \
    postgresql-client-11 \
    xvfb \
    x11-utils \
    && GECKODRIVER_VERSION=`curl https://github.com/mozilla/geckodriver/releases/latest | grep -Po 'v[0-9]+.[0-9]+.[0-9]+'` \
    FIREFOX_SETUP=firefox-setup.tar.bz2 \
    && wget https://github.com/mozilla/geckodriver/releases/download/$GECKODRIVER_VERSION/geckodriver-$GECKODRIVER_VERSION-linux64.tar.gz \
    && tar -zxf geckodriver-$GECKODRIVER_VERSION-linux64.tar.gz -C /usr/local/bin \
    && chmod +x /usr/local/bin/geckodriver \
    && rm geckodriver-$GECKODRIVER_VERSION-linux64.tar.gz \
    && wget -O $FIREFOX_SETUP "https://download.mozilla.org/?product=firefox-latest&os=linux64" \
    && tar xjf $FIREFOX_SETUP -C /opt/ \
    && ln -s /opt/firefox/firefox /usr/bin/firefox \
    && rm $FIREFOX_SETUP \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* \
    && python3 -m pip install --disable-pip-version-check --no-cache-dir -r requirements/$requirements_file

# Switch back to dialog for any ad-hoc use of apt-get
ENV DEBIAN_FRONTEND=
