#!/usr/bin/env bash
LOCATION=europe-west1
SERVICE_NAME=etl-service
PROJECT_ID='lineage-alt-test'
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='get(projectNumber)')
REPOSITORY_NAME="docker-repository"
ROOT_PATH="${LOCATION}-docker.pkg.dev"
IMAGE_NAME="${SERVICE_NAME}"
IMAGE_FULL_PATH="${ROOT_PATH}/${PROJECT_ID}/${REPOSITORY_NAME}/${IMAGE_NAME}"
SERVICE_ACCOUNT=etl-service-account
SCHEDULER_SERVICE_ACCOUNT=scheduler-service-account
PORT=5000   
PUBSUB_TOPIC=etl-topic
PUBSUB_SUBSCRIPTION=etl-subscription


# Infra

function setup_project(){
    echo "Setting up project to ${PROJECT_ID}..."
    gcloud config set project ${PROJECT_ID}

    echo "Setting up location to ${LOCATION}..."
    gcloud config set run/region ${LOCATION}
}

function setup_docker_auth(){
    echo "Setting up docker auth..."
    gcloud auth configure-docker gcr.io
    gcloud auth configure-docker ${ROOT_PATH}
}

function create_artifact_repository(){
    echo "Creating artifact repository ${REPOSITORY_NAME}..."
    gcloud artifacts repositories create ${REPOSITORY_NAME} \
        --repository-format=docker \
        --location=${LOCATION} \
        --project=${PROJECT_ID}
}

function create_etl_service_account(){
    echo "Creating service account ${SERVICE_ACCOUNT}..."
    gcloud iam service-accounts create ${SERVICE_ACCOUNT} \
        --display-name="ETL Service Account" \
        --project=${PROJECT_ID}

    echo "Adding permissions to service account ${SERVICE_ACCOUNT}..."
    gcloud projects add-iam-policy-binding ${PROJECT_ID} \
        --member serviceAccount:${SERVICE_ACCOUNT}@${PROJECT_ID}.iam.gserviceaccount.com \
        --role roles/bigquery.admin

    gcloud projects add-iam-policy-binding ${PROJECT_ID} \
        --member serviceAccount:${SERVICE_ACCOUNT}@${PROJECT_ID}.iam.gserviceaccount.com \
        --role roles/secretmanager.admin

    gcloud projects add-iam-policy-binding ${PROJECT_ID} \
        --member serviceAccount:${SERVICE_ACCOUNT}@${PROJECT_ID}.iam.gserviceaccount.com \
        --role roles/pubsub.publisher

    gcloud projects add-iam-policy-binding ${PROJECT_ID} \
        --member serviceAccount:${SERVICE_ACCOUNT}@${PROJECT_ID}.iam.gserviceaccount.com \
        --role roles/pubsub.subscriber

    gcloud projects add-iam-policy-binding ${PROJECT_ID} \
        --member serviceAccount:${SERVICE_ACCOUNT}@${PROJECT_ID}.iam.gserviceaccount.com \
        --role roles/errorreporting.writer
}

function setup_scheduler_service_account(){
    echo "Setting up scheduler"

    gcloud services enable cloudscheduler.googleapis.com

    gcloud iam service-accounts create ${SCHEDULER_SERVICE_ACCOUNT} \
       --display-name "Scheduler Service Account" \
       --project=${PROJECT_ID}

    # Give cloud run invoker role to the scheduler service account
    gcloud run services add-iam-policy-binding ${SERVICE_NAME} \
       --member serviceAccount:${SCHEDULER_SERVICE_ACCOUNT}@${PROJECT_ID}.iam.gserviceaccount.com \
       --role=roles/run.invoker
}

function create_scheduler(){
    echo "Creating cloud scheduler"

    gcloud scheduler jobs create http ${SERVICE_NAME}-job \
        --schedule "1 0 * * *" \
        --http-method=GET \
        --uri=${SERVICE_URL} \
        --oidc-service-account-email=${SCHEDULER_SERVICE_ACCOUNT}@${PROJECT_ID}.iam.gserviceaccount.com \
        --oidc-token-audience=${SERVICE_URL} \
        --location=${LOCATION}
}

function setup_pubsub(){
    echo "Setting up pubsub"
    gcloud pubsub topics create ${PUBSUB_TOPIC}

    echo "Allow Pub/Sub to create authentication tokens in your project"
    gcloud projects add-iam-policy-binding ${PROJECT_ID} \
        --member=serviceAccount:service-${PROJECT_NUMBER}@gcp-sa-pubsub.iam.gserviceaccount.com \
        --role=roles/iam.serviceAccountTokenCreator

    gcloud pubsub subscriptions create ${PUBSUB_SUBSCRIPTION}\
        --topic ${PUBSUB_TOPIC} \
        --push-endpoint=${SERVICE_URL} \
        --push-auth-service-account=${SCHEDULER_SERVICE_ACCOUNT}@${PROJECT_ID}.iam.gserviceaccount.com 
}


function setup_gcp(){
    setup_project
    setup_docker_auth
    create_artifact_repository
    create_etl_service_account
}

function docker_build_gcp(){
    echo "Building docker image on GCP"
    gcloud builds submit --tag ${IMAGE_FULL_PATH} .
    
}

function docker_build_local(){
    echo "Building docker image locally"
    docker image build -t ${SERVICE_NAME} .

    echo "Deploying docker image to ${IMAGE_FULL_PATH}"
    docker tag "${SERVICE_NAME}:latest" "${IMAGE_FULL_PATH}:latest"
    docker push "${IMAGE_FULL_PATH}:latest"
    
}

function cloud_run_deploy(){
    echo "Deploying cloud run service"
    gcloud run deploy ${SERVICE_NAME} \
        --image ${IMAGE_FULL_PATH}:latest \
        --service-account ${SERVICE_ACCOUNT}@${PROJECT_ID}.iam.gserviceaccount.com \
        --region ${LOCATION} \
        --port ${PORT} \
        --no-allow-unauthenticated
    SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --format='value(status.address.url)')
}

function deploy(){
    docker_build_gcp
    cloud_run_deploy
}

function deploy_local(){
    docker_build_local
    cloud_run_deploy
}

function run_cloud_scheduler(){
    echo "Running cloud scheduler"
    gcloud scheduler jobs run ${SERVICE_NAME}-job
}
