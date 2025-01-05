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
    logger.info(f"Got {len(issue_ids)=} issues ids")

    issues = get_bulk_data_from_jira_api(issue_ids)
    logger.info(f"Got {len(issues)=} issues jsons")

    output_path.write_text(json.dumps(issues, indent=4, ensure_ascii=False))
    logger.info(f"Saved issues to {output_path}")


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
    json_data = {"jql": f"project = {key}", "fields": ["key"], "maxResults": 5000}

    try:
        response = requests.post(
            f"{config.jira_domain}/rest/api/3/search/jql",
            cookies=cookies,
            headers=headers,
            json=json_data,
            timeout=600,
        )

        return response.json()
    except Exception as e:
        logger.error(f"Error: {e}")
        return {}


def get_bulk_data_from_jira_api(
    issue_ids: list,
    fields_list: Iterable[str] | None = (
        "description",
        "assignee",
        "summary",
        "issuetype",
        "status",
        "created",
        "timeestimate",
        "timeoriginalestimate",
        # custom fields for my project
        "customfield_12039",
        "customfield_12040",
        "customfield_12041",
    ),
) -> list:
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
        issues = []
        for i in range(0, len(issue_ids), 100):
            json_data = {
                "fields": fields_list,
                "issueIdsOrKeys": issue_ids[i : i + 100],
            }
            response = requests.post(
                f"{config.jira_domain}/rest/api/2/issue/bulkfetch",
                cookies=cookies,
                headers=headers,
                json=json_data,
                timeout=600,
            )
            issues.extend(response.json()["issues"])

        return issues
    except Exception as e:
        logger.error(f"Error: {e}")
        return []


if __name__ == "__main__":
    app()
