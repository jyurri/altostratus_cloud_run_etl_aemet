import os
from datetime import datetime
from cloud_run_elt.source import ApiSourceConfig, ApiSource
from cloud_run_elt.sink import SinkConfig, Sink

# Set up the configuration for the source
source_config_data = {
    "endpoint": "https://opendata.aemet.es/opendata/",
    "api_key": "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJqeXVycmlAZ21haWwuY29tIiwianRpIjoiYTI4ZTdlMGQtZTNhZC00NGU5LWJmYTAtNjRiNmRiZGQ4YzVlIiwiaXNzIjoiQUVNRVQiLCJpYXQiOjE3MTg5ODU5MTksInVzZXJJZCI6ImEyOGU3ZTBkLWUzYWQtNDRlOS1iZmEwLTY0YjZkYmRkOGM1ZSIsInJvbGUiOiIifQ.baJ5JyuPx3L2psYPJSqo_nM-kvxksePjsWXiNxNAlME"
}

source_config = ApiSourceConfig(**source_config_data)
source = ApiSource(config=source_config)

# Define the start and end datetimes for the data extraction
start_datetime = datetime(2024, 6, 15, 14, 45, 30)
end_datetime = datetime(2024, 6, 16, 14, 45, 30)

# Extract the data
df = source.extract_object(start_datetime=start_datetime, end_datetime=end_datetime)

# Set up the configuration for the sink
sink_config_data = {
    "project_id": "data-altostratus",
    "dataset_id": "aemet_weather_data",
    "table_name": "weather_raw_data",
    "timestamp_column": "fecha",
    "first_date_to_load": '2024-05-20'
}

sink_config = SinkConfig(**sink_config_data)
sink = Sink(config=sink_config)

# Load the data into BigQuery
#sink.load_object(df)

print(sink.get_missing_dates_from_raw_data())


# Print the last update datetime
print(f"Last update datetime: {sink.get_last_update_datetime()}")
