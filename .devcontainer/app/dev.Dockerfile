FROM docker.pkg.github.com/systori/systori/dev_base:latest

ARG requirements_file
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED 1

COPY ./ /app
WORKDIR /app
RUN mv /app/.devcontainer/app/idle.sh / \
    && chmod +x /idle.sh \
    && python3 -m pip install --disable-pip-version-check --no-cache-dir -r requirements/$requirements_file \
    && apt-get update \
    && apt-get install --no-install-recommends -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

ENV DEBIAN_FRONTEND=