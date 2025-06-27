import logging
from pathlib import Path

import truststore
from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI

from app.logs import setup_logging
from app.middleware import AddNoIndex
from app.settings import settings
from routers import redirect, auctions, venues, recordshops

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
    version='1.16.34',
    description='This API returns RSS feeds for the search results of auction sites, '
                'online record stores and concert venues.'
)

logger.info('Starting application...')

# Add routers and middleware
app.include_router(auctions.router)
app.include_router(recordshops.router)
app.include_router(venues.router)
app.include_router(redirect.router)
app.add_middleware(middleware_class=AddNoIndex) # noqa
app.add_middleware(middleware_class=CorrelationIdMiddleware) # noqa

routes = {x.name for x in app.routes if x.name.endswith('_rss')} # noqa
logger.info(f'Total feeds: {len(routes)}')
