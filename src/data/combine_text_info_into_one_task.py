from tqdm import tqdm
from typer import Typer
from src.config import BaseConfig
import json
from pathlib import Path
from loguru import logger

from src.tools.task_creator import TaskCreator, TaskSchema

app = Typer(pretty_exceptions_enable=False)

config = BaseConfig()
HEADERS = {"Authorization": f"Bearer {config.slack_bot_token}"}


@app.command()
def main(
    input_path: Path = config.interim_data_dir / "cleaned_enriched_jira_tasks.json",
    output_path: Path = config.interim_data_dir / "combined_jira_tasks.json",
):
    """
    Combine text information into one task.

    :param input_path:
    :param output_path:
    :return:
    """

    data = json.loads(input_path.read_text())
    result = handle_task_creation(data)

    output_path.write_text(json.dumps(result, indent=4, ensure_ascii=False))
    logger.info(f"Prepared tasks saved to {output_path}")


def handle_task_creation(data: list[dict]) -> list[dict]:
    """
    Handle the creation of tasks from the given data.
    """
    task_creator = TaskCreator()
    for item in tqdm(data):
        task = TaskSchema(
            jira_title=item.get("jira_title"),
            jira_description=item.get("jira_description"),
            slack_messages=item.get("slack_thread_messages"),
        )

        task_description = task_creator.combine_json_to_task(task)
        result = task_creator.create_task(task_description)

        item["prepared_task"] = result.model_dump()

    return data


if __name__ == "__main__":
    app()
