from fastapi import APIRouter, Depends
from fastapi_rss import RSSResponse

from auction_rss_api.app.dependencies import Translate, TranslateLanguage
from auction_rss_api.auction_extractors.anonne import Anonne
from auction_rss_api.auction_extractors.artunlimited import ArtunLimited
from auction_rss_api.auction_extractors.atlasrecords import AtlasRecords
from auction_rss_api.auction_extractors.audiophileusa import AudiophileUSA
from auction_rss_api.auction_extractors.backstage import BackStage
from auction_rss_api.auction_extractors.bandcamp import Bandcamp
from auction_rss_api.auction_extractors.bandcamp_faves import BandcampFaves
from auction_rss_api.auction_extractors.boilerroom import BoilerRoom
from auction_rss_api.auction_extractors.cashensgap import CashensGap
from auction_rss_api.auction_extractors.cdandlp import CdAndLp
from auction_rss_api.auction_extractors.dais import Dais
from auction_rss_api.auction_extractors.davidbowie import DavidBowie
from auction_rss_api.auction_extractors.davidtibet import DavidTibet
from auction_rss_api.auction_extractors.deezer import Deezer
from auction_rss_api.auction_extractors.discogs_wantlist import DiscogsWantlist
from auction_rss_api.auction_extractors.discords import Discords
from auction_rss_api.auction_extractors.diskunion import DiskUnion
from auction_rss_api.auction_extractors.diskunion_used import DiskUnionUsed
from auction_rss_api.auction_extractors.eil import EIL
from auction_rss_api.auction_extractors.evilgreed import EvilGreed
from auction_rss_api.auction_extractors.foetus import Foetus
from auction_rss_api.auction_extractors.hhv import HHV
from auction_rss_api.auction_extractors.hmv_jp import HMVJapan
from auction_rss_api.auction_extractors.hotstuff import HotStuff
from auction_rss_api.auction_extractors.houseofmythology import HouseOfMythology
from auction_rss_api.auction_extractors.ideanow import IdeaNow
from auction_rss_api.auction_extractors.imusic import Imusic
from auction_rss_api.auction_extractors.infinitefog import InfiniteFog
from auction_rss_api.auction_extractors.japanrecords import JapanRecords
from auction_rss_api.auction_extractors.japanrecordvinyl import JapanRecordVinyl
from auction_rss_api.auction_extractors.juno import Juno
from auction_rss_api.auction_extractors.kent import Kent
from auction_rss_api.auction_extractors.kontaktaudio import KontaktAudio
from auction_rss_api.auction_extractors.kroese import Kroese
from auction_rss_api.auction_extractors.magicbus import MagicbusExtractor
from auction_rss_api.auction_extractors.memorabiliauk import MemorabiliaUk
from auction_rss_api.auction_extractors.montreuxjazzshop import MontreuxJazzShop
from auction_rss_api.auction_extractors.musichug import MusicHug
from auction_rss_api.auction_extractors.musicstack import MusicStack
from auction_rss_api.auction_extractors.newburycomics import NewBuryComics
from auction_rss_api.auction_extractors.platomania import PlatoMania
from auction_rss_api.auction_extractors.platomania_exclusives import PlatomaniaExclusives
from auction_rss_api.auction_extractors.pleasuresofpasttimes import PleasuresOfPastTimes
from auction_rss_api.auction_extractors.rarevinyl import RareVinyl
from auction_rss_api.auction_extractors.recordmecca import RecordMecca
from auction_rss_api.auction_extractors.redeye import RedEye
from auction_rss_api.auction_extractors.rockabuy import RockaBuy
from auction_rss_api.auction_extractors.rockaway import Rockaway
from auction_rss_api.auction_extractors.roughtrade import RoughTrade
from auction_rss_api.auction_extractors.slcd import SLCD
from auction_rss_api.auction_extractors.soisong import Soisong
from auction_rss_api.auction_extractors.thehague3345 import TheHague3345
from auction_rss_api.auction_extractors.tokyomusicjapan import TokyoMusicJapan
from auction_rss_api.auction_extractors.tracks import Tracks
from auction_rss_api.auction_extractors.vandabowie import VandaBowie
from auction_rss_api.auction_extractors.vandacollection import VandaCollection
from auction_rss_api.auction_extractors.variaworld import Variaworld
from auction_rss_api.auction_extractors.vinylalert import VinylAlert
from auction_rss_api.auction_extractors.vinyleers import Vinyleers
from auction_rss_api.auction_extractors.vinylmania import VinylmaniaExtractor
from auction_rss_api.auction_extractors.waaghals import Waaghals
from auction_rss_api.auction_extractors.woodenchild import WoodenChild
from auction_rss_api.auction_extractors.younggod import YoungGod
from auction_rss_api.routers.logger import LoggedRoute

