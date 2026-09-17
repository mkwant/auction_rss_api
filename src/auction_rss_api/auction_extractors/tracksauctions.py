import hashlib
import re
from typing import List

import httpx
from bs4 import BeautifulSoup

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractor


def _solve_pow(nonce: str, difficulty: int) -> int:
    zero_bytes = difficulty >> 1
    odd_nibble = (difficulty & 1) == 1
    solution = 0
    while True:
        digest = hashlib.sha256(f"{nonce}{solution}".encode()).digest()
        if all(b == 0 for b in digest[:zero_bytes]) and (
                not odd_nibble or (digest[zero_bytes] & 0xF0) == 0
        ):
            return solution
        solution += 1


def _pass_bpbc_challenge(client: httpx.Client, url: str, html: str) -> bool:
    """Detects and solves the bpbc proof-of-work gate. Returns True if a
    challenge was present and solved (caller should re-GET the page)."""
    m_nonce = re.search(r'var nonce = "([^"]+)"', html)
    if not m_nonce:
        return False

    token = re.search(r'var challengeToken = "([^"]+)"', html).group(1)
    difficulty = int(re.search(r'var difficulty = (\d+)', html).group(1))
    nonce = m_nonce.group(1)

    solution = _solve_pow(nonce, difficulty)

    verify_url = httpx.URL(url).copy_merge_params({"bpbc_verify": "1"})
    resp = client.post(
        verify_url,
        data={
            "bp_challenge_token": token,
            "bp_challenge_response": str(solution),
            "bot_verify": "1",
        },
    )
    resp.raise_for_status()
    return True


class TracksAuctions(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return 'https://bid.tracksauctions.com/auction/search/?st=bowie&g=-1'

    @property
    def site_desc(self) -> str:
        return 'Tracks Auctions'

    def get_auctions(self) -> List[Auction]:
        auctions = []

        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:156.0) Gecko/20100101 Firefox/156.0"}

        with httpx.Client(headers=headers, follow_redirects=True, timeout=30) as client:
            r = client.get(self.search_link)

            if _pass_bpbc_challenge(client=client, url=self.search_link, html=r.text):
                r = client.get(self.search_link)  # cookie is now set, fetch real page

            soup = BeautifulSoup(r.content, features='html.parser')
            items = soup.select('div.auction-lot')

            for item in items:
                title = item.select_one('span.lot-title').text.strip()
                link = 'https://bid.tracksauctions.com' + item.select_one('p.auction-lot-title>a')['href']
                image_link = item.select_one('div.auction-lot-image img')['src'].replace('-small', '')
                auction_id = hashlib.md5(link.encode('utf-8')).hexdigest()

                _auction_info = item.select('p.auction-lot-title')[1].text.strip().split('(')[1].split(')')[0]

                try:
                    _estimate = item.select_one('div.estimate').text.strip()
                except AttributeError:
                    _estimate = ''

                _desc = item.select_one('p.lot-desc').text.replace('... read more', '').strip() + ' ...'
                description = f'{_auction_info}\n{_estimate}\n\n{_desc}'

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
