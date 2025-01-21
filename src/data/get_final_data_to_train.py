from tqdm import tqdm
from typer import Typer
from src.config import BaseConfig
import json
from pathlib import Path
from loguru import logger

app = Typer(pretty_exceptions_enable=False)

config = BaseConfig()


@app.command()
def main(
    input_path: Path = config.interim_data_dir / "combined_jira_tasks.json",
    output_path: Path = config.processed_data_dir / "processed_tasks.json",
):
    """
    Combine text information into one task.

    :param input_path:
    :param output_path:
    :return:
    """

    data = json.loads(input_path.read_text())
    new_data = []
    for item in tqdm(data):
        if not check_data_ok(item):
            continue

        new_data.append(select_columns(item))

    output_path.write_text(json.dumps(new_data, indent=4, ensure_ascii=False))


def check_data_ok(data: dict):
    """
    Check if the data is ok.
    :param data:
    :return:
    """
    flg_ok_quality = data["prepared_task"]["flg_ok_quality"]
    flg_llm_work_done = data["prepared_task"]["flg_llm_work_done"]

    if not flg_ok_quality:
        logger.error(f"Quality is not ok for {data['jira_key']}")
        return False

    if not flg_llm_work_done:
        logger.error(f"LLM work is not done for {data['jira_key']}")
        return False

    return True


def select_columns(data: dict):
    """
    Select the columns.
    :param data:
    :return:
    """
    return {
        "assignee_level_order": data["assignee_level_order"],
        "jira_key": data["jira_key"],
        "weeks_since_member_join": data["weeks_since_member_join"],
        "time_to_complete_hours": max(data["time_to_complete_hours"], 1),
        "task_text": data["prepared_task"]["result"],
    }


if __name__ == "__main__":
    app()
