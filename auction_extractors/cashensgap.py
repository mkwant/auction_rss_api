import requests
from bs4 import BeautifulSoup

from models.auction import Auction
from models.auctionextractor import AuctionExtractor


class CashensGap(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return "https://www.cashensgap.com/products"

    @property
    def site_desc(self) -> str:
        return "Cashens Gap"

    def get_auctions(self) -> list[Auction]:
        auctions = []

        r = requests.get(self.search_link)
        soup = BeautifulSoup(r.content, features="html.parser")
        items = soup.select("div.product")

        for item in items:
            print(item)
            title = item.select_one("div.product-list-thumb-name").text.strip()
            _price = item.select_one("div.product-list-thumb-price").text.strip()
            _status = item.select_one("div.product-list-thumb-status").text.strip()
            description = f"{_price}\n\n{_status}"
            link = "https://www.cashensgap.com" + item.select_one("a")['href']
            auction_id = link.split('/')[-1]
            image_link = item.select_one("img")['data-srcset'].split(',')[-1].split()[0]

            auctions.append(
                Auction(**{
                    'title': title,
                    'auction_id': auction_id,
                    'description': description,
                    'link': link,
                    'image_link': image_link
                }))

        return auctions
