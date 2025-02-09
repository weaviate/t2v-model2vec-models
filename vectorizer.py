import asyncio
from concurrent.futures import ThreadPoolExecutor
from pydantic import BaseModel
from typing import Optional

from model2vec import StaticModel


class VectorInputConfig(BaseModel):
    pooling_strategy: Optional[str] = None
    task_type: Optional[str] = None

    def __hash__(self):
        return hash((self.pooling_strategy, self.task_type))

    def __eq__(self, other):
        if isinstance(other, VectorInputConfig):
            return (
                self.pooling_strategy == other.pooling_strategy
                and self.task_type == other.task_type
            )
        return False


class VectorInput(BaseModel):
    text: str
    config: Optional[VectorInputConfig] = None

    def __hash__(self):
        return hash((self.text, self.config))

    def __eq__(self, other):
        if isinstance(other, VectorInput):
            return self.text == other.text and self.config == other.config
        return False


class Model2VecVectorizer:
    model: StaticModel

    def __init__(self, model_path: str):
        self.model = StaticModel.load_local(model_path)

    def vectorize(self, text: str, config: VectorInputConfig):
        embeddings = self.model.encode([text], use_multiprocessing=True)
        return embeddings[0]


class Vectorizer:
    executor: ThreadPoolExecutor

    def __init__(
        self,
        model_path: str,
    ):
        self.executor = ThreadPoolExecutor()
        self.vectorizer = Model2VecVectorizer(model_path)

    async def vectorize(self, text: str, config: VectorInputConfig):
        return await asyncio.wrap_future(
            self.executor.submit(self.vectorizer.vectorize, text, config)
        )
