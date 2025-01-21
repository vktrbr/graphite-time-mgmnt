import pytest
from src.tools.task_creator import TaskCreator
from pathlib import Path
import json


@pytest.fixture
def creator():
    return TaskCreator()


def test_creator(creator):
    example = json.loads(
        (Path(__file__).parent / "task_creator_prompt.json").read_text()
    )
    text = creator.combine_json_to_task(example)
    creator_result = creator.create_task(text)

    print(creator_result)

    assert creator_result.flg_ok_quality
