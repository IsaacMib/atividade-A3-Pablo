FROM python:3.12

# Install packages needed to run your application (not build deps):
# We need to recreate the /usr/share/man/man{1..8} directories first because
# they were clobbered by a parent image.
RUN set -ex \
    && RUN_DEPS=" \
        libexpat1 \
        libjpeg62-turbo \
        libpcre3 \
        libpq5 \
        mime-support \
        postgresql-client \
        procps \
        zlib1g \
        gnupg \
    " \
    && seq 1 8 | xargs -I{} mkdir -p /usr/share/man/man{} \
    && apt-get update && apt-get install -y --no-install-recommends $RUN_DEPS \
    && rm -rf /var/lib/apt/lists/*

ADD requirements/ /requirements/
ENV VIRTUAL_ENV=/venv
ENV PATH=/venv/bin:$PATH
ENV PYTHONPATH=/wagtail/
ENV BUILD_DEPS=" \
    build-essential \
    curl \
    git \
    libexpat1-dev \
    libjpeg62-turbo-dev \
    libpcre3-dev \
    libpq-dev \
    zlib1g-dev "

RUN apt-get update && apt-get install -y --no-install-recommends $BUILD_DEPS \
    && python3.12 -m venv ${VIRTUAL_ENV} \
    && python3.12 -m pip install -U pip \
    && python3.12 -m pip install --no-cache-dir -r /requirements/production.txt \
    && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs

RUN mkdir -p /wagtail/
WORKDIR /wagtail/
ADD . /wagtail/
ENV PORT=8080
# ENV NODE_ENV=production
EXPOSE 8080

# TODO: ajustar o build do tailwind para versão 4.0.0

RUN ./manage.py tailwind install 

RUN ./manage.py tailwind build 

RUN node --version \
    && npm install -D webpack-cli terser-webpack-plugin \
    && npm install \
    && npm run build

RUN ./manage.py collectstatic --no-input

RUN apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false $BUILD_DEPS \
    && rm -rf /var/lib/apt/lists/*

# Add custom environment variables needed by Django or your settings file here:
ENV DJANGO_SETTINGS_MODULE=codatasite.settings.production
ENV DJANGO_DEBUG=off

# Call collectstatic with dummy environment variables:
RUN DATABASE_URL=postgres://none REDIS_URL=none python manage.py collectstatic --noinput

# make sure static files are writable by uWSGI process
RUN mkdir -p /wagtail/codatasite/media/images && mkdir -p /wagtail/codatasite/media/original_images && chown -R 1000:2000 /wagtail/codatasite/media

# mark the destination for images as a volume
# VOLUME ["/wagtail/codatasite/media/images/"]
# VOLUME /data/uploads

ENV DJANGO_STATIC_ROOT=/data/uploads/static
ENV DJANGO_MEDIA_ROOT=/data/uploads/media

RUN mkdir -p /data
RUN mkdir -p /data/uploads
RUN mkdir -p /data/uploads/media

# start uWSGI, using a wrapper script to allow us to easily add more commands to container startup:
ENTRYPOINT ["/wagtail/docker-entrypoint.sh"]

# Start uWSGI
CMD ["uwsgi", "/wagtail/etc/uwsgi.ini"]
