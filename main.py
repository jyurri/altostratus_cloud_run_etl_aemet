from datetime import datetime

from cloudops.logging.google import get_logger
from fastapi import FastAPI
from pydantic import BaseModel

from cloud_run_etl_template.config import get_config
from cloud_run_etl_template.connector import Connector
from cloud_run_etl_template.sink import DummySink
from cloud_run_etl_template.source import DummySource

logger = get_logger(__name__)

app = FastAPI()


def get_connector() -> Connector:
    config = get_config("./config.yaml")
    source = DummySource(config.source)
    sink = DummySink(config.sink)
    connector = Connector(config.connector, source, sink)
    return connector


class IncrementalLoadRequest(BaseModel):
    object_ids: list[str]


class BackfillRequest(BaseModel):
    object_ids: list[str]
    start_date: datetime
    end_date: datetime


@app.post("/incremental_load")
def process_object_ids(request: IncrementalLoadRequest):
    connector = get_connector()
    for object_id in request.object_ids:
        logger.info(f"Processing object: {object_id}")
        connector.incremental_load(object_id)


@app.post("/backfill")
def backfill(request: BackfillRequest):
    connector = get_connector()
    for object_id in request.object_ids:
        logger.info(f"Processing object: {object_id}")
        start_datetime = request.start_date
        end_datetime = request.end_date
        connector.extract_and_load_object(
            object_id,
            start_datetime,
            end_datetime,
        )
