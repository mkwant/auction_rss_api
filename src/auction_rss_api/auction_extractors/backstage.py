from typing import List

import httpx
from bs4 import BeautifulSoup

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractor


class BackStage(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return "https://www.backstageauctions.com/catalog/index.php"

    @property
    def site_desc(self) -> str:
        return "Backstage Auctions store"

    def get_auctions(self) -> List[Auction]:
        auctions = []

        data = {'ckeyword': self.search_term}

        r = httpx.post(url=self.search_link, data=data)
        r.raise_for_status()

        soup = BeautifulSoup(r.text, features="html.parser")

        itemlist = soup.select_one('form#itemlist>table')
        for header_row in itemlist.select("tr:has(h2.itemhead)"):
            title = header_row.select_one("h2.itemhead a").text.strip()
            link = 'https://www.backstageauctions.com' + header_row.select_one("h2.itemhead a")['href']
            image_link = 'https://www.backstageauctions.com' + header_row.select_one("img")["src"].replace('_th', '')

            _details_row = header_row.find_next_sibling("tr")
            auction_id = _details_row.select_one('span.snap-list-id').find(string=True, recursive=False)
            _price = _details_row.select_one(".snap-list-price").text.strip()
            details = _details_row.select_one(".snap-list-id")
            description = f'{_price}\n\n'
            for label in details.select(".snap-list-categorylabel, .snap-list-traitlabel"):
                label_text = label.text.strip()
                value_elem = label.find_next_sibling("a")
                value_text = value_elem.text.strip()
                description += f"{label_text} {value_text}\n"

            auctions.append(
                Auction(auction_id=auction_id,
                        description=description,
                        image_link=image_link,
                        link=link,
                        title=title
                        )
            )

        return auctions