router = APIRouter(
    route_class=LoggedRoute,
    default_response_class=RSSResponse,
    tags=['Record shops']
)


@router.get(path='/3345')
def thehague3345_rss(search_term: str) -> RSSResponse:
    site = TheHague3345(search_term=search_term)
    return site.search()


@router.get(path='/anonne')
def anonne_rss() -> RSSResponse:
    site = Anonne()
    return site.search()


@router.get(path='/artunlimited')
def artunlimited_rss(search_term: str) -> RSSResponse:
    site = ArtunLimited(search_term=search_term)
    return site.search()


@router.get(path='/atlasrecords')
def atlasrecords_rss(search_term: str) -> RSSResponse:
    site = AtlasRecords(search_term=search_term)
    return site.search()


@router.get(path='/audiophileusa')
def audiophileusa_rss(search_term: str) -> RSSResponse:
    site = AudiophileUSA(search_term=search_term)
    return site.search()


@router.get(path='/backstage')
def backstage_rss(search_term: str) -> RSSResponse:
    site = BackStage(search_term=search_term)
    return site.search()


@router.get(path='/bandcamp')
def bandcamp_rss(artist: str) -> RSSResponse:
    site = Bandcamp(search_term=artist)
    return site.search()


@router.get(path='/bandcamp_faves')
def bandcamp_faves_rss(username: str) -> RSSResponse:
    site = BandcampFaves(search_term=username)
    return site.search()


@router.get(path='/boilerroom')
def boilerroom_rss(search_term: str) -> RSSResponse:
    site = BoilerRoom(search_term=search_term)
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


@router.get(path='/davidbowie')
def davidbowie_rss() -> RSSResponse:
    site = DavidBowie()
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


@router.get(path='/diskunion')
def diskunion_rss(artist_id: str, translate: Translate = Depends()) -> RSSResponse:
    if translate.translate_titles:
        site = DiskUnion(
            search_term=artist_id,
            transformers=[translate.translate_from(language=TranslateLanguage.JAPANESE)]
        )
    else:
        site = DiskUnion(search_term=artist_id)
    return site.search()


@router.get(path='/diskunion_used')
def diskunion_used_rss(artist_id: str, translate: Translate = Depends()) -> RSSResponse:
    if translate.translate_titles:
        site = DiskUnionUsed(
            search_term=artist_id,
            transformers=[translate.translate_from(language=TranslateLanguage.JAPANESE)]
        )
    else:
        site = DiskUnionUsed(search_term=artist_id)
    return site.search()


@router.get(path='/eil')
def eil_rss(search_term: str) -> RSSResponse:
    site = EIL(search_term=search_term)
    return site.search()


@router.get(path='/evilgreed')
def evilgreed_rss(collection: str) -> RSSResponse:
    site = EvilGreed(search_term=None, collection=collection)
    return site.search()


@router.get(path='/foetus')
def foetus_rss() -> RSSResponse:
    site = Foetus()
    return site.search()


@router.get(path='/hhv')
def hhv_rss(search_term: str) -> RSSResponse:
    site = HHV(search_term=search_term)
    return site.search()


@router.get(path='/hmvjapan')
def hmvjapan_rss(search_term: str) -> RSSResponse:
    site = HMVJapan(search_term=search_term)
    return site.search()


@router.get(path='/hotstuff')
def hotstuff_rss(search_term: str) -> RSSResponse:
    site = HotStuff(search_term=search_term)
    return site.search()


@router.get(path='/houseofmythology')
def houseofmythology_rss(search_term: str) -> RSSResponse:
    site = HouseOfMythology(search_term=search_term)
    return site.search()


@router.get(path='/ideanow')
def ideanow_rss(search_term: str) -> RSSResponse:
    site = IdeaNow(search_term=search_term)
    return site.search()


@router.get(path='/imusic')
def imusic_rss(search_term: str) -> RSSResponse:
    site = Imusic(search_term=search_term)
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


@router.get(path='/japanrecordvinyl')
def japanrecordvinyl_rss(search_term: str) -> RSSResponse:
    site = JapanRecordVinyl(search_term=search_term)
    return site.search()


@router.get(path='/juno')
def juno_rss(search_term: str) -> RSSResponse:
    site = Juno(search_term=search_term)
    return site.search()


@router.get(path='/kent')
def kent_rss(search_term: str) -> RSSResponse:
    site = Kent(search_term=search_term)
    return site.search()


@router.get(path='/kontaktaudio')
def kontaktaudio_rss(search_term: str) -> RSSResponse:
    site = KontaktAudio(search_term=search_term)
    return site.search()


@router.get(path='/kroese')
def kroese_rss(search_term: str) -> RSSResponse:
    site = Kroese(search_term=search_term)
    return site.search()


