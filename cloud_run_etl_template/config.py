import pydantic
from pyaml_env import parse_config

from cloud_run_etl_template.connector import ConnectorConfig
from cloud_run_etl_template.sink import DummySinkConfig
from cloud_run_etl_template.source import DummySourceConfig


class Config(pydantic.BaseModel):
    source: DummySourceConfig
    sink: DummySinkConfig
    connector: ConnectorConfig


def get_config(config_path: str = "config.yaml") -> Config:
    config = parse_config(config_path)
    return Config(**config)
