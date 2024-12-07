from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi_rss import RSSResponse

from app.dependencies import Translate
from auction_extractors.buyee_mercari import BuyeeMercari
from auction_extractors.buyee_rakuma import BuyeeRakuma
from auction_extractors.buyee_yahoo import BuyeeYahoo
from auction_extractors.catawiki import CataWiki
from auction_extractors.delcampe import Delcampe
from auction_extractors.ebay import SiteId, Ebay
from auction_extractors.ebay_tst import EbayTest
from auction_extractors.kleinanzeigen import Kleinanzeigen
from auction_extractors.marktplaats import Marktplaats
from auction_extractors.omega import Omega
from auction_extractors.todocoleccion import Todocoleccion
from auction_extractors.tradera import Tradera
from auction_extractors.tweedehands import TweedeHands
from auction_extractors.vinted import Vinted
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


@router.get(path='/ebay_tst')
def ebay_test_rss(
        search_term: str,
        site_id: SiteId = SiteId.EBAY_US,
        only_locally_listed_items: bool = True
) -> RSSResponse:
    site = EbayTest(
        search_term=search_term,
        site_id=site_id.value,
        only_locally_listed_items=only_locally_listed_items
    )
    return site.search()


@router.get(path='/kleinanzeigen')
def kleinanzeigen_rss(search_term: str) -> RSSResponse:
    site = Kleinanzeigen(search_term=search_term)
    return site.search()


@router.get(path='/marktplaats')
def marktplaats_rss(search_term: str, search_in_seller_name: bool = False) -> RSSResponse:
    site = Marktplaats(
        search_term=search_term,
        search_in_seller_name=search_in_seller_name
    )
    return site.search()


@router.get(path='/omega')
def omega_rss(search_term: str) -> RSSResponse:
    site = Omega(search_term=search_term)
    return site.search()


@router.get(path='/todocoleccion')
def todocoleccion_rss(search_term: str, translate: Translate = Depends(Translate)) -> RSSResponse:
    if translate.translate_titles:
        site = Todocoleccion(search_term=search_term, transformers=[translate_from_es])
    else:
        site = Todocoleccion(search_term=search_term)
    return site.search()


@router.get(path='/tradera')
def tradera_rss(search_term: str, currency: str = Query(
    default="EUR", enum=['DKK', 'EUR', 'GBP', 'JPY', 'NOK', 'SEK', 'USD']
)) -> RSSResponse:
    site = Tradera(search_term=search_term, currency=currency)
    return site.search()


@router.get(path='/vinted.nl')
def vinted_rss(search_term: str, catalog_id: Optional[int] = None, search_title_only: bool = True) -> RSSResponse:
    site = Vinted(search_term=search_term, catalog_id=catalog_id, search_title_only=search_title_only)
    return site.search()
