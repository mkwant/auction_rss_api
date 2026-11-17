import asyncio
import json
from typing import ClassVar, List

from bs4 import BeautifulSoup
from playwright.async_api import Page

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractorAsync


class BandcampFaves(AuctionExtractorAsync):
    # Every request is a real browser tab, so keep this modest.
    MAX_CONCURRENT_REQUESTS: ClassVar = 2
    PAGE_TIMEOUT_MS: ClassVar = 60_000
    CHALLENGE_MARKER: ClassVar = "/_fs-ch-"

    @property
    def search_link(self) -> str:
        return f"https://bandcamp.com/{self.search_term}/following/artists_and_labels"

    @property
    def site_desc(self) -> str:
        return "Bandcamp faves"

    async def get_html(self, url: str) -> str:
        """Load a URL in the browser, wait out the client challenge, return the HTML."""

        page: Page = await self.browser.new_page()

        try:
            await page.goto(
                url=url,
                wait_until="domcontentloaded",
                timeout=self.PAGE_TIMEOUT_MS,
            )

            loop = asyncio.get_running_loop()
            deadline = loop.time() + self.PAGE_TIMEOUT_MS / 1000

            while True:
                try:
                    html = await page.content()

                    if self.CHALLENGE_MARKER not in html:
                        # Real page reached; let it finish parsing, then re-read.
                        await page.wait_for_load_state("domcontentloaded")
                        return await page.content()
                except Exception:
                    # The page is probably mid-navigation (challenge reload).
                    pass

                if loop.time() > deadline:
                    raise TimeoutError(f"Bandcamp client challenge not passed for {url}")

                await asyncio.sleep(0.5)
        finally:
            await page.close()

    @staticmethod
    def parse_merch(html: str, subdomain: str) -> list[Auction]:
        """Given the HTML of a merch page, extract the merch items."""

        auctions = []
        base_url = f"https://{subdomain}.bandcamp.com"

        soup = BeautifulSoup(markup=html, features="html.parser")

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

    async def get_bandcamp_merch(
            self,
            subdomain: str,
            semaphore: asyncio.Semaphore,
    ) -> list[Auction]:
        """Given a subdomain, scrape the merch items."""

        try:
            async with semaphore:
                html = await self.get_html(f"https://{subdomain}.bandcamp.com/merch")

            return self.parse_merch(html=html, subdomain=subdomain)
        except Exception as e:
            raise RuntimeError(f"Bandcamp merch failed for {subdomain}: {e!r}") from e

    async def get_followed_subdomains(self) -> list[str]:
        """Get the subdomains of the artists the user is following."""

        html = await self.get_html(self.search_link)

        soup = BeautifulSoup(markup=html, features="html.parser")

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

        subdomains = await self.get_followed_subdomains()

        semaphore = asyncio.Semaphore(self.MAX_CONCURRENT_REQUESTS)

        tasks = [
            asyncio.create_task(self.get_bandcamp_merch(subdomain=subdomain, semaphore=semaphore))
            for subdomain in subdomains
        ]

        try:
            results = await asyncio.gather(*tasks)
        except BaseException:
            # Fail the whole feed, but don't leave the other pages loading.
            for task in tasks:
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
            raise

        # Flatten the list of lists.
        return [item for fave in results for item in fave]

    async def get_auctions(self) -> List[Auction]:
        auctions = await self.get_faves_merch()
        auctions.sort(
            key=lambda x: x.auction_id,
            reverse=True,
        )
        return auctions
