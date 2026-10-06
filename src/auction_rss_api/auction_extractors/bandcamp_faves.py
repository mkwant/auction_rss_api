import asyncio
import json
from typing import ClassVar, List

import httpx2
from bs4 import BeautifulSoup

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractor


class BandcampFaves(AuctionExtractor):
    MAX_CONCURRENT_REQUESTS: ClassVar = 10

    @property
    def search_link(self) -> str:
        return f"https://bandcamp.com/{self.search_term}/following/artists_and_labels"

    @property
    def site_desc(self) -> str:
        return "Bandcamp faves"

    @staticmethod
    async def get_bandcamp_merch(
        subdomain: str,
        client: httpx2.AsyncClient,
        semaphore: asyncio.Semaphore,
    ) -> list[Auction]:
        """Given a subdomain, scrape the merch items."""

        auctions = []
        base_url = f"https://{subdomain}.bandcamp.com"

        async with semaphore:
            response = await client.get(f"{base_url}/merch")
            response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            features="html.parser",
        )

        item_list = soup.select_one("ol.merch-grid")

        if item_list is None:
            return auctions

        items = item_list.select("li.merch-grid-item")

        for item in items:
            title_element = item.select_one("p.title")

            if title_element is None:
                continue

            title_parts = [x.strip() for x in title_element if isinstance(x, str)]

            _title = " ".join(" ".join(title_parts).strip().split())

            artist_element = item.select_one("p.title>span.artist-override")

            if artist_element is not None:
                title = f"{artist_element.text}: {_title}"
            else:
                title = _title

            link_element = item.select_one("a")

            if link_element is None:
                continue

            stub = link_element.get("href")

            if not stub:
                continue

            if base_url in stub:
                link = stub
            else:
                link = base_url + stub

            image_element = item.select_one("img")

            if image_element is None:
                image_link = None
            else:
                image_link = image_element.get("data-original") or image_element.get("src")

                if image_link:
                    image_link = image_link.replace("_37", "_10")

            if not image_link:
                continue

            auction_id = image_link.split("/")[-1].split("_")[0]

            item_type_element = item.select_one("div.merchtype")
            price_element = item.select_one("p.price")

            item_type = item_type_element.text.strip() if item_type_element else ""

            price = price_element.text.strip() if price_element else ""

            description = f"{item_type}\n{price}".strip()

            auctions.append(
                Auction(
                    title=title,
                    auction_id=auction_id,
                    description=description,
                    link=link,
                    image_link=image_link,
                    seller=subdomain,
                )
            )

        return auctions

    def get_followed_subdomains(self) -> list[str]:
        """Get the subdomains of the artists the user is following."""

        with httpx2.Client(follow_redirects=True) as client:
            response = client.get(self.search_link)
            response.raise_for_status()

            soup = BeautifulSoup(
                response.content,
                features="html.parser",
            )

        pagedata = soup.select_one("div#pagedata")

        if pagedata is None:
            raise ValueError("Could not find Bandcamp page data")

        data_blob = pagedata.get("data-blob")

        if not data_blob:
            raise ValueError("Bandcamp page data is empty")

        json_data = json.loads(data_blob)

        following = json_data["item_cache"]["following_bands"]

        return [
            following[item]["url_hints"]["subdomain"]
            for item in following
            if following[item]["url_hints"].get("subdomain")
        ]

    async def get_faves_merch(self) -> list[Auction]:
        """Get merch of all followed subdomains."""

        subdomains = self.get_followed_subdomains()

        semaphore = asyncio.Semaphore(self.MAX_CONCURRENT_REQUESTS)

        async with httpx2.AsyncClient(
            follow_redirects=True,
        ) as client:
            tasks = [
                self.get_bandcamp_merch(
                    subdomain=subdomain,
                    client=client,
                    semaphore=semaphore,
                )
                for subdomain in subdomains
            ]

            faves_merch = await asyncio.gather(*tasks)

        # Flatten the list of lists.
        return [item for fave in faves_merch for item in fave]

    def get_auctions(self) -> List[Auction]:
        auctions = asyncio.run(self.get_faves_merch())
        auctions.sort(
            key=lambda x: x.auction_id,
            reverse=True,
        )
        return auctions
