from fastapi_rss import RSSResponse, GUID, Enclosure, EnclosureAttrs, Item, RSSFeed

from auction_extractors.base import AuctionExtractor


def generate_rss_response(auction_extractor: AuctionExtractor) -> RSSResponse:
    """From an AuctionExtractor create an RSSResponse that can be used as a FastApi response."""

    auction_search_response = auction_extractor.search()

    items = []
    for auction in auction_search_response.auctions:

        item_data = {'title': auction.title,
                     'link': auction.link,
                     'description': auction.description,
                     'guid': GUID(content=auction.auction_id),
                     'author': auction.seller,
                     'pub_date': auction.start_date
                     }

        if auction.image_link:
            item_data['enclosure'] = Enclosure(content='',
                                               attrs=EnclosureAttrs(url=auction.image_link, length=1000,
                                                                    type='image/jpeg'))
        items.append(Item(**item_data))

    # Instantiate the RSSFeed class
    feed_data = {
        'title': f"{auction_search_response.site_desc} ('{auction_search_response.search_term}')",
        'link': auction_search_response.search_link,
        'description': f"{auction_search_response.site_desc} ('{auction_search_response.search_term}')",
        'language': 'en-us',
        'generator': 'Auction RSS api',
        'ttl': 40,
        'item': items
    }
    feed = RSSFeed(**feed_data)

    # Return the RSSResponse
    return RSSResponse(content=feed)
