FROM python:3.10-slim-buster

ENV PYTHONUNBUFFERED True
ENV APP_HOME /app
WORKDIR $APP_HOME

RUN pip install --no-cache-dir poetry

RUN poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-dev 

COPY data-altostratus-challenge-1689e3bfff2f.json ./service-account-file.json

ENV GOOGLE_APPLICATION_CREDENTIALS="$APP_HOME/service-account-file.json"

COPY . .

ARG PORT=8000
EXPOSE $PORT


CMD exec poetry run gunicorn --bind 0.0.0.0:$PORT --workers 1 --worker-class uvicorn.workers.UvicornWorker --threads 8 --timeout 0 main:app
