import codecs
import json
import re
from typing import List, Literal

import dateutil
import httpx

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
        pushes = re.findall(
            pattern=r"self\.__next_f\.push\(\[(.*?)\]\)",
            string=html,
            flags=re.S,
        )

        decoded_payloads = []

        for p in pushes:
            first_quote = p.find('"')
            last_quote = p.rfind('"')

            if first_quote == -1 or last_quote == -1:
                continue

            raw = p[first_quote + 1:last_quote]

            try:
                decoded = codecs.decode(raw, "unicode_escape")
            except Exception:
                continue

            decoded_payloads.append(decoded)

        return decoded_payloads

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
                        array_str = array_str.encode('latin1').decode('utf-8')  # Fix encoding
                        try:
                            return json.loads(array_str)
                        except json.JSONDecodeError as e:
                            print(f"JSON decode error: {e}")
                            continue
        return []

    @staticmethod
    def extract_items(payloads: list[str]) -> list[dict]:
        for payload in payloads:
            if "discover/receiveSearchResults" in payload:
                try:
                    start = payload.find('"actions"')
                    start = payload.rfind("{", 0, start)

                    depth = 0
                    end = None

                    for i in range(start, len(payload)):
                        if payload[i] == "{":
                            depth += 1
                        elif payload[i] == "}":
                            depth -= 1
                            if depth == 0:
                                end = i + 1
                                break
                    json_str = payload[start:end].encode('latin1').decode('utf-8')  # Fix encoding
                    obj = json.loads(json_str)
                    return obj["actions"][0]["payload"]["result"]["items"]

                except Exception:
                    continue

        return []

    def _get_json_data(self) -> dict:
        url = 'https://www.tradera.com/en/search'
        params = {
            'q': self.search_term,
            'sortBy': 'AddedOn'
        }

        cookies = {
            'preferred_currency': self.currency,
            'shipping_country': 'NL',
            'gdpr_consent_v1': '1:1,2:1,3:1,4:1',
        }

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:152.0) Gecko/20100101 Firefox/152.0'
        }

        r = httpx.get(
            url=url,
            params=params,
            cookies=cookies,
            headers=headers
        )
        r.raise_for_status()

        payloads = self.extract_flight_payloads(r.text)

        items = self.extract_items(payloads)
        currencies = self.extract_currencies(payloads)

        return {
            "items": items,
            "currencies": currencies
        }

    def get_auctions(self) -> List[Auction]:
        data = self._get_json_data()

        currency_map = {c["code"]: c for c in data["currencies"]}
        currency = currency_map[self.currency]

        auctions = []

        for item in data["items"]:
            auction_id = str(item['itemId'])
            title = item['shortDescription']
            image_link = item['imageUrlTemplate'].replace('{format}', 'large-fit')
            link = item['itemUrl'].replace('tradera.com/', 'tradera.com/en/')
            start_date = dateutil.parser.isoparse(item['startDate'])
            seller = item['sellerAlias']

            # Add seller rating to seller if it exists
            try:
                _seller_rating = item['sellerDsrAverage']
                seller += f" ({_seller_rating:.1f})"
            except KeyError:
                pass

            # Build description from pricing info
            _price_auction = (f"{currency['symbolPrefix'] or currency['symbolSuffix']}"
                              f"{item['price'] * currency['rate']:.2f} ({item['totalBids']} bids, ending "
                              f"{dateutil.parser.isoparse(item['endDate']):%d-%m-%Y %H:%M})")
            _price_bin = (f"{currency['symbolPrefix'] or currency['symbolSuffix']}"
                          f"{item['buyNowPrice'] * currency['rate']:.2f} Buy It Now")
            _shipping_options = '\n'.join([(f"- {x['type']}: {currency['symbolPrefix'] or currency['symbolSuffix']}"
                                            f"{x['cost'] * currency['rate']:.2f}")
                                           for x in item['shippingOptions']])
            _price_shipping = f"\nShipping options:\n{_shipping_options}"

            type_desc_mapping = {
                'Auction': [_price_auction, _price_shipping],
                'AuctionBin': [_price_auction, _price_bin, _price_shipping],
                'PureBin': [_price_bin, _price_shipping],
                'ShopItem': [_price_bin, _price_shipping]
            }

            description = '\n'.join(type_desc_mapping.get(item['itemType'], []))

            auctions.append(
                Auction(
                    title=title,
                    auction_id=auction_id,
                    description=description,
                    link=link,
                    image_link=image_link,
                    seller=seller,
                    start_date=start_date
                )
            )
        return auctions
