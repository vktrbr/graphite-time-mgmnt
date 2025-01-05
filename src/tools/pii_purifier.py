import anthropic
from src.config import BaseConfig
from pathlib import Path
import json

config = BaseConfig()
PATH_JSON = Path(__file__).parent / "pii_purifier_prompt.json"


class PIIPurifier:
    def __init__(
        self,
        api_key: str = config.anthropic_api_key,
        system_prompt_path: Path = PATH_JSON,
    ):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.system_prompt_json = json.loads(system_prompt_path.read_text())
        self.system_prompt: str = self.system_prompt_json["prompt"]
        self.examples: str = self.system_prompt_json["examples"]

    def purify(self, text) -> str:
        """
        Template method to purify the given text

        :param text:
        :return:
        """

        return text

    def todo_purify(self, text) -> str:
        """
        Purify the given text

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
                                "{{text_to_redact}}", text
                            ),
                        },
                    ],
                },
                {
                    "role": "assistant",
                    "content": [{"type": "text", "text": "<pii_analysis>"}],
                },
            ],
        )
        result = messages.content[0].text

        result = result.split("</pii_analysis>")[-1]
        result = result.strip()

        return result
