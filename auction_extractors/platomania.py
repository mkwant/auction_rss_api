from datetime import datetime
from typing import List

import requests
from bs4 import BeautifulSoup

from app.models import AuctionExtractor, Auction


class PlatoMania(AuctionExtractor):
    search_term: str

    @property
    def search_link(self) -> str:
        return f"https://www.platomania.nl/search/results/?q={self.search_term}"

    @property
    def site_desc(self) -> str:
        return "PlatoMania"

    def get_auctions(self) -> List[Auction]:
        r = requests.get(url=self.search_link)

        soup = BeautifulSoup(r.content, features='html.parser')
        articles = soup.select('main.content>article')

        items = []

        for article in articles:
            title = article.select_one('div.article__content')['title']
            link = 'https://www.platomania.nl' + article.select_one('div.article__image-container > a')['href']
            image_link = 'https://www.platomania.nl' + article.select_one('div.article__image')['style'].split('\'')[1]
            _medium = article.select_one('div.article__medium').text.strip()
            _price = article.select_one('div.article__price').text.strip()
            _desc = '\n'.join([x.text.strip() for x in article.select('div.article-details__text')])
            description = f"{_price} - {_medium}\n\n{_desc}"
            item_id = article.select_one('div.article__image-container > a')['href'].split('/')[2]

            items.append(
                Auction(
                    auction_id=item_id,
                    title=title,
                    link=link,
                    image_link=image_link,
                    description=description,
                    start_date=datetime.now()
                )
            )

        return items
