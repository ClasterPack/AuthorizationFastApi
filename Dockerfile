FROM python:3.12-alpine

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/usr/src/app

COPY requirements.txt requirements.txt
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh

RUN apk add --no-cache netcat-openbsd \
    && mkdir -p /usr/src/app/logs/booking \
    && chmod -R 777 /usr/src/app/logs

RUN chmod +x /usr/local/bin/docker-entrypoint.sh

RUN pip install --upgrade pip --no-cache-dir \
    && pip install -r requirements.txt --no-cache-dir

COPY .. .