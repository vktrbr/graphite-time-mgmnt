from typing import Optional

import anthropic
from loguru import logger

from src.config import BaseConfig
from pathlib import Path
import json
from pydantic import BaseModel

config = BaseConfig()
PATH_JSON = Path(__file__).parent / "task_estimation_prompt.json"


class QuerySchema(BaseModel):
    current_task: str
    related_tasks: list[dict]
    weeks_since_member_join: int
    assignee_level_order: int


class LLMEvaluationResultSchema(BaseModel):
    current_task: Optional[str] = None
    estimated_time: Optional[int] = None
    explanation: Optional[str] = None

    error: Optional[str] = None
    raw_result: Optional[str] = None


class TaskEstimator:
    def __init__(
        self,
        api_key: str = config.anthropic_api_key,
        system_prompt_path: Path = PATH_JSON,
    ):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.system_prompt_json = json.loads(system_prompt_path.read_text())
        self.examples: str = self.system_prompt_json["examples"]
        self.system_prompt: str = self.system_prompt_json["prompt"]

    def estimate_task_time(self, query: QuerySchema) -> LLMEvaluationResultSchema:
        try:
            related_tasks_str = "\n".join(
                [
                    f"{{\"jira_key\": \"{task['jira_key']}\", "
                    f"\"task_text\": \"{task['task_text']}\", "
                    f"\"time_to_complete_hours\": {task['time_to_complete_hours']}, "
                    f"\"assignee_level_order\": {task['assignee_level_order']}, "
                    f"\"weeks_since_member_join\": {task['weeks_since_member_join']}}}"
                    for task in query.related_tasks
                ]
            )

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
                                    "{{RELATED_TASKS}}", related_tasks_str
                                )
                                .replace("{{CURRENT_TASK}}", query.current_task)
                                .replace(
                                    "{{WEEKS_SINCE_MEMBER_JOIN}}",
                                    str(query.weeks_since_member_join),
                                )
                                .replace(
                                    "{{ASSIGNEE_LEVEL_ORDER}}",
                                    str(query.assignee_level_order),
                                ),
                            },
                        ],
                    },
                    {
                        "role": "assistant",
                        "content": [{"type": "text", "text": "```json"}],
                    },
                ],
            )
            result = messages.content[0].text
            result = result.strip()

            valid = False
            if result[0] == "{" and result[-3:] == "```":
                result = result[:-3]
                valid = True

            if valid:
                return LLMEvaluationResultSchema.model_validate_json(result)
            else:
                return LLMEvaluationResultSchema(
                    error="Invalid result", raw_result=result
                )
        except Exception as e:
            logger.error(f"Error estimating task time: {e}")

            return LLMEvaluationResultSchema(
                error=str(e),
            )
