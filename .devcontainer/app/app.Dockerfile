FROM docker.pkg.github.com/systori/systori/base:latest

ARG requirements_file
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=systori.settings.common

COPY ./ /app
WORKDIR /app
RUN mv /app/.devcontainer/app/idle.sh / \
    && chmod +x /idle.sh \
    && python3 -m pip install --disable-pip-version-check --no-cache-dir -r requirements/$requirements_file \
    && python3 manage.py collectstatic --ignore=*.scss --noinput

ENV DEBIAN_FRONTEND=