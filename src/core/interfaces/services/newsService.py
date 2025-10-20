from abc import ABC, abstractmethod

from src.core.common.result import Result
from src.core.models.news import NewsInputModel, NewsOutputModel


class INewsService(ABC):
    @abstractmethod
    async def run(self, dto: NewsInputModel) -> Result[NewsOutputModel]:
        pass