FROM hub.docker.com/elmcrest/systori:base

ARG requirements_file
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED 1

COPY ./ /app
WORKDIR /app
RUN mv /app/.devcontainer/app/idle.sh / \
    && chmod +x /idle.sh \
    && python3 -m pip install --disable-pip-version-check --no-cache-dir -r requirements/$requirements_file

ENV DEBIAN_FRONTEND=