@router.get(path='/magicbus')
def magicbus_rss(search_term: str) -> RSSResponse:
    site = MagicbusExtractor(search_term=search_term)
    return site.search()


@router.get(path='/memorabiliauk')
def memorabiliauk_rss(search_term: str) -> RSSResponse:
    site = MemorabiliaUk(search_term=search_term)
    return site.search()


@router.get(path='/montreuxjazzshop')
def montreuxjazzshop_rss(search_term: str) -> RSSResponse:
    site = MontreuxJazzShop(search_term=search_term)
    return site.search()


@router.get(path='/musichug')
def musichug_rss(search_term: str) -> RSSResponse:
    site = MusicHug(search_term=search_term)
    return site.search()


@router.get(path='/musicstack')
def musicstack_rss(search_term: str) -> RSSResponse:
    site = MusicStack(search_term=search_term)
    return site.search()


@router.get(path='/newburycomics')
def newburycomics_rss() -> RSSResponse:
    site = NewBuryComics()
    return site.search()


@router.get(path='/platomania')
def platomania_rss(search_term: str) -> RSSResponse:
    site = PlatoMania(search_term=search_term)
    return site.search()


@router.get(path='/platomania_exclusives')
def platomania_exclusives_rss() -> RSSResponse:
    site = PlatomaniaExclusives()
    return site.search()


@router.get(path='/pleasuresofpasttimes')
def pleasuresofpasttimes_rss(search_term: str) -> RSSResponse:
    site = PleasuresOfPastTimes(search_term=search_term)
    return site.search()


@router.get(path='/rarevinyl')
def rarevinyl_rss(search_term: str) -> RSSResponse:
    site = RareVinyl(search_term=search_term)
    return site.search()


@router.get(path='/recordmecca')
def recordmecca_rss(search_term: str) -> RSSResponse:
    site = RecordMecca(search_term=search_term)
    return site.search()


@router.get(path='/redeye')
def redeye_rss(search_term: str) -> RSSResponse:
    site = RedEye(search_term=search_term)
    return site.search()


@router.get(path='/rockabuy')
def rockabuy_rss(search_term: str) -> RSSResponse:
    site = RockaBuy(search_term=search_term)
    return site.search()


@router.get(path='/rockaway')
def rockaway_rss(search_term: str) -> RSSResponse:
    site = Rockaway(search_term=search_term)
    return site.search()


@router.get(path='/slcd')
def slcd_rss(search_term: str) -> RSSResponse:
    site = SLCD(search_term=search_term)
    return site.search()


@router.get(path='/roughtrade')
def roughtrade_rss(
        search_term: str | None = None,
        available_only: bool = False,
        exclusives_only: bool = False,
) -> RSSResponse:
    site = RoughTrade(search_term=search_term, available_only=available_only, exclusives_only=exclusives_only)
    return site.search()


@router.get(path='/soisong')
def soisong_rss() -> RSSResponse:
    site = Soisong()
    return site.search()


@router.get(path='/tokyomusicjapan')
def tokyomusicjapan_rss(search_term: str) -> RSSResponse:
    site = TokyoMusicJapan(search_term=search_term)
    return site.search()


@router.get(path='/tracks')
def tracks_rss(search_term: str) -> RSSResponse:
    site = Tracks(search_term=search_term)
    return site.search()


@router.get(path='/vandabowie')
def vandabowie_rss() -> RSSResponse:
    site = VandaBowie()
    return site.search()


@router.get(path='/vandacollection')
def vandacollection_rss(category: str = 'THES394093') -> RSSResponse:
    site = VandaCollection(search_term=category)
    return site.search()


@router.get(path='/variaworld')
def variaworld_rss(search_term: str) -> RSSResponse:
    site = Variaworld(search_term=search_term)
    return site.search()


@router.get(path='/vinylalert')
def vinylalert_rss(search_term: str | None = None) -> RSSResponse:
    site = VinylAlert(search_term=search_term)
    return site.search()


@router.get(path='/vinyleers')
def vinyleers_rss(search_term: str) -> RSSResponse:
    site = Vinyleers(search_term=search_term)
    return site.search()


@router.get(path='/vinylmania')
def vinylmania_rss(search_term: str) -> RSSResponse:
    site = VinylmaniaExtractor(search_term=search_term)
    return site.search()


@router.get(path='/younggod')
def younggod_rss(search_term: str, search_in_desc: bool = False) -> RSSResponse:
    site = YoungGod(search_term=search_term, search_in_desc=search_in_desc)
    return site.search()


@router.get(path='/waaghals')
def waaghals_rss(collection: str) -> RSSResponse:
    site = Waaghals(collection=collection)
    return site.search()


@router.get(path='/woodenchild')
def woodenchild_rss() -> RSSResponse:
    site = WoodenChild()
    return site.search()
