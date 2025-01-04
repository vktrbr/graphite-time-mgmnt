from typing import Iterable

from loguru import logger
from typer import Typer
from pathlib import Path
from src.config import BaseConfig
import json
import requests

app = Typer(pretty_exceptions_enable=False)

config = BaseConfig()


@app.command()
def main(
    output_path: Path = config.raw_data_dir / "jira_tasks_from_api.json",
):
    """
    Request data from Jira API

    :param output_path:
    :return:
    """

    issues = get_my_project_issues()
    issue_ids = [issue["key"] for issue in issues["issues"]]

    data = [
        get_bulk_data_from_jira_api(issue_ids[i : i + 100])
        for i in range(0, len(issue_ids), 100)
    ]
    logger.info(f"Data shape: {len(data)}")

    output_path.write_text(json.dumps(data, indent=4, ensure_ascii=False))


def get_my_project_issues(key: str = config.jira_project_key) -> dict:
    """
    Get my project issues from Jira API

    :param key:
    :return:
    """

    cookies = {
        # мне немножко не дали доступов, поэтому реверс-инжиниринг
        "tenant.session.token": config.jira_api_key,
    }

    headers = {}
    try:
        response = requests.post(
            f"{config.jira_domain}/rest/api/3/search/jql",
            cookies=cookies,
            headers=headers,
            json={"jql": f"project = {key}", "fields": ["key"], "maxResults": 5000},
            timeout=600,
        )

        return response.json()
    except Exception as e:
        logger.error(f"Error: {e}")
        return {}


def get_bulk_data_from_jira_api(
    issue_ids: list,
    fields_list: Iterable[str] = (
        "description",
        "assignee",
        "summary",
        "issueType",
        "status",
        "created",
        "timeestimate",
        "timeoriginalestimate",
        # custom fields for my project
        "customfield_12039",
        "customfield_12040",
        "customfield_12041",
    ),
) -> dict:
    """
    Get bulk data from Jira API

    :param issue_ids:
    :param fields_list:
    :return:
    """
    cookies = {
        # мне немножко не дали доступов, поэтому реверс-инжиниринг
        # TODO: Make it correct
        "tenant.session.token": config.jira_api_key,
    }

    headers = {}
    try:
        response = requests.post(
            f"{config.jira_domain}/rest/api/2/issue/bulkfetch",
            cookies=cookies,
            headers=headers,
            json={"fields": fields_list, "issueIdsOrKeys": issue_ids},
            timeout=600,
        )

        return response.json()
    except Exception as e:
        logger.error(f"Error: {e}")
        return {}


if __name__ == "__main__":
    app()
