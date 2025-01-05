import anthropic
from src.config import BaseConfig
from pathlib import Path
import json
from pydantic import BaseModel

config = BaseConfig()
PATH_JSON = Path(__file__).parent / "task_creator_prompt.json"


class TaskCreatedSchema(BaseModel):
    result: str
    quality_check: bool


class TaskCreator:
    def __init__(
        self,
        api_key: str = config.anthropic_api_key,
        system_prompt_path: Path = PATH_JSON,
    ):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.system_prompt_json = json.loads(system_prompt_path.read_text())
        self.system_prompt: str = self.system_prompt_json["prompt"]
        self.examples: str = self.system_prompt_json["examples"]
        self.assistant_prefilled_part: str = self.system_prompt_json[
            "assistant_prefilled_part"
        ]

    def create_task(self, text) -> TaskCreatedSchema:
        """

        :param text:
        :return:
        """
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
        return TaskCreatedSchema(result=result, quality_check=quality_check)
