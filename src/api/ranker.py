from pydantic import BaseModel
from sentence_transformers.cross_encoder import CrossEncoder
from src.config import BaseConfig
import pandas as pd

config = BaseConfig()


class RankerInput(BaseModel):
    query: str
    top_k: int = 5


class RankerOutput(RankerInput):
    results: list


class Ranker:
    def __init__(
        self,
        model_name: str = "cross-encoder/stsb-distilroberta-base",
        data_path: str = config.processed_data_dir / "final_data_to_train.json",
    ):
        self.model = CrossEncoder(model_name)
        self.data = pd.read_json(data_path)

    def rank(self, query: str, top_k: int = 5):
        """
        Rank tasks by query.

        :param query:
        :param top_k:
        :return:
        """
        return self.model.rank(query, self.data["task_text"])[:top_k]

    def __call__(self, input: RankerInput) -> RankerOutput:
        """
        Rank tasks by query.

        :param input:
        :return:
        """
        results = self.rank(input.query, input.top_k)

        results = [
            {
                "task_text": self.data.iloc[result["corpus_id"]].tolist(),
                "score": result["score"],
            }
            for result in results
        ]

        return RankerOutput(query=input.query, top_k=input.top_k, results=results)


if __name__ == "__main__":
    ranker = Ranker()
    print(
        ranker(RankerInput(query="How to make a good " "coffee?")).model_dump_json(
            indent=4
        )
    )
