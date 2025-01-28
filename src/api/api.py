from fastapi import APIRouter
from src.api.schemas import TaskInputSchema, TaskOutputSchema
from src.api.services import TaskEstimatorService

router = APIRouter(
    prefix="/task",
)


@router.post("/estimate_time")
async def estimate_time(task: TaskInputSchema) -> TaskOutputSchema:
    """
    Оценка времени выполнения задачи.

    :param task:
    :return:
    """

    return TaskEstimatorService()(task)
