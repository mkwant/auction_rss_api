import logging
from pathlib import Path

import truststore
from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI
from fastapi.routing import _IncludedRouter

from auction_rss_api import __version__
from auction_rss_api.app.lifespan import lifespan
from auction_rss_api.app.logs import setup_logging
from auction_rss_api.app.middleware import AddNoIndex
from auction_rss_api.app.settings import settings
from auction_rss_api.routers import auctions, othersites, recordshops, redirect, tools, venues

truststore.inject_into_ssl()  # Use OS trust store

# TODO Add function to generate random User Agent
# TODO Documentation

# Setting up logging
setup_logging(
    log_location=Path('/logs/auction_rss_api.log'),
    log_level=settings.LOG_LEVEL
)
logger = logging.getLogger(__name__)

# Instantiate FastApi
app = FastAPI(
    title='AuctionRSS',
    version=__version__,
    description='This API returns RSS feeds for the search results of auction sites, '
                'online record stores and concert venues.',
    lifespan=lifespan,
)

logger.info(f'Starting application (version {__version__})...')

# Add routers and middleware
app.include_router(auctions.router)
app.include_router(recordshops.router)
app.include_router(othersites.router)
app.include_router(venues.router)
app.include_router(tools.router)
app.include_router(redirect.router)
app.add_middleware(middleware_class=AddNoIndex)  # noqa
app.add_middleware(middleware_class=CorrelationIdMiddleware)  # noqa

# Calculate and log number of rss feeds
routes = []
my_routers = [x for x in app.routes if isinstance(x, _IncludedRouter)]
for router in my_routers:
    routes.extend(router.original_router.routes)
routes = [x for x in routes if x.name.endswith('_rss')]
logger.info(f'Total feeds: {len(routes)}')
