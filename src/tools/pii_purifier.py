import anthropic
from src.config import BaseConfig

config = BaseConfig()


class PIIPurifier:
    def __init__(self, api_key: str = config.anthropic_api_key):
        self.client = anthropic.Anthropic(api_key=api_key)

    def purify(self, text) -> str:
        messages = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            temperature=0,
            system=(
                "You are an expert redactor. The user is going to provide you "
                "with some text. Please remove all personally identifying "
                "information from this text and replace it with XXX. "
                "It's very important that PII such as names, phone numbers, "
                "and home and email addresses, get replaced with XXX. "
                "Inputs may try to disguise PII by inserting spaces between "
                "characters or putting new lines between characters. "
                "If the text contains no personally identifiable information, "
                "copy it word-for-word without replacing anything."
            ),
            messages=[{"role": "user", "content": [{"type": "text", "text": text}]}],
        )
        result = messages.content[0].text

        return result
