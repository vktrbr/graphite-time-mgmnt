from uuid import uuid4

from src.api.schemas import TaskInputSchema, TaskOutputSchema
from src.data.enrich_with_slack_thread import enrich_with_slack_thread
from src.tools.task_creator import TaskCreator, TaskSchema, TaskCreatedSchema
from src.tools.ask_anthropic import TaskEstimator
from src.api.ranker import Ranker, RankerOutput, RankerInput
from src.config import BaseConfig
from loguru import logger

import joblib

config = BaseConfig()


class TaskEstimatorService:
    def __init__(self):
        self.task_creator = TaskCreator()
        self.task_estimator = TaskEstimator()
        self.ranker = Ranker()
        self.model = joblib.load(config.models_dir / "regression_model.pkl")

    def __call__(self, task: TaskInputSchema) -> TaskOutputSchema:
        return self._estimate_time(task)

    def _estimate_time(self, task: TaskInputSchema) -> TaskOutputSchema:
        """
        Оценка времени выполнения задачи.


        :param task:
        :return:
        """
        logger.info("Start task estimation")
        input_task = task
        task = self._enrich_with_slack_thread(task)
        logger.info("Enriched with Slack thread")
        task_created = self._create_task(task)
        logger.info("Task created")

        eta = self._estimate_task_time(task_created)
        logger.info("Task estimated")

        return TaskOutputSchema(
            jira_title=input_task.jira_title,
            jira_description=input_task.jira_description,
            slack_link=input_task.slack_link,
            id=str(uuid4()),
            task_text=task_created.result,
            predicted_hours=eta,
        )

    def _estimate_task_time(self, task: TaskCreatedSchema) -> int:
        """
        Оценка времени выполнения задачи.

        :param task:
        :return:
        """
        result = self.model.predict([task.result])
        return round(result[0], 0)

    def _get_relevant_tasks(self, task: TaskCreatedSchema) -> RankerOutput:
        """
        Получение релевантных задач.

        :param task:
        :return:
        """
        if not task.flg_ok_quality:
            raise ValueError("Task quality is not ok")

        input_ = RankerInput(query=task.result)
        result = self.ranker(input_)
        return result

    def _create_task(self, task: TaskSchema) -> TaskCreatedSchema:
        """
        Создание задачи.

        :param task:
        :return:
        """
        text = self.task_creator.combine_json_to_task(task)
        result = self.task_creator.create_task(text)
        return result

    @staticmethod
    def _enrich_with_slack_thread(task: TaskInputSchema) -> TaskSchema:
        """
        Обогащение данных задачи данными из Slack.

        :param task:
        :return:
        """
        result = enrich_with_slack_thread({"slack_link": task.slack_link})

        return TaskSchema(
            jira_title=task.jira_title,
            jira_description=task.jira_description,
            slack_messages=result["slack_thread_messages"],
        )
