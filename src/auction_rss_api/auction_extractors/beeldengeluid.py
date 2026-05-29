import asyncio
from typing import List

import httpx

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractor


class BeeldEnGeluid(AuctionExtractor):
    LIMIT: int = 50

    @property
    def search_link(self) -> str:
        return f"https://schatkamer.beeldengeluid.nl/zoeken?q={self.search_term}&sorteren=oudste"

    @property
    def site_desc(self) -> str:
        return "BeeldEnGeluid Schatkamer"

    async def fetch_page(self, client: httpx.AsyncClient, offset: int) -> dict:
        url = "https://schatkamer.beeldengeluid.nl/api/media/bff/search"
        params = {
            "query": self.search_term,
            "playable": True,
            "sort": "date-oldest",
            "offset": offset,
            "limit": self.LIMIT,
        }

        response = await client.get(url=url, params=params)
        response.raise_for_status()

        return response.json()

    async def fetch_all_pages(self) -> list[dict]:
        async with httpx.AsyncClient(timeout=30) as client:
            # First request to determine total amount
            first_page = await self.fetch_page(client=client, offset=0)

            total = first_page["data"]["total"]
            results = first_page["data"]["results"]

            # Create tasks for remaining pages
            tasks = []

            for offset in range(self.LIMIT, total, self.LIMIT):
                tasks.append(self.fetch_page(client=client, offset=offset))

            # Fetch all remaining pages concurrently
            pages = await asyncio.gather(*tasks)

            # Merge all results
            for page in pages:
                results.extend(page["data"]["results"])

        return results

    def get_auctions(self) -> List[Auction]:
        auctions = []

        for item in asyncio.run(self.fetch_all_pages()):
            unique_id = item["externalId"]

            if item['series'] is not None:
                title = f"{item['date']}: [{item['mediaType'].upper()}] {item['series']['title']} - {item['title'] or 'Geen afleveringstitel'}"
                link = f"https://schatkamer.beeldengeluid.nl/serie/{item["series"]["id"]}/{item["series"]["slug"]}/aflevering/{item["externalId"]}"
            else:
                title = f"{item['date']}: [{item['mediaType'].upper()}] {item['title']}"
                link = f"https://schatkamer.beeldengeluid.nl/programma/{item["externalId"]}/{item["slug"]}"

            if item['image'] is not None:
                image_link = item['image']['url']
            else:
                image_link = None

            _highlights = item['highlights']['summary'] if 'summary' in item['highlights'] else ''
            _summary = item['summary'] if 'summary' in item else ''
            description = f"{_highlights}\n\n{_summary}"

            author = item['broadcaster']

            auctions.append(
                Auction(
                    auction_id=unique_id,
                    title=title,
                    link=link,
                    image_link=image_link,
                    description=description,
                    seller=author,
                )
            )

        return auctions
