FROM python:3.10-slim-buster

ENV PYTHONUNBUFFERED True
ENV APP_HOME /app
ENV FLASK_APP main.py 

WORKDIR $APP_HOME

RUN pip install --no-cache-dir poetry

RUN poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock ./

RUN poetry install --only main

COPY data-altostratus-challenge_key.json ./service-account-file.json

ENV GOOGLE_APPLICATION_CREDENTIALS="$APP_HOME/service-account-file.json"

COPY . .

ARG PORT=5000
EXPOSE $PORT

CMD ["poetry", "run", "flask", "run", "--host=0.0.0.0", "--port=5000"]
