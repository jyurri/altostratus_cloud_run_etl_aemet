import pydantic
from pyaml_env import parse_config

from cloud_run_elt.connector import ConnectorConfig
from cloud_run_elt.sink import SinkConfig
from cloud_run_elt.source import ApiSourceConfig


class Config(pydantic.BaseModel):
    source: ApiSourceConfig
    sink: SinkConfig
    connector: ConnectorConfig


def get_config(config_path: str = "config.yaml") -> Config:
    config = parse_config(config_path)
    return Config(**config)
