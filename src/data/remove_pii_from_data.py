from typing import Iterable

from loguru import logger
from tqdm import tqdm
from typer import Typer
from pathlib import Path
from src.config import BaseConfig
import json

from src.tools.pii_purifier import PIIPurifier

app = Typer(pretty_exceptions_enable=False)

config = BaseConfig()


@app.command()
def main(
    input_path: Path = config.interim_data_dir / "enriched_jira_tasks.json",
    output_path: Path = config.interim_data_dir / "enriched_jira_tasks_no_pii.json",
    pii_fields_to_remove: str = "jira_description",
):
    """
    Remove PII from the given data
    :param input_path:
    :param output_path:
    :param pii_fields_to_remove:
    :return:
    """

    data = json.loads(input_path.read_text())
    pii_fields = pii_fields_to_remove.split(",")

    data = remove_pii_from_data(data, pii_fields)

    output_path.write_text(json.dumps(data, indent=4, ensure_ascii=False))
    logger.info(f"Saved issues to {output_path}")


def remove_pii_from_data(
    data: Iterable[dict],
    pii_fields: Iterable[str],
) -> Iterable[dict]:
    """
    Remove PII from the given data
    :param data:
    :param pii_fields:
    :return:
    """
    for record in tqdm(data):
        for pii_field in pii_fields:
            if pii_field in record and record[pii_field]:
                record[pii_field] = PIIPurifier().purify(record[pii_field])

    return data


if __name__ == "__main__":
    app()
