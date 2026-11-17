import datetime
import re
from typing import List, Optional

from bs4 import BeautifulSoup, Tag
from playwright.async_api import Page, TimeoutError as PlaywrightTimeoutError

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractorAsync

ROW_LINK_SELECTOR = "a[data-row-link]"

_UNIT_DAYS = {"day": 1, "week": 7, "month": 30, "year": 365}


def valid_xml_char_ordinal(c):
    """Test for any non-unicode characters."""
    codepoint = ord(c)
    # conditions ordered by presumed frequency
    return (
        0x20 <= codepoint <= 0xD7FF
        or codepoint in (0x9, 0xA, 0xD)
        or 0xE000 <= codepoint <= 0xFFFD
        or 0x10000 <= codepoint <= 0x10FFFF
    )


def parse_listed(text: str) -> datetime.datetime:
    """Parse 'Listed today' / 'Listed yesterday' / 'Listed 3 days|weeks|months|years ago'."""
    text = " ".join(text.split()).lower()  # also normalises non-breaking spaces
    now = datetime.datetime.now()
    if "yesterday" in text:
        return now - datetime.timedelta(days=1)
    match = re.search(r"(\d+)\s*(day|week|month|year)", text)
    if match:
        return now - datetime.timedelta(days=int(match[1]) * _UNIT_DAYS[match[2]])
    return now  # "today" or anything unrecognised


def parse_price(price_p: Optional[Tag]) -> str:
    """The price is split over several spans, e.g. '20', sr-only '.', '95', '€'."""
    if price_p is None:
        return ""
    text = " ".join(price_p.get_text(" ", strip=True).split())  # '20 . 95 €'
    text = re.sub(r"(\d+)\s*\.\s*(\d+)", r"\1.\2", text)
    return text


class MusicStack(AuctionExtractorAsync):
    search_term: str

    @property
    def search_link(self) -> str:
        return f"https://www.musicstack.com/show.cgi?per_page=50&new=1&find={self.search_term}"

    @property
    def site_desc(self) -> str:
        return "MusicStack"

    async def get_auctions(self) -> List[Auction]:
        page: Page = await self.browser.new_page()

        try:
            await page.goto(
                url=self.search_link,
                wait_until="domcontentloaded",
                timeout=30_000,
            )

            try:
                await page.wait_for_selector(selector=ROW_LINK_SELECTOR, timeout=30_000)
            except PlaywrightTimeoutError:
                pass  # no results (or layout changed again) -> parsing below yields an empty list

            html = await page.content()

        finally:
            await page.close()

        soup = BeautifulSoup(markup=html, features="html.parser")

        auctions = []

        for item_link in soup.select(ROW_LINK_SELECTOR):
            row = item_link.find_parent("div", class_="group")
            if row is None:
                continue

            link = item_link["href"]
            auction_id = link.rstrip("/").split("/")[-1]

            paragraphs = row.find_all("p", recursive=False)
            artist = " ".join(paragraphs[0].get_text().split())
            title_p = paragraphs[1]
            _title = " ".join(title_p.select_one("span.line-clamp-3").get_text().split())
            title = f"{artist} - {_title}" if artist else _title

            _format = " ".join(paragraphs[2].select_one("span").get_text().split())

            details = title_p.find("span", class_="max-md:hidden")
            blocks = details.find_all("span", class_="block", recursive=False)
            # blocks: [description + condition], [Sold by ...], [Listed ...]
            _description = "\n".join(" ".join(ln.split()) for ln in blocks[0].get_text("\n").splitlines() if ln.strip())
            seller = " ".join(blocks[1].get_text().split()).removeprefix("Sold by ")
            start_date = parse_listed(blocks[2].get_text())

            price_p = row.select_one("div p.text-2xl")
            _price = parse_price(price_p)

            img = row.select_one("img")
            image_link = img.get("src", "") if img else ""

            description = "\n".join((_price, _format, _description))
            description = "".join(c for c in description if valid_xml_char_ordinal(c))

            auctions.append(
                Auction(
                    title=title,
                    auction_id=auction_id,
                    description=description,
                    link=link,
                    image_link=image_link,
                    seller=seller,
                    start_date=start_date,
                )
            )
        return auctions
