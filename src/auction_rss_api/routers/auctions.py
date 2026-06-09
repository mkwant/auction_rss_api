from typing import Literal, Optional

from fastapi import APIRouter, Depends, Query
from fastapi_rss import RSSResponse
from playwright.async_api import Browser, BrowserContext

from auction_rss_api.app.dependencies import Translate, TranslateLanguage, get_browser
from auction_rss_api.auction_extractors.bonhams import Bonhams
from auction_rss_api.auction_extractors.buyee_mercari import BuyeeMercari
from auction_rss_api.auction_extractors.buyee_rakuma import BuyeeRakuma
from auction_rss_api.auction_extractors.buyee_yahoo import BuyeeYahoo
from auction_rss_api.auction_extractors.catawiki import CataWiki
from auction_rss_api.auction_extractors.christies import Christies
from auction_rss_api.auction_extractors.delcampe import Delcampe
from auction_rss_api.auction_extractors.ebay import Ebay, SiteId
from auction_rss_api.auction_extractors.ewbank import Ewbank
from auction_rss_api.auction_extractors.gottahaverockandroll import GottaHaveRockAndRoll
from auction_rss_api.auction_extractors.gumtree import GumTree
from auction_rss_api.auction_extractors.juliens import JuliensAuctions
from auction_rss_api.auction_extractors.kleinanzeigen import Kleinanzeigen
from auction_rss_api.auction_extractors.lastdodo import LastDodo
from auction_rss_api.auction_extractors.liveauctioneers import LiveAuctioneers
from auction_rss_api.auction_extractors.marktplaats import Marktplaats
from auction_rss_api.auction_extractors.omega import Omega
from auction_rss_api.auction_extractors.rrauction import RRAuction
from auction_rss_api.auction_extractors.sothebys import Sothebys
from auction_rss_api.auction_extractors.subito import Subito
from auction_rss_api.auction_extractors.todocoleccion import Todocoleccion
from auction_rss_api.auction_extractors.tracksauctions import TracksAuctions
from auction_rss_api.auction_extractors.trademe import TradeMe
from auction_rss_api.auction_extractors.tradera import Tradera
from auction_rss_api.auction_extractors.tweedehands import TweedeHands
from auction_rss_api.auction_extractors.vinted import Vinted
from auction_rss_api.routers.logger import LoggedRoute

router = APIRouter(
    route_class=LoggedRoute,
    default_response_class=RSSResponse,
    tags=['Auction sites']
)


@router.get(path='/2dehands')
def tweedehands_rss(
        search_term: str,
        search_in_seller_name: bool = False,
        disable_fuzzy_search: bool = True
) -> RSSResponse:
    site = TweedeHands(
        search_term=search_term,
        search_in_seller_name=search_in_seller_name,
        disable_fuzzy_search=disable_fuzzy_search
    )
    return site.search()


@router.get(path='/bonhams')
def bonhams_rss(search_term: str) -> RSSResponse:
    site = Bonhams(search_term=search_term)
    return site.search()


@router.get("/buyee_mercari")
async def buyee_mercari_rss(
        search_term: str,
        translate: Translate = Depends(),
        browser: BrowserContext = Depends(get_browser),
) -> RSSResponse:
    transformers = []

    if translate.translate_titles:
        transformers.append(
            translate.translate_from(language=TranslateLanguage.JAPANESE)
        )

    site = BuyeeMercari(
        search_term=search_term,
        transformers=transformers,
        browser=browser,
    )

    return await site.search()


@router.get("/buyee_rakuma")
async def buyee_rakuma_rss(
        search_term: str,
        translate: Translate = Depends(),
        browser: BrowserContext = Depends(get_browser),
) -> RSSResponse:
    transformers = []

    if translate.translate_titles:
        transformers.append(
            translate.translate_from(language=TranslateLanguage.JAPANESE)
        )

    site = BuyeeRakuma(
        search_term=search_term,
        transformers=transformers,
        browser=browser,
    )

    return await site.search()


@router.get("/buyee_yahoo")
async def buyee_yahoo_rss(
        search_term: str,
        translate: Translate = Depends(),
        browser: BrowserContext = Depends(get_browser),
) -> RSSResponse:
    transformers = []

    if translate.translate_titles:
        transformers.append(
            translate.translate_from(language=TranslateLanguage.JAPANESE)
        )

    site = BuyeeYahoo(
        search_term=search_term,
        transformers=transformers,
        browser=browser,
    )

    return await site.search()


