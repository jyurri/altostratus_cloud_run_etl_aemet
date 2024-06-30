from datetime import datetime
from flask import Flask, request, jsonify
from cloudops.logging.google import get_logger
from cloud_run_elt.config import get_config
from cloud_run_elt.connector import Connector
from cloud_run_elt.sink import Sink
from cloud_run_elt.source import ApiSource
import os

logger = get_logger(__name__)

app = Flask(__name__)

def get_connector() -> Connector:
    config = get_config("./config.yaml")
    source = ApiSource(config.source)
    sink = Sink(config.sink)
    connector = Connector(config.connector, source, sink)
    return connector



@app.route("/load_data", methods=["POST"])
def load_missing_data():
    rows_added = 0
    try:
        connector = get_connector()
        rows_added = connector.load_missing_data()
        if rows_added == 0:
            return jsonify({"status": "No new rows added."}), 202
        return jsonify({"status": f"{rows_added} rows added."})
    except Exception as e:
        logger.error(f"Error during load_missing_data load: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
