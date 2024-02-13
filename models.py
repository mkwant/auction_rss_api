from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class Auction(BaseModel):
    """An auction model."""
    title: str
    auction_id: str
    description: str
    link: str
    image_link: Optional[str]
    seller: Optional[str] = None
    start_date: datetime


class AuctionSearchResponse(BaseModel):
    """The result from an auction search."""
    search_link: str
    search_term: str
    site_desc: str
    auctions: List[Auction]
