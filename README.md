# Cloud Run ETL from the AEMET API

App that cheks the data from a bigquery raw dat; gets the missing dates and load those dates from the AEMET API.
It has a post endpoint to load the data: load_missing_data; and a get healt endpoint.

There is a config.yaml file to configure your API.

## Run locally

```bash
docker compose up --build
```

## Setup Google Cloud Infrastructure

1. Modify `deploy_utils.bash` to set the environment variables.
2. Source the file: `source deploy_utils.bash`.
3. Run `setup_gcp` to set up the necessary infrastructure.

## Deploy service

You have two options:

1. Run `deploy` (recommended).
2. Run `deploy_local` and build the docker image locally instead of GCP (faster).

## Set up development environment

Install dependencies in a virtual environment:

```bash
poetry install
```

Start a shell in the virtual environment:

```bash
poetry shell
```
