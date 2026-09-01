import html
import json
from datetime import datetime
from typing import List

import curl_cffi
import dateparser
from bs4 import BeautifulSoup

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractor


class Kleinanzeigen(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return f'https://www.kleinanzeigen.de/s-{self.search_term}/k0'

    @property
    def site_desc(self) -> str:
        return 'Kleinanzeigen'

    def get_auctions(self) -> List[Auction]:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:154.0) Gecko/20100101 Firefox/154.0'}

        r = curl_cffi.get(url=self.search_link, headers=headers, impersonate='firefox')
        r.raise_for_status()

        soup = BeautifulSoup(markup=html.unescape(r.text), features='html.parser')

        items = soup.select('article[data-adid]')

        auctions = []

        for item in items:
            auction_id = item.get('data-adid')
            href = item.get('data-href')

            if not auction_id or not href:
                continue

            link = f'https://www.kleinanzeigen.de{href}'

            data = {}

            script = item.select_one(
                'script[type="application/ld+json"]'
            )

            if script and script.string:
                try:
                    data = json.loads(script.string)
                except json.JSONDecodeError:
                    pass

            # Title
            title = data.get('title')

            if not title:
                title_element = item.select_one('h3 a')

                if title_element:
                    title = title_element.get_text(strip=True)

            if not title:
                continue

            # Description
            description_text = data.get('description')

            if not description_text:
                description_element = item.select_one('p')

                if description_element:
                    description_text = description_element.get_text(
                        " ",
                        strip=True,
                    )

            # Image
            image_link = data.get('contentUrl')

            if not image_link:
                image = item.select_one('img')

                if image:
                    image_link = (
                            image.get('srcset')
                            or image.get('src')
                    )

            if not image_link:
                image_link = (
                    'https://www.kleinanzeigen.de/'
                    'liberty/liberty-js/placeholder-logo.svg'
                )

            image_link = image_link.replace(
                '$_35.AUTO',
                '$_59.AUTO',
            ).replace(
                '$_35',
                '$_59',
            )

            text = item.get_text('\n', strip=True)
            lines = [
                line.strip()
                for line in text.splitlines()
                if line.strip()
            ]

            start_date = datetime.now()

            if len(lines) >= 3:
                date_text = lines[2]

                parsed_date = dateparser.parse(
                    date_text,
                    languages=['de'],
                    settings={
                        'RELATIVE_BASE': datetime.now(),
                    },
                )

                if parsed_date:
                    start_date = parsed_date

            price = ''

            for line in reversed(lines):
                if '€' in line:
                    price = line
                    break

            description = description_text or ''

            if price:
                description = (
                    f'{description}\n\n{price}'
                    if description
                    else price
                )
            auctions.append(
                Auction(
                    title=title,
                    auction_id=auction_id,
                    description=description,
                    link=link,
                    image_link=image_link,
                    start_date=start_date,
                )
            )

        return auctions
