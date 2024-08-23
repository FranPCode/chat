FROM python:3.12.3-alpine3.20

RUN pip install --upgrade pip
RUN apk add --no-cache build-base libffi-dev postgresql-dev postgresql-client

RUN addgroup -S pythonapp && adduser -S -G pythonapp pythonapp
USER pythonapp

WORKDIR /app/

COPY --chown=pythonapp requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir

EXPOSE 8000

COPY --chown=pythonapp . .



