import logging
import pandas as pd
import pydantic
from datetime import datetime
from google.cloud import bigquery

class SinkConfig(pydantic.BaseModel):
    project_id: str
    dataset_id: str
    table_name: str
    timestamp_column: str
    first_date_to_load: str

class Sink:
    def __init__(self, config: SinkConfig):
        self.config = config
        self.client = bigquery.Client(project=self.config.project_id)

    def get_last_update_datetime(self) -> datetime:
        query = f"""
        SELECT MAX(CAST({self.config.timestamp_column} AS DATE)) AS last_update
        FROM {self.config.project_id}.{self.config.dataset_id}.{self.config.table_name}
        """
        query_job = self.client.query(query)
        result = query_job.result()
        for row in result:
            last_update = row['last_update']
            if last_update is not None:
                return datetime.combine(last_update, datetime.min.time())
        return datetime.strptime(self.config.first_date_to_load, "%Y-%m-%d")
    
    def get_missing_dates_from_raw_data(self) -> list:
        query = f"""
            WITH RECURSIVE date_series AS (
                SELECT DATE('{self.config.first_date_to_load}') AS date
                UNION ALL
                SELECT DATE_ADD(date, INTERVAL 1 DAY)
                FROM date_series
                WHERE DATE_ADD(date, INTERVAL 1 DAY) <= CURRENT_DATE()
            )
            SELECT date_series.date
            FROM date_series
            LEFT JOIN (
                SELECT DISTINCT CAST({self.config.timestamp_column} AS DATE) AS date
                FROM `{self.config.project_id}.{self.config.dataset_id}.{self.config.table_name}`
                WHERE CAST({self.config.timestamp_column} AS DATE) >= '{self.config.first_date_to_load}'
            ) existing_dates
            ON date_series.date = existing_dates.date
            WHERE existing_dates.date IS NULL
            ORDER BY date_series.date;
        """
        query_job = self.client.query(query)
        result = query_job.result()
        dates = [row['date'] for row in result]
        return dates

    def load_object(self, df: pd.DataFrame, ) -> int:
        table_id = f"{self.config.project_id}.{self.config.dataset_id}.{self.config.table_name}"
        job = self.client.load_table_from_dataframe(df, table_id)
        job.result()
        print(f"Loaded {job.output_rows} rows into {table_id}.")
        return job.output_rows

