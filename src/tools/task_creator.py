from typing import Optional

import anthropic
from loguru import logger

from src.config import BaseConfig
from pathlib import Path
import json
from pydantic import BaseModel, Field

config = BaseConfig()
PATH_JSON = Path(__file__).parent / "task_creator_prompt.json"


class TaskSchema(BaseModel):
    jira_title: str | None
    jira_description: str | None
    slack_messages: str | None


class TaskCreatedSchema(BaseModel):
    result: str
    flg_ok_quality: bool
    flg_llm_work_done: bool

    error: Optional[str] = Field(None, title="Error message")


class TaskCreator:
    def __init__(
        self,
        api_key: str = config.anthropic_api_key,
        system_prompt_path: Path = PATH_JSON,
    ):
        logger.info(api_key)
        self.client = anthropic.Anthropic(api_key=api_key)
        self.system_prompt_json = json.loads(system_prompt_path.read_text())
        self.system_prompt: str = self.system_prompt_json["prompt"]
        self.examples: str = self.system_prompt_json["examples"]
        self.assistant_prefilled_part: str = self.system_prompt_json[
            "assistant_prefilled_part"
        ]

    @staticmethod
    def combine_json_to_task(task: TaskSchema) -> str:
        """

        :param task:
        :return:
        """
        text = (
            f"{task.jira_title=}\n\n"
            f"{task.jira_description=}\n\n"
            f"{task.slack_messages=}"
        )
        return text

    def create_task(self, text) -> TaskCreatedSchema:
        """

        :param text:
        :return:
        """

        try:
            messages = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4096,
                temperature=0,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": self.examples},
                            {
                                "type": "text",
                                "text": self.system_prompt.replace(
                                    "{{UNSTRUCTURED_TEXT}}", text
                                ),
                            },
                        ],
                    },
                    {
                        "role": "assistant",
                        "content": [
                            {"type": "text", "text": self.assistant_prefilled_part}
                        ],
                    },
                ],
            )
            result = messages.content[0].text
            result = result.strip()

            quality_check = False
            if result.startswith("**Summary") and result.endswith("```"):
                quality_check = True

            result = result[:-3].strip()
            return TaskCreatedSchema(
                result=result, flg_ok_quality=quality_check, flg_llm_work_done=True
            )
        except Exception as e:
            logger.error(f"Error creating task: {e}")

            return TaskCreatedSchema(
                result="", flg_ok_quality=False, error=str(e), flg_llm_work_done=False
            )
