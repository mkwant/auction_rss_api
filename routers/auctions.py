from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi_rss import RSSResponse

from app.dependencies import Translate
from auction_extractors.bandcamp import Bandcamp
from auction_extractors.bandcamp_faves import BandcampFaves
from auction_extractors.buyee_mercari import BuyeeMercari
from auction_extractors.buyee_rakuma import BuyeeRakuma
from auction_extractors.buyee_yahoo import BuyeeYahoo
from auction_extractors.catawiki import CataWiki
from auction_extractors.cdandlp import CdAndLp
from auction_extractors.dais import Dais
from auction_extractors.davidtibet import DavidTibet
from auction_extractors.delcampe import Delcampe
from auction_extractors.discogs_wantlist import DiscogsWantlist
from auction_extractors.discords import Discords
from auction_extractors.ebay import SiteId, Ebay
from auction_extractors.eil import EIL
from auction_extractors.hhv import HHV
from auction_extractors.hmv_jp import HMVJapan
from auction_extractors.houseofmythology import HouseOfMythology
from auction_extractors.infinitefog import InfiniteFog
from auction_extractors.japanrecords import JapanRecords
from auction_extractors.juno import Juno
from auction_extractors.kleinanzeigen import Kleinanzeigen
from auction_extractors.kontaktaudio import KontaktAudio
from auction_extractors.marktplaats import Marktplaats
from auction_extractors.musicstack import MusicStack
from auction_extractors.omega import Omega
from auction_extractors.platomania import PlatoMania
from auction_extractors.pleasuresofpasttimes import PleasuresOfPastTimes
from auction_extractors.recordmecca import RecordMecca
from auction_extractors.slcd import SLCD
from auction_extractors.todocoleccion import Todocoleccion
from auction_extractors.tokyomusicjapan import TokyoMusicJapan
from auction_extractors.tracks import Tracks
from auction_extractors.tradera import Tradera
from auction_extractors.tweedehands import TweedeHands
from auction_extractors.variaworld import Variaworld
from auction_extractors.vinted import Vinted
from auction_extractors.younggod import YoungGod
from auction_transformers.translator import translate_from_jp, translate_from_es
from routers.logger import LoggedRoute

router = APIRouter(
    route_class=LoggedRoute,
    default_response_class=RSSResponse,
    tags=['Auction sites']
)


@router.get(path='/2dehands')
def tweedehands_rss(search_term: str, search_in_seller_name: bool = False) -> RSSResponse:
    site = TweedeHands(
        search_term=search_term,
        search_in_seller_name=search_in_seller_name
    )
    return site.search()


@router.get(path='/bandcamp')
def bandcamp_rss(artist: str) -> RSSResponse:
    site = Bandcamp(search_term=artist)
    return site.search()


@router.get(path='/bandcamp_faves')
def bandcamp_faves_rss(username: str) -> RSSResponse:
    site = BandcampFaves(search_term=username)
    return site.search()


@router.get(path='/buyee_mercari')
def buyee_mercari_rss(search_term: str, translate: Translate = Depends(Translate)) -> RSSResponse:
    if translate.translate_titles:
        site = BuyeeMercari(search_term=search_term, transformers=[translate_from_jp])
    else:
        site = BuyeeMercari(search_term=search_term)
    return site.search()


@router.get(path='/buyee__rakuma', include_in_schema=False)  # For backwards compatibility
@router.get(path='/buyee_rakuma')
def buyee_rakuma_rss(search_term: str, translate: Translate = Depends(Translate)) -> RSSResponse:
    if translate.translate_titles:
        site = BuyeeRakuma(search_term=search_term, transformers=[translate_from_jp])
    else:
        site = BuyeeRakuma(search_term=search_term)
    return site.search()


@router.get(path='/buyee__yahoo', include_in_schema=False)  # For backwards compatibility
@router.get(path='/buyee_yahoo')
def buyee_yahoo_rss(search_term: str, translate: Translate = Depends(Translate)) -> RSSResponse:
    if translate.translate_titles:
        site = BuyeeYahoo(search_term=search_term, transformers=[translate_from_jp])
    else:
        site = BuyeeYahoo(search_term=search_term)
    return site.search()


@router.get(path='/catawiki')
def catawiki_rss(search_term: str) -> RSSResponse:
    site = CataWiki(search_term=search_term)
    return site.search()


@router.get(path='/cdandlp')
def cdandlp_rss(search_term: str) -> RSSResponse:
    site = CdAndLp(search_term=search_term)
    return site.search()


@router.get(path='/dais')
def dais_rss(search_term: str, search_in_desc: bool = False) -> RSSResponse:
    site = Dais(search_term=search_term, search_in_desc=search_in_desc)
    return site.search()


@router.get(path='/davidtibet')
def davidtibet_rss(search_term: str) -> RSSResponse:
    site = DavidTibet(search_term=search_term)
    return site.search()


