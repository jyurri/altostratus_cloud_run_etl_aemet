from datetime import datetime, timedelta
from typing import Protocol

import pandas as pd
import pydantic
from cloudops.logging.google import get_logger


class Source(Protocol):
    def extract_object(
        self,
        start_datetime: datetime,
        end_datetime: datetime,
    ) -> pd.DataFrame:
        ...


class Sink(Protocol):
    def get_last_update_datetime(self, object_id: str) -> datetime:
        ...
    def get_missing_dates_from_raw_data(self) -> list:
        ...
    def load_object(self, object_id: str, df: pd.DataFrame) -> int:
        ...


class ConnectorConfig(pydantic.BaseModel):
    max_delta_time_hours: int


class Connector:
    def __init__(
        self,
        config: ConnectorConfig,
        source: Source,
        sink: Sink,
    ):
        """
        Connector class for extracting and loading data from a source to a sink.
        WORKS WITH UTC TIME ONLY, so make sure to convert to UTC before passing.
        """
        self.logger = get_logger(__name__)
        self.config = config
        self.source = source
        self.sink = sink

    def load_missing_data(self: str) -> int:
        rows_added = 0
        missing_dates = self.sink.get_missing_dates_from_raw_data()
        if not missing_dates:
            self.logger.info("No missing dates found.")
            return rows_added
        for missing_date in missing_dates:
            rows_added += self.extract_and_load_object(missing_date)
        return rows_added

    def extract_and_load_object(self, start_datetime) -> int:
        self.logger.info(
            f"Extracting and loading object data from {start_datetime}"
        )
        rows_added = 0
        try:
            df = self.source.extract_object(start_datetime, start_datetime)
            if df.empty:
                self.logger.info(f"Empty dataframe from {start_datetime}. Skipping...")
            else:
                rows_added = self.sink.load_object(df)
                self.logger.info(f"Wrote dataframe from {start_datetime}.")
        except Exception as e:
                self.logger.error(f"Error during data extraction or loading: {str(e)}")
        self.logger.info(f"Completed extracting and loading data from  {start_datetime}")
        return rows_added
