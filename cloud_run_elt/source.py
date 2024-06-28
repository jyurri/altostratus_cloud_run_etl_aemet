import logging
import requests
import pandas as pd
from datetime import datetime
import pydantic

class ApiSourceConfig(pydantic.BaseModel):
    endpoint: str
    api_key: str

class ApiSource:
    def __init__(self, config: ApiSourceConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)

    def extract_object(self, start_datetime: datetime, end_datetime: datetime) -> pd.DataFrame:
        formatted_start_date = start_datetime.strftime('%Y-%m-%dT%H%%3A%M%%3A%SUTC')
        formatted_end_date = end_datetime.strftime('%Y-%m-%dT%H%%3A%M%%3A%SUTC')
        url = f"{self.config.endpoint}api/valores/climatologicos/diarios/datos/fechaini/{formatted_start_date}/fechafin/{formatted_end_date}/todasestaciones"
        headers = {
            'api_key': self.config.api_key
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        if data['estado'] != 200:
            raise ValueError(f"API request failed with status {data['estado']}: {data['descripcion']}")

        datos_url = data['datos']
        datos_response = requests.get(datos_url)
        datos_response.raise_for_status()
        datos_data = datos_response.json()

        metadatos_url = data['metadatos']
        metadatos_response = requests.get(metadatos_url)
        metadatos_response.raise_for_status()
        metadatos_data = metadatos_response.json()

        type_mapping = {
            'string': str,
            'float': float,
        }

        column_types = {}
        for field in metadatos_data['campos']:
            field_id = field['id']
            field_type = field['tipo_datos']
            column_types[field_id] = type_mapping.get(field_type, str)

        df = pd.DataFrame(datos_data)

        for column, dtype in column_types.items():
            if column in df.columns:
                if dtype == float:
                    df[column] = df[column].replace('Ip', '0')
                    df[column] = df[column].str.replace(',', '.')
                try:
                    df[column] = df[column].astype(dtype)
                except ValueError as e:
                    self.logger.error(f"Could not convert column {column} to {dtype}: {e}")
                    if dtype == float:
                        df[column] = 0
                        df[column] = df[column].astype(dtype)
        return df
