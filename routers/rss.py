from functools import lru_cache

from fastapi import APIRouter, Depends
from fastapi_rss import RSSResponse

from app.settings import Settings
from auction_extractors.buyee_mercari import BuyeeMercari
from auction_extractors.buyee_rakuma import BuyeeRakuma
from auction_extractors.buyee_yahoo import BuyeeYahoo
from auction_extractors.cdandlp import CdAndLp
from auction_extractors.delcampe import Delcampe
from auction_extractors.discogs_wantlist import DiscogsWantlist
from auction_extractors.discords import Discords
from auction_extractors.ebay import SiteId, Ebay
from auction_extractors.juno import Juno
from auction_extractors.marktplaats import Marktplaats
from auction_extractors.pleasuresofpasttimes import PleasuresOfPastTimes
from auction_extractors.recordmecca import RecordMecca
from auction_extractors.todocoleccion import Todocoleccion
from auction_extractors.tokyomusicjapan import TokyoMusicJapan
from auction_extractors.tracks import Tracks
from auction_extractors.tweedehands import TweedeHands
from auction_extractors.variaworld import Variaworld
from dependencies.translate import Translate


@lru_cache
def get_settings():
    return Settings()


router = APIRouter(
    default_response_class=RSSResponse,
    tags=['RSS-feeds']
)


@router.get(path='/2dehands')
def tweedehands_rss(search_term: str, search_in_seller_name: bool = False) -> RSSResponse:
    site = TweedeHands(
        search_term=search_term,
        search_in_seller_name=search_in_seller_name
    )
    return site.search()


@router.get(path='/buyee_mercari')
def buyee_mercari_rss(search_term: str, translate: Translate = Depends(Translate)) -> RSSResponse:
    site = BuyeeMercari(search_term=search_term, translate_titles=translate.translate_titles, translate_from='ja')
    return site.search()


@router.get(path='/buyee__rakuma')
def buyee_rakuma_rss(search_term: str, translate: Translate = Depends(Translate)) -> RSSResponse:
    site = BuyeeRakuma(search_term=search_term, translate_titles=translate.translate_titles, translate_from='ja')
    return site.search()


@router.get(path='/buyee__yahoo', include_in_schema=False)  # For backwards compatibility
@router.get(path='/buyee_yahoo')
def buyee_yahoo_rss(search_term: str, translate: Translate = Depends(Translate)) -> RSSResponse:
    site = BuyeeYahoo(search_term=search_term, translate_titles=translate.translate_titles, translate_from='ja')
    return site.search()


@router.get(path='/cdandlp')
def cdandlp_rss(search_term: str) -> RSSResponse:
    site = CdAndLp(search_term=search_term)
    return site.search()


@router.get(path='/delcampe_')
def delcampe_rss(search_term: str) -> RSSResponse:
    site = Delcampe(search_term=search_term)
    return site.search()


@router.get(path='/discogs_wantlist')
async def discogs_wantlist_rss(username: str) -> RSSResponse:
    site = DiscogsWantlist(search_term=username)
    return await site.search()


@router.get(path='/discords')
def discords_rss(search_term: str) -> RSSResponse:
    site = Discords(search_term=search_term)
    return site.search()


@router.get(path='/ebay')
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


@router.get(path='/juno')
def juno_rss(search_term: str) -> RSSResponse:
    site = Juno(search_term=search_term)
    return site.search()


@router.get(path='/marktplaats')
def marktplaats_rss(search_term: str, search_in_seller_name: bool = False) -> RSSResponse:
    site = Marktplaats(
        search_term=search_term,
        search_in_seller_name=search_in_seller_name
    )
    return site.search()


@router.get(path='/pleasuresofpasttimes')
def pleasuresofpasttimes_rss(search_term: str) -> RSSResponse:
    site = PleasuresOfPastTimes(search_term=search_term)
    return site.search()


@router.get(path='/recordmecca')
def recordmecca_rss(search_term: str) -> RSSResponse:
    site = RecordMecca(search_term=search_term)
    return site.search()


@router.get(path='/todocoleccion')
def todocoleccion_rss(search_term: str, translate: Translate = Depends(Translate)) -> RSSResponse:
    site = Todocoleccion(search_term=search_term, translate_titles=translate.translate_titles, translate_from='es')
    return site.search()


@router.get(path='/tokyomusicjapan')
def tokyomusicjapan_rss(search_term: str) -> RSSResponse:
    site = TokyoMusicJapan(search_term=search_term)
    return site.search()


@router.get(path='/tracks')
def tracks_rss(search_term: str) -> RSSResponse:
    site = Tracks(search_term=search_term)
    return site.search()


@router.get(path='/variaworld')
def variaworld_rss(search_term: str) -> RSSResponse:
    site = Variaworld(search_term=search_term)
    return site.search()
