FROM python:3.10-slim 

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

ENV APP_HOME /app
WORKDIR ${APP_HOME}

RUN pip3 install poetry
RUN poetry config virtualenvs.create false

# add and install python requirements
COPY pyproject.toml ./
COPY poetry.lock ./
RUN poetry install --only main 

COPY . ./

EXPOSE $PORT

CMD exec poetry run gunicorn --bind 0.0.0.0:$PORT --workers 1 --worker-class uvicorn.workers.UvicornWorker --threads 8 --timeout 0 main:app
