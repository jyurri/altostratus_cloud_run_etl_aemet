from datetime import datetime

import pandas as pd
import pydantic


class DummySinkConfig(pydantic.BaseModel):
    table_name: str


class DummySink:
    def __init__(self, config: DummySinkConfig):
        self.config = config

    def get_last_update_datetime(self, object_id: str) -> datetime:
        # Return a dummy datetime
        return datetime(2021, 1, 1, 0, 0, 0)

    def load_object(self, object_id: str, df: pd.DataFrame) -> None:
        # Do nothing
        return None
