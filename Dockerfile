FROM python:3.12.3-alpine3.20

RUN pip install --upgrade pip && \
    apk add --no-cache \
    bash \
    chromium \
    chromium-chromedriver \
    postgresql-dev \
    build-base \
    libffi-dev \
    py3-cffi

ENV CHROME_BIN=/usr/bin/chromium-browser \
    CHROMEDRIVER_PATH=/usr/bin/chromedriver

WORKDIR /app/

COPY --chown=pythonapp requirements.txt .

RUN pip install -r requirements.txt --no-cache-dir

EXPOSE 8000

COPY --chown=pythonapp . .

