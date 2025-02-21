from fastapi import APIRouter
from fastapi_rss import RSSResponse

from auction_extractors.bandcamp import Bandcamp
from auction_extractors.bandcamp_faves import BandcampFaves
from auction_extractors.cashensgap import CashensGap
from auction_extractors.cdandlp import CdAndLp
from auction_extractors.dais import Dais
from auction_extractors.davidtibet import DavidTibet
from auction_extractors.deezer import Deezer
from auction_extractors.discogs_wantlist import DiscogsWantlist
from auction_extractors.discords import Discords
from auction_extractors.eil import EIL
from auction_extractors.hhv import HHV
from auction_extractors.hmv_jp import HMVJapan
from auction_extractors.houseofmythology import HouseOfMythology
from auction_extractors.infinitefog import InfiniteFog
from auction_extractors.japanrecords import JapanRecords
from auction_extractors.juno import Juno
from auction_extractors.kontaktaudio import KontaktAudio
from auction_extractors.kroese import Kroese
from auction_extractors.musicstack import MusicStack
from auction_extractors.platomania import PlatoMania
from auction_extractors.pleasuresofpasttimes import PleasuresOfPastTimes
from auction_extractors.recordmecca import RecordMecca
from auction_extractors.slcd import SLCD
from auction_extractors.tokyomusicjapan import TokyoMusicJapan
from auction_extractors.tracks import Tracks
from auction_extractors.variaworld import Variaworld
from auction_extractors.younggod import YoungGod
from routers.logger import LoggedRoute

router = APIRouter(
    route_class=LoggedRoute,
    default_response_class=RSSResponse,
    tags=['Record shops']
)


@router.get(path='/bandcamp')
def bandcamp_rss(artist: str) -> RSSResponse:
    site = Bandcamp(search_term=artist)
    return site.search()


@router.get(path='/bandcamp_faves')
def bandcamp_faves_rss(username: str) -> RSSResponse:
    site = BandcampFaves(search_term=username)
    return site.search()


@router.get(path='/cashensgap')
def cashensgap_rss() -> RSSResponse:
    site = CashensGap()
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


@router.get(path='/deezer')
def deezer_rss(search_term: str) -> RSSResponse:
    site = Deezer(search_term=search_term)
    return site.search()


@router.get(path='/discogs_wantlist')
async def discogs_wantlist_rss(username: str) -> RSSResponse:
    site = DiscogsWantlist(search_term=username)
    return await site.search()


@router.get(path='/discords')
def discords_rss(search_term: str) -> RSSResponse:
    site = Discords(search_term=search_term)
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


@router.get(path='/kontaktaudio')
def kontaktaudio_rss(search_term: str) -> RSSResponse:
    site = KontaktAudio(search_term=search_term)
    return site.search()


@router.get(path='/kroese')
def kroese_rss(search_term: str) -> RSSResponse:
    site = Kroese(search_term=search_term)
    return site.search()


@router.get(path='/musicstack')
def musicstack_rss(search_term: str) -> RSSResponse:
    site = MusicStack(search_term=search_term)
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


@router.get(path='/younggod')
def younggod_rss(search_term: str, search_in_desc: bool = False) -> RSSResponse:
    site = YoungGod(search_term=search_term, search_in_desc=search_in_desc)
    return site.search()
