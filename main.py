from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from cloudops.logging.google import get_logger


from cloud_run_elt.config import get_config
from cloud_run_elt.connector import Connector
from cloud_run_elt.sink import Sink
from cloud_run_elt.source import ApiSource

logger = get_logger(__name__)

app = FastAPI()

def get_connector() -> Connector:
    config = get_config("./config.yaml")
    source = ApiSource(config.source)
    sink = Sink(config.sink)
    connector = Connector(config.connector, source, sink)
    return connector

class LoadDataRequest(BaseModel):
    pass


@app.post("/load_missing_data")
def load_missing_data(request: LoadDataRequest):
    rows_added = 0
    try:
        connector = get_connector()
        rows_added = connector.load_missing_data()
        if rows_added == 0:
            return JSONResponse(status_code=202, content={"status": "No new rows added1."})
        return {"status": f"{rows_added} rows added."}
    except Exception as e:
        logger.error(f"Error during load_missing_data load: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health():
    return {"status": "ok"}



