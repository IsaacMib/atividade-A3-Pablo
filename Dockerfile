FROM python:3.12

# Install packages needed to run your application (not build deps):
RUN set -ex \
    && RUN_DEPS=" \
        libexpat1 \
        libjpeg62-turbo \
        libpcre2-32-0 \
        libpq5 \
        media-types \
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
    libpcre2-dev \
    libpq-dev \
    zlib1g-dev \
"

RUN apt-get update && apt-get install -y --no-install-recommends $BUILD_DEPS \
    && apt-get install -y locales \
    && sed -i '/pt_BR.UTF-8/s/^# //g' /etc/locale.gen \
    && locale-gen pt_BR.UTF-8 \
    && python3.12 -m venv ${VIRTUAL_ENV} \
    && python3.12 -m pip install -U pip \
    && python3.12 -m pip install --no-cache-dir -r /requirements/production.txt \
    && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs

RUN mkdir -p /wagtail/
WORKDIR /wagtail/
ADD . /wagtail/
ENV PORT=8080
EXPOSE 8080

ENV LANG=pt_BR.UTF-8
ENV LANGUAGE=pt_BR:pt
ENV LC_ALL=pt_BR.UTF-8

RUN node --version \
    && npm install -D webpack-cli terser-webpack-plugin \
    && npm install \
    && npm run build

RUN ./manage.py collectstatic --no-input

RUN apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false $BUILD_DEPS \
    && rm -rf /var/lib/apt/lists/*

# Add custom environment variables needed by Django or your settings file here:
ENV DJANGO_SETTINGS_MODULE=sitepadrao.settings.production
ENV DJANGO_DEBUG=off

# Call collectstatic with dummy environment variables:
RUN DATABASE_URL=postgres://none REDIS_URL=none python manage.py collectstatic --noinput

# make sure static files are writable by uWSGI process
RUN mkdir -p /wagtail/sitepadrao/media/images \
    && mkdir -p /wagtail/sitepadrao/media/original_images \
    && chown -R 1000:2000 /wagtail/sitepadrao/media

ENV DJANGO_STATIC_ROOT=/data/uploads/static
ENV DJANGO_MEDIA_ROOT=/data/uploads/media

RUN mkdir -p /data/uploads/media

# start uWSGI, using a wrapper script to allow us to easily add more commands to container startup:
ENTRYPOINT ["/wagtail/docker-entrypoint.sh"]

# Start uWSGI
CMD ["uwsgi", "/wagtail/etc/uwsgi.ini"]
