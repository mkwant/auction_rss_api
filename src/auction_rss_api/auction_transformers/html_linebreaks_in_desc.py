from auction_rss_api.models.auction import Auction


async def html_linebreaks_in_desc(auction: Auction) -> Auction:
    """Replace `\n` linebreaks in the auction description with `<br>`"""
    auction.description = auction.description.replace('\n', '<br>\n')
    return auction