@router.get(path='/delcampe_', include_in_schema=False)  # For backwards compatibility
@router.get(path='/delcampe')
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
        only_locally_listed_items: bool = True
) -> RSSResponse:
    site = Ebay(
        search_term=search_term,
        site_id=site_id.value,
        only_locally_listed_items=only_locally_listed_items
    )
    return site.search()


@router.get(path='/eil')
def eil_rss(search_term: str) -> RSSResponse:
    site = EIL(search_term=search_term)
    return site.search()


@router.get(path='/hhv')
def hhv_rss(search_term: str) -> RSSResponse:
    site = HHV(search_term=search_term)
    return site.search()


@router.get(path='/hmvjapan')
def hmvjapan_rss(search_term: str) -> RSSResponse:
    site = HMVJapan(search_term=search_term)
    return site.search()


@router.get(path='/houseofmythology')
def houseofmythology_rss(search_term: str) -> RSSResponse:
    site = HouseOfMythology(search_term=search_term)
    return site.search()


@router.get(path='/infinitefog')
def infinitefog_rss(search_term: str) -> RSSResponse:
    site = InfiniteFog(search_term=search_term)
    return site.search()


@router.get(path='/japanrecords_', include_in_schema=False)  # For backwards compatibility
@router.get(path='/japanrecords')
def japanrecords_rss(search_term: str) -> RSSResponse:
    site = JapanRecords(search_term=search_term)
    return site.search()


@router.get(path='/juno')
def juno_rss(search_term: str) -> RSSResponse:
    site = Juno(search_term=search_term)
    return site.search()


@router.get(path='/kleinanzeigen')
def kleinanzeigen_rss(search_term: str) -> RSSResponse:
    site = Kleinanzeigen(search_term=search_term)
    return site.search()


@router.get(path='/kontaktaudio')
def kontaktaudio_rss(search_term: str) -> RSSResponse:
    site = KontaktAudio(search_term=search_term)
    return site.search()


@router.get(path='/marktplaats')
def marktplaats_rss(search_term: str, search_in_seller_name: bool = False) -> RSSResponse:
    site = Marktplaats(
        search_term=search_term,
        search_in_seller_name=search_in_seller_name
    )
    return site.search()


@router.get(path='/musicstack')
def musicstack_rss(search_term: str) -> RSSResponse:
    site = MusicStack(search_term=search_term)
    return site.search()


@router.get(path='/omega')
def omega_rss(search_term: str) -> RSSResponse:
    site = Omega(search_term=search_term)
    return site.search()


@router.get(path='/platomania')
def platomania_rss(search_term: str) -> RSSResponse:
    site = PlatoMania(search_term=search_term)
    return site.search()


@router.get(path='/pleasuresofpasttimes')
def pleasuresofpasttimes_rss(search_term: str) -> RSSResponse:
    site = PleasuresOfPastTimes(search_term=search_term)
    return site.search()


@router.get(path='/recordmecca')
def recordmecca_rss(search_term: str) -> RSSResponse:
    site = RecordMecca(search_term=search_term)
    return site.search()


@router.get(path='/slcd')
def slcd_rss(search_term: str) -> RSSResponse:
    site = SLCD(search_term=search_term)
    return site.search()


@router.get(path='/todocoleccion')
def todocoleccion_rss(search_term: str, translate: Translate = Depends(Translate)) -> RSSResponse:
    if translate.translate_titles:
        site = Todocoleccion(search_term=search_term, transformers=[translate_from_es])
    else:
        site = Todocoleccion(search_term=search_term)
    return site.search()


@router.get(path='/tokyomusicjapan')
def tokyomusicjapan_rss(search_term: str) -> RSSResponse:
    site = TokyoMusicJapan(search_term=search_term)
    return site.search()


@router.get(path='/tracks')
def tracks_rss(search_term: str) -> RSSResponse:
    site = Tracks(search_term=search_term)
    return site.search()


@router.get(path='/tradera')
def tradera_rss(search_term: str, currency: str = Query(
    default="EUR", enum=['DKK', 'EUR', 'GBP', 'JPY', 'NOK', 'SEK', 'USD']
)) -> RSSResponse:
    site = Tradera(search_term=search_term, currency=currency)
    return site.search()


@router.get(path='/variaworld')
def variaworld_rss(search_term: str) -> RSSResponse:
    site = Variaworld(search_term=search_term)
    return site.search()


@router.get(path='/vinted.nl')
def vinted_rss(search_term: str, catalog_id: Optional[int] = None, search_title_only: bool = True) -> RSSResponse:
    site = Vinted(search_term=search_term, catalog_id=catalog_id, search_title_only=search_title_only)
    return site.search()


@router.get(path='/younggod')
def younggod_rss(search_term: str, search_in_desc: bool = False) -> RSSResponse:
    site = YoungGod(search_term=search_term, search_in_desc=search_in_desc)
    return site.search()
