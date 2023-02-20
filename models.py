from datetime import datetime
from typing import List, Optional, Union

from pydantic import BaseModel, HttpUrl, AnyUrl


class Auction(BaseModel):
    """An auction model."""
    title: str
    auction_id: str
    description: str
    link: HttpUrl
    image_link: Optional[str]
    seller: Optional[str]
    start_date: datetime


class AuctionSearchResponse(BaseModel):
    """The result from an auction search."""
    search_link: str
    search_term: str
    site_desc: str
    auctions: List[Auction]
