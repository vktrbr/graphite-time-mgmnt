from src.data.data_connector import get_engine
import pandas as pd
from loguru import logger
from typer import Typer
from pathlib import Path
from src.config import BaseConfig
import json

app = Typer(pretty_exceptions_enable=False)

config = BaseConfig()


@app.command()
def main(
    query_path: Path = config.raw_data_dir / "query_public.sql",
    params_path: Path = config.raw_data_dir / ".private_params.json",
    output_path: Path = config.raw_data_dir / "jira_tasks_from_dwh.csv",
):
    """
    Get raw data from DWH.

    :param query_path:
    :param params_path: Configuration file with query parameters
    :param output_path:
    :return:
    """
    query_path = query_path.read_text()
    params_path = json.loads(params_path.read_text())

    data = get_data(query_path, params_path)
    logger.info(f"Data shape: {data.shape}")
    data.to_csv(output_path, index=False)
    logger.info(f"Data saved to {output_path}")


def get_data(query: str, query_params: dict) -> pd.DataFrame:
    """
    Get data from DWH

    :param query:
    :param query_params:
    :return:
    """
    engine = get_engine(config.snowflake_database, config.snowflake_schema)
    with engine.connect() as conn:
        query = query.format(**query_params)
        df = pd.read_sql(query, conn)

    return df


if __name__ == "__main__":
    app()
