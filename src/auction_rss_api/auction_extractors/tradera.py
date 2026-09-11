import codecs
import json
import re
from typing import List, Literal

import dateparser
import httpx
from bs4 import BeautifulSoup

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractor


class Tradera(AuctionExtractor):
    search_term: str
    currency: Literal['DKK', 'EUR', 'GBP', 'JPY', 'NOK', 'SEK', 'USD'] = 'EUR'

    @property
    def search_link(self) -> str:
        return f'https://www.tradera.com/en/search?sortBy=AddedOn&q={self.search_term}'

    @property
    def site_desc(self) -> str:
        return 'Tradera'

    @staticmethod
    def extract_flight_payloads(html: str) -> list[str]:
        """Extract and decode Next.js React Flight payloads from HTML."""
        marker = 'self.__next_f.push(['
        payloads = []
        pos = 0

        while True:
            start = html.find(marker, pos)
            if start == -1:
                break

            string_start = html.find('"', start + len(marker))
            if string_start == -1:
                break

            i = string_start + 1
            escaped = False

            while i < len(html):
                char = html[i]

                if escaped:
                    escaped = False
                elif char == '\\':
                    escaped = True
                elif char == '"':
                    break

                i += 1

            if i >= len(html):
                break

            raw = html[string_start + 1:i]

            try:
                decoded = codecs.decode(raw, encoding='unicode_escape')
            except UnicodeDecodeError:
                decoded = raw

            payloads.append(decoded)
            pos = i + 1

        return payloads

    @staticmethod
    def extract_currencies(payloads: list[str]) -> list[dict]:
        for payload in payloads:
            key = '"currencies":'
            idx = payload.find(key)
            if idx == -1:
                continue

            array_start = payload.find('[', idx)
            if array_start == -1:
                continue

            bracket_count = 0

            for i in range(array_start, len(payload)):
                if payload[i] == '[':
                    bracket_count += 1
                elif payload[i] == ']':
                    bracket_count -= 1

                    if bracket_count == 0:
                        array_end = i + 1
                        array_str = payload[array_start:array_end]
                        array_str = array_str.encode('latin1').decode('utf-8')

                        try:
                            return json.loads(array_str)
                        except json.JSONDecodeError:
                            continue

        return []

    @staticmethod
    def extract_items(html: str) -> list[dict]:
        """Extract auction data from the server-rendered search result cards."""
        soup = BeautifulSoup(html, 'html.parser')
        items = []

        for card in soup.select('[data-item-card-id]'):
            item_id = card.get('data-item-card-id')
            item_type = card.get('data-item-type')
            link_element = card.select_one('a[data-testid="item-card-image"]')
            title_element = card.select_one('.item-card-module-scss-module__ihfzoa__title a')
            image_element = card.select_one('img[data-testid="item-card-image"]')

            if not image_element:
                image_element = card.select_one('img.item-card-image-module-scss-module__BeJPHq__primaryImage')

            time_element = card.select_one('[id$="-time"]')
            price_element = card.select_one('[data-testid="price"]')

            if not item_id or not link_element or not title_element:
                continue

            image_url = None
            if image_element:
                image_url = image_element.get('src')

            end_date = None
            if time_element:
                end_text = time_element.get_text(separator=' ', strip=True)
                end_text = re.sub(pattern='^Ending time\s*', repl='', string=end_text)
                end_date = dateparser.parse(end_text)

            price = None
            if price_element:
                price_text = price_element.get_text(' ', strip=True)

                # EUR 8.82 -> 8.82
                match = re.search(pattern='([\d.,]+)', string=price_text.replace('\xa0', ' '))

                if match:
                    price = float(
                        match.group(1).replace(',', '')
                    )

            items.append({
                'itemId': int(item_id),
                'itemType': item_type,
                'shortDescription': title_element.get_text(separator=' ', strip=True),
                'itemUrl': link_element.get('href'),
                'imageUrl': image_url,
                'endDate': end_date,
                'price': price,
            })

        return items

    def _get_json_data(self) -> dict:
        url = 'https://www.tradera.com/en/search'

        params = {
            'q': self.search_term,
            'sortBy': 'AddedOn',
        }

        cookies = {
            'preferred_currency': self.currency,
            'shipping_country': 'NL',
            'gdpr_consent_v1': '1:1,2:1,3:1,4:1',
        }

        headers = {
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:152.0) '
                'Gecko/20100101 Firefox/152.0'
            )
        }

        r = httpx.get(
            url=url,
            params=params,
            cookies=cookies,
            headers=headers,
        )
        r.raise_for_status()

        payloads = self.extract_flight_payloads(r.text)

        return {
            'items': self.extract_items(r.text),
            'currencies': self.extract_currencies(payloads),
        }

    def get_auctions(self) -> List[Auction]:
        data = self._get_json_data()

        currency_map = {
            c['code']: c
            for c in data['currencies']
        }

        currency = currency_map[self.currency]

        auctions = []

        for item in data['items']:
            auction_id = str(item['itemId'])
            title = item['shortDescription']
            end_date = item['endDate']
            image_link = item['imageUrl']
            link = item['itemUrl']
            if link.startswith('/'):
                link = f'https://www.tradera.com{link}'

            price = item['price']

            if price is not None:
                symbol = (
                        currency['symbolPrefix']
                        or currency['symbolSuffix']
                )

                if item['itemType'] == 'Auction':
                    description = f'{symbol}{price:.2f} (ending {end_date:%d-%m-%Y %H:%M})'
                else:
                    description = f'{symbol}{price:.2f}'
            else:
                description = ''

            auctions.append(
                Auction(
                    title=title,
                    auction_id=auction_id,
                    description=description,
                    link=link,
                    image_link=image_link,
                )
            )

        return auctions
