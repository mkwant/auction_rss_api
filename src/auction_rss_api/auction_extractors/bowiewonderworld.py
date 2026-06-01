import hashlib
import re
from datetime import datetime
from typing import List

import dateparser
import httpx
from bs4 import BeautifulSoup

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractor


class BowieWonderWorld(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return "https://bowiewonderworld.com/bowienews/latestnews.htm"

    @property
    def site_desc(self) -> str:
        return "BowieWonderWorld"

    def get_auctions(self) -> List[Auction]:
        r = httpx.get(url=self.search_link)
        r.raise_for_status()

        soup = BeautifulSoup(markup=r.text, features="html.parser")

        items = []

        # find all hr tags (each often separates sections)
        hrs = soup.find_all("hr")

        for hr in hrs:
            item = {
                "title": None,
                "date": None,
                "updated": None,
                "content": []
            }

            node = hr.find_next_sibling()
            date_pattern = re.compile(r"\d{1,2}(st|nd|rd|th)\s+\w+\s+\d{4}")

            while node and node.name != "hr":
                # Title (blue font block)
                if node.name == "font" and node.get("size") == "4":
                    item["title"] = node.text.strip()

                # Main text block
                elif node.name == "font" and node.get("size") == "2":
                    text = node.text.strip()

                    match = date_pattern.search(text)
                    if match:
                        item["date"] = match.group()

                        # remove only the matched date text from content
                        text = text.replace(item["date"], "").strip()

                    item["content"].append(text)

                elif node.name == "p":
                    item["content"].append(node.get_text(" ", strip=True))

                node = node.find_next_sibling()

            # only keep meaningful blocks
            if item["title"] or item["date"]:
                items.append(item)

            if not item["title"]:
                item["title"] = item["date"]

        auctions = []
        for i in items:
            if i["date"]:
                i["updated"] = dateparser.parse(i["date"])
            else:
                i["updated"] = datetime.now()

            auctions.append(
                Auction(
                    auction_id=hashlib.md5(f"{i['title']}-{i['date']}".encode()).hexdigest(),
                    title=i["title"],
                    link=self.search_link,
                    description="\n".join(i["content"]),
                    start_date=i["updated"],
                )
            )

        return auctions
