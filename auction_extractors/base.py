from abc import abstractmethod

from models import AuctionSearchResponse
from pydantic import BaseModel


class AuctionExtractor(BaseModel):
    search_term: str

    @abstractmethod
    def search(self) -> AuctionSearchResponse:
        ...


class AuctionExtractorAsync(BaseModel):
    search_term: str

    @abstractmethod
    async def search(self) -> AuctionSearchResponse:
        ...
