import string
from typing import Iterable

from loguru import logger
from typer import Typer
from pathlib import Path
from src.config import BaseConfig
import json

from urllib.parse import urlparse
from datetime import datetime

app = Typer(pretty_exceptions_enable=False)

config = BaseConfig()


@app.command()
def main(
    input_path: Path = config.raw_data_dir / "jira_tasks_from_api.json",
    output_path: Path = config.interim_data_dir / "jira_tasks_filtered.json",
):
    """
    Filter Jira JSON data by assignees, done issues, issue types,
    and necessary fields.

    :param input_path:
    :param output_path:
    :return:
    """

    data = json.loads(input_path.read_text())
    logger.info(f"Loaded Jira data from {input_path}")

    employees_information = read_employees_information()
    assignees_email = [employee["email"] for employee in employees_information]
    logger.info(f"Got {len(assignees_email)=} assignees email addresses")

    issues_information = read_issues_information()
    issue_types = [issue["id"] for issue in issues_information["types"]]
    logger.info(f"Got {len(issue_types)=} issue types")

    data = filter_by_assignees(data, assignees_email)
    data = filter_done_issues(data)
    data = filter_by_issue_types(data, issue_types)
    data = handle_custom_12039_12040_12041_fields(data)
    data = filter_necessary_fields(data)
    data = add_employee_information(data, employees_information)
    data = extract_slack_link_from_description(data)
    data = calculate_experience_weeks(data)
    data = filter_null_timeestimates(data)
    data = calculate_time_to_complete(data)

    data = rename_fields(
        data,
        {
            "key": "jira_key",
            "fields.summary": "jira_title",
            "fields.description": "jira_description",
            "fields.created": "jira_created",
            "fields.assignee.emailAddress": "assignee_email",
            "assignee_level_order": "assignee_level_order",
            "slack_link": "slack_link",
            "experience_weeks": "weeks_since_member_join",
            "time_to_complete_hours": "time_to_complete_hours",
        },
    )

    output_path.write_text(json.dumps(data, indent=4, ensure_ascii=False))


def read_issues_information(
    input_path: Path = config.raw_data_dir / ".private.issue_types.json",
) -> dict:
    """
    Read issues information from JSON file.

    :param input_path:
    :return:
    """
    issues_information = json.loads(input_path.read_text())
    logger.info(f"Loaded issues information from {input_path}")

    return issues_information


def read_employees_information(
    input_path: Path = config.raw_data_dir / ".private.employees.json",
) -> dict:
    """
    Read employees information from JSON file.

    :param input_path:
    :return:
    """
    employees_information = json.loads(input_path.read_text())
    logger.info(f"Loaded employees information from {input_path}")

    return employees_information


def filter_by_assignees(
    data: Iterable[dict],
    assignees_email: Iterable[str],
) -> Iterable[dict]:
    """
    Filter Jira JSON data by assignee email addresses.

    :param data:
    :param assignees_email:
    :return:
    """
    logger.info("Filtering Jira data by assignee email. Len = {len(data)}")
    res = []
    for item in data:
        try:
            if item["fields"]["assignee"]["emailAddress"] in assignees_email:
                res.append(item)
        except (KeyError, TypeError):
            pass
    logger.info("Filtered Jira data. Len = {len(res)}")

    return res


def filter_done_issues(data: Iterable[dict]) -> Iterable[dict]:
    """
    Filter Jira JSON data by done issues.

    :param data:
    :return:
    """
    logger.info("Filtering Jira data by done issues. Len = {len(data)}")
    res = [item for item in data if item["fields"]["status"]["name"] == "Done"]
    logger.info("Filtered Jira data. Len = {len(res)}")

    return res


def filter_by_issue_types(
    data: Iterable[dict],
    issue_types: Iterable[str],
) -> Iterable[dict]:
    """
    Filter Jira JSON data by issue types.

    :param data:
    :param issue_types: List of issue types IDs to filter by.
    :return:
    """
    logger.info("Filtering Jira data by issue types. Len = {len(data)}")
    res = [item for item in data if item["fields"]["issuetype"]["id"] in issue_types]
    logger.info(f"Filtered Jira data. {len(res)=}")

    return res


def filter_necessary_fields(
    data: Iterable[dict],
    fields: Iterable[str] = (
        "key",
        "fields.summary",
        "fields.issuetype.id",
        "fields.timeestimate",
        "fields.created",
        "fields.timeoriginalestimate",
        "fields.description",
        "fields.assignee.emailAddress",
        "fields.status.name",
    ),
) -> Iterable[dict]:
    """
    Filter Jira JSON data by necessary fields.

    :param data:
    :param fields: json path to fields to keep
    :return:
    """
    logger.info("Removing unnecessary fields from Jira data")
    res = []
    for item in data:
        res_item = {}
        for field in fields:
            value = item
            for key in field.split("."):
                value = value.get(key, {})
            res_item[field] = value if value else None
        res.append(res_item)
    logger.info(f"Removed unnecessary fields from Jira data. Len = {len(res)}")

    return res


