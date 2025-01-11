from loguru import logger
from typer import Typer
from pathlib import Path
from src.config import BaseConfig
import json

from datetime import datetime

import re
import requests

app = Typer(pretty_exceptions_enable=False)

config = BaseConfig()
HEADERS = {"Authorization": f"Bearer {config.slack_bot_token}"}


@app.command()
def main(
    input_path: Path = config.interim_data_dir / "filtered_jira_tasks.json",
    output_path: Path = config.interim_data_dir / "enriched_jira_tasks.json",
):
    """
    Main function to enrich the JIRA tasks with Slack thread messages

    :param input_path:
    :param output_path:
    :return:
    """

    data = json.loads(input_path.read_text())

    enriched_data = []
    for item in data:
        enriched_item = enrich_with_slack_thread(item)
        enriched_data.append(enriched_item)

    output_path.write_text(
        json.dumps(enriched_data, indent=4, ensure_ascii=False, sort_keys=True)
    )

    logger.info(f"Enriched data saved to: {output_path}")


def enrich_with_slack_thread(data: dict) -> dict:
    """
    Enrich the data with the Slack thread messages
    :param data:
    :return:
    """
    slack_thread_link = data.get("slack_link")
    if not slack_thread_link:
        return data

    if "/archives/" not in slack_thread_link:
        return data

    channel_id, parent_ts = parse_slack_link(slack_thread_link)
    messages = fetch_thread_messages(channel_id, parent_ts)
    messages = filter_message_at_the_same_day(messages, parent_ts)
    messages = get_only_text_messages(messages)

    data["slack_thread_messages"] = "\n".join(messages)
    return data


def parse_slack_link(link: str):
    """
    Function to parse the link and extract channel ID and timestamp

    :param link: https://workspace.slack.com/archives/CHANNEL_ID/pTIMESTAMP
    :return:
    """
    match = re.search(r"/archives/([^/]+)/p(\d+)", link)
    if not match:
        raise ValueError("Invalid Slack message link format")

    channel_id = match.group(1)
    raw_ts = match.group(2)
    # Format the timestamp (add a '.' before the last 6 digits)
    timestamp = f"{raw_ts[:10]}.{raw_ts[10:]}"
    return channel_id, timestamp


def fetch_thread_messages(channel_id: str, parent_ts: str):
    """
    Fetch Thread Messages

    :param channel_id:
    :param parent_ts:
    :return:
    """
    url = "https://slack.com/api/conversations.replies"
    params = {"channel": channel_id, "ts": parent_ts}

    response = requests.get(url, headers=HEADERS, params=params, timeout=600)
    if response.status_code == 200:
        data = response.json()
        if data.get("ok"):
            return data.get("messages", [])
        else:
            logger.warning(f"Error: {data.get('error')}")
    else:
        logger.warning(f"HTTP Error: {response.status_code}")

    logger.warning(
        f"Failed to fetch thread messages for channel: "
        f"{channel_id} and ts: {parent_ts}"
    )
    return []


def filter_message_at_the_same_day(messages, parent_ts):
    """

    The end of 24 hours is the end of the day.

    :param messages:
    :param parent_ts: Format "1634567890.000100"
    :return:
    """
    end_of_day = datetime.fromtimestamp(float(parent_ts.split(".")[0]) + 86400)
    filtered_messages = []

    for msg in messages:
        ts = float(msg.get("ts"))
        if ts < end_of_day.timestamp():
            filtered_messages.append(msg)

    return filtered_messages


def get_only_text_messages(messages):
    """
    Get only text messages from the list of messages

    :param messages:
    :return:
    """
    return [msg.get("text") for msg in messages if msg.get("type") == "message"]


if __name__ == "__main__":
    app()
