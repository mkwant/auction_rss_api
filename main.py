from functools import lru_cache
from typing import Optional

from fastapi import FastAPI, Depends, Query
from fastapi.responses import RedirectResponse
from fastapi_rss import RSSResponse

import config
from auction_extractors.buyee_mercari import BuyeeMercari
from auction_extractors.buyee_yahoo import BuyeeYahoo
from auction_extractors.delcampe import Delcampe
from auction_extractors.ebay import EbayApi, SiteId
from auction_extractors.marktplaats import Marktplaats
from auction_extractors.tweedehands import TweedeHands
from auction_extractors.todocoleccion import Todocoleccion
from rss import generate_rss_response

app = FastAPI(title='Auction to RSS')


@lru_cache
def get_settings():
    return config.Settings()


@app.get('/', include_in_schema=False)
async def docs_redirect():
    return RedirectResponse(url='/docs')


@app.get('/ebay', response_class=RSSResponse)
async def ebay_rss(
        search_term: str,
        site_id: SiteId = SiteId.EBAY_US,
        ebay_app_id: str = Query(description='An Ebay app id. You can request one from https://developer.ebay.com'),
        _settings: config.Settings = Depends(get_settings)
) -> RSSResponse:
    auction_extractor = EbayApi(search_term=search_term, appid=ebay_app_id, site_id=site_id.value)
    return generate_rss_response(auction_extractor=auction_extractor)


@app.get('/marktplaats', response_class=RSSResponse)
async def marktplaats_rss(search_term: str, search_in_seller_name: Optional[bool] = False) -> RSSResponse:
    auction_extractor = Marktplaats(search_term=search_term, search_in_seller_name=search_in_seller_name)
    return generate_rss_response(auction_extractor=auction_extractor)


@app.get('/2dehands', response_class=RSSResponse)
async def tweedehands_rss(search_term: str, search_in_seller_name: Optional[bool] = False) -> RSSResponse:
    auction_extractor = TweedeHands(search_term=search_term, search_in_seller_name=search_in_seller_name)
    return generate_rss_response(auction_extractor=auction_extractor)


@app.get('/todocoleccion', response_class=RSSResponse)
async def todocoleccion_rss(search_term: str) -> RSSResponse:
    auction_extractor = Todocoleccion(search_term=search_term)
    return generate_rss_response(auction_extractor=auction_extractor)


@app.get('/delcampe', response_class=RSSResponse)
async def delcampe_rss(search_term: str) -> RSSResponse:
    auction_extractor = Delcampe(search_term=search_term)
    return generate_rss_response(auction_extractor=auction_extractor)


@app.get('/buyee_mercari', response_class=RSSResponse)
async def buyee_mercari_rss(search_term: str) -> RSSResponse:
    auction_extractor = BuyeeMercari(search_term=search_term)
    return generate_rss_response(auction_extractor=auction_extractor)


@app.get('/buyee_yahoo', response_class=RSSResponse)
async def buyee_yahoo_rss(search_term: str) -> RSSResponse:
    auction_extractor = BuyeeYahoo(search_term=search_term)
    return generate_rss_response(auction_extractor=auction_extractor)