@router.get(path='/catawiki')
def catawiki_rss(search_term: str) -> RSSResponse:
    site = CataWiki(search_term=search_term)
    return site.search()


@router.get(path='/christies')
def christies_rss(search_term: str) -> RSSResponse:
    site = Christies(search_term=search_term)
    return site.search()


@router.get(path='/delcampe_', include_in_schema=False)  # For backwards compatibility
@router.get(path='/delcampe')
def delcampe_rss(search_term: str) -> RSSResponse:
    site = Delcampe(search_term=search_term)
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


@router.get(path='/ewbank')
def ewbank_rss(search_term: str) -> RSSResponse:
    site = Ewbank(search_term=search_term)
    return site.search()


@router.get(path='/gottahaverockandroll')
def gottahaverockandroll_rss(search_term: str) -> RSSResponse:
    site = GottaHaveRockAndRoll(search_term=search_term)
    return site.search()


@router.get(path='/gumtree')
def gumtree_rss(search_term: str) -> RSSResponse:
    site = GumTree(search_term=search_term)
    return site.search()


@router.get(path='/juliens')
def juliens_rss(search_term: str) -> RSSResponse:
    site = JuliensAuctions(search_term=search_term)
    return site.search()


@router.get(path='/kleinanzeigen')
def kleinanzeigen_rss(search_term: str) -> RSSResponse:
    site = Kleinanzeigen(search_term=search_term)
    return site.search()


@router.get(path='/lastdodo')
def lastdodo_rss(search_term: str) -> RSSResponse:
    site = LastDodo(search_term=search_term)
    return site.search()


@router.get(path='/liveauctioneers')
def liveauctioneers_rss(search_term: str) -> RSSResponse:
    site = LiveAuctioneers(search_term=search_term)
    return site.search()


@router.get(path='/marktplaats')
def marktplaats_rss(
        search_term: str,
        search_in_seller_name: bool = False,
        disable_fuzzy_search: bool = True
) -> RSSResponse:
    site = Marktplaats(
        search_term=search_term,
        search_in_seller_name=search_in_seller_name,
        disable_fuzzy_search=disable_fuzzy_search
    )
    return site.search()


@router.get(path='/omega')
def omega_rss(search_term: str) -> RSSResponse:
    site = Omega(search_term=search_term)
    return site.search()


@router.get(path='/rrauction')
def rrauction_rss(search_term: str) -> RSSResponse:
    site = RRAuction(search_term=search_term)
    return site.search()


@router.get(path='/sothebys')
def sothebys_rss(search_term: str) -> RSSResponse:
    site = Sothebys(search_term=search_term)
    return site.search()


@router.get(path='/subito')
def subito_rss(search_term: str, translate: Translate = Depends()) -> RSSResponse:
    if translate.translate_titles:
        site = Subito(
            search_term=search_term,
            transformers=[translate.translate_from(language=TranslateLanguage.ITALIAN)]
        )
    else:
        site = Subito(search_term=search_term)
    return site.search()


@router.get(path='/todocoleccion')
def todocoleccion_rss(search_term: str, translate: Translate = Depends()) -> RSSResponse:
    if translate.translate_titles:
        site = Todocoleccion(
            search_term=search_term,
            transformers=[translate.translate_from(language=TranslateLanguage.SPANISH)]
        )
    else:
        site = Todocoleccion(search_term=search_term)
    return site.search()


@router.get(path='/tracksauctions')
def tracksauctions_rss(search_term: str) -> RSSResponse:
    site = TracksAuctions(search_term=search_term)
    return site.search()


@router.get(path='/trademe')
def trademe_rss(search_term: str) -> RSSResponse:
    site = TradeMe(search_term=search_term)
    return site.search()


@router.get(path='/tradera')
def tradera_rss(search_term: str, currency: Literal['DKK', 'EUR', 'GBP', 'JPY', 'NOK', 'SEK', 'USD'] = Query(
    default="EUR", enum=['DKK', 'EUR', 'GBP', 'JPY', 'NOK', 'SEK', 'USD']
)) -> RSSResponse:
    site = Tradera(search_term=search_term, currency=currency)
    return site.search()


@router.get(path='/vinted.nl')
def vinted_rss(search_term: str, catalog_id: Optional[int] = None, search_title_only: bool = True) -> RSSResponse:
    site = Vinted(search_term=search_term, catalog_id=catalog_id, search_title_only=search_title_only)
    return site.search()
