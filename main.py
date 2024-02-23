from functools import lru_cache

from fastapi import FastAPI, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi_rss import RSSResponse

from auction_extractors.buyee_mercari import BuyeeMercari
from auction_extractors.buyee_rakuma import BuyeeRakuma
from auction_extractors.buyee_yahoo import BuyeeYahoo
from auction_extractors.cdandlp import CdAndLp
from auction_extractors.delcampe import Delcampe
from auction_extractors.discogs_wantlist import DiscogsWantlist
from auction_extractors.discords import Discords
from auction_extractors.ebay import Ebay, SiteId
from auction_extractors.juno import Juno
from auction_extractors.marktplaats import Marktplaats
from auction_extractors.pleasuresofpasttimes import PleasuresOfPastTimes
from auction_extractors.recordmecca import RecordMecca
from auction_extractors.todocoleccion import Todocoleccion
from auction_extractors.tokyomusicjapan import TokyoMusicJapan
from auction_extractors.tracks import Tracks
from auction_extractors.tweedehands import TweedeHands
from auction_extractors.variaworld import Variaworld
from config import Settings

app = FastAPI(
    title='Auction to RSS',
    version='1.4.0'
)


@app.middleware("http")
async def add_noindex(request: Request, call_next):
    """Adding x-robots-tag to response headers to exclude from search engines."""
    response = await call_next(request)
    response.headers["x-robots-tag"] = 'noindex, nofollow'
    return response


@lru_cache
def get_settings():
    return Settings()


@app.get(path='/', include_in_schema=False)
def docs_redirect():
    return RedirectResponse(url='/docs')


@app.get(path='/2dehands', response_class=RSSResponse)
def tweedehands_rss(search_term: str, search_in_seller_name: bool = False) -> RSSResponse:
    site = TweedeHands(search_term=search_term, search_in_seller_name=search_in_seller_name)
    return site.search()


@app.get(path='/buyee_mercari', response_class=RSSResponse)
async def buyee_mercari_rss(search_term: str,
                            translate_titles: bool = True,
                            settings: Settings = Depends(get_settings)) -> RSSResponse:
    site = BuyeeMercari(
        search_term=search_term,
        translate_titles=translate_titles,
        ms_translate_api_key=settings.ms_translate_api_key,
        ms_translate_api_location=settings.ms_translate_api_location
    )
    return await site.search()


@app.get(path='/buyee__rakuma', response_class=RSSResponse)
def buyee_rakuma_rss(search_term: str) -> RSSResponse:
    site = BuyeeRakuma(search_term=search_term)
    return site.search()


@app.get(path='/buyee_yahoo', response_class=RSSResponse)
async def buyee_yahoo_rss(search_term: str,
                          translate_titles: bool = True,
                          settings: Settings = Depends(get_settings)) -> RSSResponse:
    site = BuyeeYahoo(
        search_term=search_term,
        translate_titles=translate_titles,
        ms_translate_api_key=settings.ms_translate_api_key,
        ms_translate_api_location=settings.ms_translate_api_location
    )
    return await site.search()


@app.get(path='/cdandlp', response_class=RSSResponse)
def cdandlp_rss(search_term: str) -> RSSResponse:
    site = CdAndLp(search_term=search_term)
    return site.search()


@app.get(path='/delcampe_', response_class=RSSResponse)
def delcampe_rss(search_term: str) -> RSSResponse:
    site = Delcampe(search_term=search_term)
    return site.search()


@app.get(path='/discogs_wantlist', response_class=RSSResponse)
async def discogs_wantlist_rss(username: str) -> RSSResponse:
    site = DiscogsWantlist(search_term=username)
    return await site.search()


@app.get(path='/discords', response_class=RSSResponse)
def discords_rss(search_term: str) -> RSSResponse:
    site = Discords(search_term=search_term)
    return site.search()


@app.get(path='/ebay', response_class=RSSResponse)
def ebay_rss(
        search_term: str,
        site_id: SiteId = SiteId.EBAY_US,
        only_locally_listed_items: bool = True,
        settings: Settings = Depends(get_settings)
) -> RSSResponse:
    site = Ebay(
        search_term=search_term,
        app_id=settings.ebay_app_id,
        app_secret=settings.ebay_app_secret,
        ru_name=settings.ebay_ru_name,
        site_id=site_id.value,
        only_locally_listed_items=only_locally_listed_items
    )
    return site.search()


@app.get(path='/juno', response_class=RSSResponse)
def juno_rss(search_term: str) -> RSSResponse:
    site = Juno(search_term=search_term)
    return site.search()


@app.get(path='/marktplaats', response_class=RSSResponse)
def marktplaats_rss(search_term: str, search_in_seller_name: bool = False) -> RSSResponse:
    site = Marktplaats(search_term=search_term, search_in_seller_name=search_in_seller_name)
    return site.search()


@app.get(path='/pleasuresofpasttimes', response_class=RSSResponse)
def pleasuresofpasttimes_rss(search_term: str) -> RSSResponse:
    site = PleasuresOfPastTimes(search_term=search_term)
    return site.search()


@app.get(path='/recordmecca', response_class=RSSResponse)
def recordmecca_rss(search_term: str) -> RSSResponse:
    site = RecordMecca(search_term=search_term)
    return site.search()


@app.get(path='/todocoleccion', response_class=RSSResponse)
def todocoleccion_rss(search_term: str) -> RSSResponse:
    site = Todocoleccion(search_term=search_term)
    return site.search()


@app.get(path='/tokyomusicjapan', response_class=RSSResponse)
def tokyomusicjapan_rss(search_term: str) -> RSSResponse:
    site = TokyoMusicJapan(search_term=search_term)
    return site.search()


@app.get(path='/tracks', response_class=RSSResponse)
def tracks_rss(search_term: str) -> RSSResponse:
    site = Tracks(search_term=search_term)
    return site.search()


@app.get(path='/variaworld', response_class=RSSResponse)
def variaworld_rss(search_term: str) -> RSSResponse:
    site = Variaworld(search_term=search_term)
    return site.search()
