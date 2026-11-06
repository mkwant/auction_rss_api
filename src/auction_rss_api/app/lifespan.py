import logging
import os
from contextlib import asynccontextmanager

import httpx2
from camoufox import DefaultAddons
from camoufox.async_api import AsyncCamoufox
from fastapi import FastAPI

from auction_rss_api.app.settings import settings

logger = logging.getLogger(__name__)

PROFILE_DIR = settings.CAMOUFOX_PROFILE_DIR

# "virtual" = headful Firefox on an in-memory Xvfb display (needs xvfb in the image).
# Set CAMOUFOX_MODE=headless to test plain headless on the Pi.
_MODES = {"virtual": "virtual", "headless": True}
CAMOUFOX_MODE = _MODES.get(os.getenv("CAMOUFOX_MODE", "headless"), "headless")
BLOCKED_TYPES = {"image", "font", "media"}


async def block_heavy(route):
    """
    Block heavy page elements. You can opt out on the scraper level like so:
    `await page.route("**/*", lambda route: route.continue_())`
    """
    rtype = route.request.resource_type
    if rtype in BLOCKED_TYPES:
        logger.debug("blocked %s %s", rtype, route.request.url[:80])
        await route.abort()
    else:
        await route.continue_()


@asynccontextmanager
async def lifespan(app: FastAPI):
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)

    app.state.http_client = httpx2.AsyncClient(
        follow_redirects=True,
    )

    try:
        async with AsyncCamoufox(
                headless=CAMOUFOX_MODE,
                persistent_context=True,
                user_data_dir=str(PROFILE_DIR),  # keeps cf_clearance between restarts
                humanize=True,
                locale="en-US",
                exclude_addons=[DefaultAddons.UBO],
                ignore_https_errors=True,
        ) as context:
            # With persistent_context=True this is a BrowserContext;
            # context.new_page() works like the old browser attribute did.
            await context.route(url="**/*", handler=block_heavy)
            app.state.context = context
            app.state.browser = context

            yield
    finally:
        await app.state.http_client.aclose()
