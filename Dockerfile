# pull official base image
FROM python:3.10-slim-buster as requirements

# set environment variables
    # python
ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONDONTWRITEBYTECODE=1 \
  PYTHONHASHSEED=random \
  # pip
  PIP_ROOT_USER_ACTION=ignore \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100

COPY requirements.txt ./

RUN apt-get update && apt-get -y upgrade && \
    apt-get update \
    && apt-get -y install libpq-dev gcc git \
    && pip install --upgrade pip \
    && pip install --prefix=/req --force-reinstall -r requirements.txt

FROM python:3.10-slim-buster as build-image

COPY --from=requirements /req /usr/local

# add user
RUN groupadd user && adduser --disabled-password --no-create-home user --ingroup user

# set work directory
WORKDIR /usr/src/app

# chown all the files to the app user
RUN chown -R user:user /usr/src/app && chmod -R 755 /usr/src/app

# system update & cleaning cache:
RUN apt-get update && apt-get -y upgrade && apt-get install -y --no-install-recommends libpq-dev netcat \
    && apt-get autoremove -y && apt-get clean -y && rm -rf /var/lib/apt/lists/*

# copy project
COPY project .
COPY docker/script/docker-entrypoint.sh /

# switch to non-root user
USER user
