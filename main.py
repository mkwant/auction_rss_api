from functools import lru_cache
from typing import Optional

from fastapi import FastAPI, Depends
from fastapi.responses import RedirectResponse
from fastapi_rss import RSSResponse

from auction_extractors.buyee_mercari import BuyeeMercari
from auction_extractors.buyee_yahoo import BuyeeYahoo
from auction_extractors.cdandlp import CdAndLp
from auction_extractors.delcampe import Delcampe
from auction_extractors.discogs_wantlist import DiscogsWantlist
from auction_extractors.ebay import EbayApi, SiteId
from auction_extractors.juno import Juno
from auction_extractors.marktplaats import Marktplaats
from auction_extractors.todocoleccion import Todocoleccion
from auction_extractors.tweedehands import TweedeHands
from config import Settings
from rss import generate_rss_response

app = FastAPI(title='Auction to RSS')


@lru_cache
def get_settings():
    return Settings()


@app.get('/', include_in_schema=False)
def docs_redirect():
    return RedirectResponse(url='/docs')


@app.get('/2dehands', response_class=RSSResponse)
def tweedehands_rss(search_term: str, search_in_seller_name: Optional[bool] = False) -> RSSResponse:
    auction_extractor = TweedeHands(search_term=search_term, search_in_seller_name=search_in_seller_name)
    auction_search_response = auction_extractor.search()
    return generate_rss_response(auction_search_response=auction_search_response)


@app.get('/buyee_mercari', response_class=RSSResponse)
async def buyee_mercari_rss(search_term: str,
                            translate_titles: bool = True,
                            settings: Settings = Depends(get_settings)) -> RSSResponse:
    auction_extractor = BuyeeMercari(search_term=search_term,
                                     translate_titles=translate_titles,
                                     ms_translate_api_key=settings.ms_translate_api_key,
                                     ms_translate_api_location=settings.ms_translate_api_location)
    auction_search_response = await auction_extractor.search()
    return generate_rss_response(auction_search_response=auction_search_response)


@app.get('/buyee_yahoo_', response_class=RSSResponse)
async def buyee_yahoo_rss(search_term: str,
                          translate_titles: bool = True,
                          settings: Settings = Depends(get_settings)) -> RSSResponse:
    auction_extractor = BuyeeYahoo(search_term=search_term,
                                   translate_titles=translate_titles,
                                   ms_translate_api_key=settings.ms_translate_api_key,
                                   ms_translate_api_location=settings.ms_translate_api_location)
    auction_search_response = await auction_extractor.search()
    return generate_rss_response(auction_search_response=auction_search_response)


@app.get('/cdandlp', response_class=RSSResponse)
def cdandlp_rss(search_term: str) -> RSSResponse:
    auction_extractor = CdAndLp(search_term=search_term)
    auction_search_response = auction_extractor.search()
    return generate_rss_response(auction_search_response=auction_search_response)


@app.get('/delcampe_', response_class=RSSResponse)
def delcampe_rss(search_term: str) -> RSSResponse:
    auction_extractor = Delcampe(search_term=search_term)
    auction_search_response = auction_extractor.search()
    return generate_rss_response(auction_search_response=auction_search_response)


@app.get('/discogs_wantlist', response_class=RSSResponse)
async def discogs_wantlist_rss(username: str) -> RSSResponse:
    auction_extractor = DiscogsWantlist(search_term=username)
    auction_search_response = await auction_extractor.search()
    return generate_rss_response(auction_search_response=auction_search_response)


@app.get('/ebay', response_class=RSSResponse)
def ebay_rss(
        search_term: str,
        site_id: SiteId = SiteId.EBAY_US,
        settings: Settings = Depends(get_settings)
) -> RSSResponse:
    auction_extractor = EbayApi(search_term=search_term, appid=settings.ebay_app_id, site_id=site_id.value)
    auction_search_response = auction_extractor.search()
    return generate_rss_response(auction_search_response=auction_search_response)


@app.get('/juno', response_class=RSSResponse)
def juno_rss(search_term: str) -> RSSResponse:
    auction_extractor = Juno(search_term=search_term)
    auction_search_response = auction_extractor.search()
    return generate_rss_response(auction_search_response=auction_search_response)


@app.get('/marktplaats', response_class=RSSResponse)
def marktplaats_rss(search_term: str, search_in_seller_name: Optional[bool] = False) -> RSSResponse:
    auction_extractor = Marktplaats(search_term=search_term, search_in_seller_name=search_in_seller_name)
    auction_search_response = auction_extractor.search()
    return generate_rss_response(auction_search_response=auction_search_response)


@app.get('/todocoleccion', response_class=RSSResponse)
def todocoleccion_rss(search_term: str) -> RSSResponse:
    auction_extractor = Todocoleccion(search_term=search_term)
    auction_search_response = auction_extractor.search()
    return generate_rss_response(auction_search_response=auction_search_response)
