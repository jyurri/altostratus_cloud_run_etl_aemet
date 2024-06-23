# Cloud Run ETL Template

Everything you need to set up a Cloud Run service that runs an ETL job on a schedule.

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
