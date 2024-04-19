from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Auction(BaseModel):
    """An auction model."""
    title: str
    auction_id: str
    description: str
    link: str
    image_link: Optional[str] = None
    seller: Optional[str] = None
    start_date: datetime
