from pydantic import BaseModel


class TaskInputSchema(BaseModel):
    jira_title: str
    jira_description: str | None = None
    slack_link: str | None = None


class TaskOutputSchema(TaskInputSchema):
    id: str

    task_text: str | None = None
    predicted_hours: int | None = None