def handle_custom_12039_12040_12041_fields(
    data: Iterable[dict],
) -> Iterable[dict]:
    """
    Handle custom fields 12039, 12040, 12041.

    :param data:
    :return:
    """
    logger.info("Handling custom fields 12039, 12040, 12041")
    for item in data:
        if not item.get("fields", {}).get("customfield_12039"):
            continue

        what_to_do = item.get("fields", {}).get("customfield_12039", "")
        why_to_do = item.get("fields", {}).get("customfield_12040", "")
        slack = item.get("fields", {}).get("customfield_12041", "")
        item["fields"]["description"] = (
            f"WE NEED TO DO: [{what_to_do}] \n"
            f"BECAUSE: [{why_to_do}] \n"
            f"SLACK LINK: {slack}"
        )

    logger.info("Handled custom fields 12039, 12040, 12041")

    return data


def add_employee_information(
    data: Iterable[dict],
    employees_information: Iterable[dict],
) -> Iterable[dict]:
    """
    Add employee information to Jira JSON filtered data

    :param data:
    :param employees_information: level, join_date, level_order
    :return:
    """
    logger.info("Adding employee information to Jira data")
    for item in data:
        assignee_email = item.get("fields.assignee.emailAddress")
        if not assignee_email:
            continue

        employee = next(
            (
                employee
                for employee in employees_information
                if employee["email"] == assignee_email
            ),
            None,
        )
        if not employee:
            continue

        item["assignee_level"] = employee["level"]
        item["assignee_join_date"] = employee["join_date"]
        item["assignee_level_order"] = employee["level_order"]

    return data


def extract_slack_link_from_description(
    data: Iterable[dict],
) -> Iterable[dict]:
    """
    Extract Slack link from description and add it to the data.

    :param data:
    :return:
    """
    logger.info("Extracting Slack link from description")
    for item in data:
        description = item.get("fields.description", "")
        if not description:
            continue

        all_valid_links = []
        for word_0 in description.split():
            words = word_0.split("|")
            for word in words:
                word = word.strip(string.punctuation)
                if urlparse(word).scheme in ["http", "https"]:
                    all_valid_links.append(word)

        slack_link = next(
            (link for link in all_valid_links if "slack.com" in link),
            None,
        )

        if not slack_link:
            continue
        # remove certain message path
        slack_link = slack_link.split("?")[0]

        item["slack_link"] = slack_link

    return data


def calculate_experience_weeks(
    data: Iterable[dict],
) -> Iterable[dict]:
    """
    Calculate experience weeks and add it to the data.

    :param data:
    :return:
    """
    logger.info("Calculating experience weeks")
    for item in data:
        assignee_join_date = item.get("assignee_join_date")
        task_created = item.get("fields.created")
        if not assignee_join_date:
            continue

        assignee_join_date = datetime.strptime(assignee_join_date[:10], "%Y-%m-%d")
        task_created = datetime.strptime(task_created[:10], "%Y-%m-%d")
        experience_weeks = (task_created - assignee_join_date).days // 7
        item["experience_weeks"] = experience_weeks

    return data


def calculate_time_to_complete(
    data: Iterable[dict],
) -> Iterable[dict]:
    """
    Calculate time to complete and add it to the data.

    :param data:
    :return:
    """
    logger.info("Calculating time to complete")
    for item in data:
        time_estimate = item.get("fields.timeestimate")
        time_original_estimate = item.get("fields.timeoriginalestimate")

        try:
            time_to_complete_minutes = time_estimate or time_original_estimate
            time_to_complete_hours = time_to_complete_minutes / 60 / 60
            item["time_to_complete_hours"] = int(time_to_complete_hours)

        except TypeError:
            item["time_to_complete_hours"] = None
            logger.warning(f"Error calculating time to complete for {item['key']}")

    return data


def filter_null_timeestimates(
    data: Iterable[dict],
) -> Iterable[dict]:
    """
    Filter out tasks with null timeoriginalestimate or timeestimate.

    :param data:
    :return:
    """
    logger.info("Filtering out tasks with null timeestimates")
    res = [
        item
        for item in data
        if item.get("fields.timeestimate") or item.get("fields.timeoriginalestimate")
    ]
    logger.info(f"Filtered out tasks with null timeestimates. Len = {len(res)}")

    return res


def rename_fields(
    data: Iterable[dict],
    fields: dict,
) -> Iterable[dict]:
    """
    Rename fields in Jira JSON data.

    :param data:
    :param fields: dict with old and new field names
    :return:
    """
    logger.info("Renaming fields in Jira data")
    new_data = []
    for item in data:
        new_item = {}
        for old_field, new_field in fields.items():
            new_item[new_field] = item.get(old_field)
        new_data.append(new_item)

    return new_data


if __name__ == "__main__":
    app()
