import os
from contextlib import asynccontextmanager
from pathlib import Path

import httpx2
from camoufox import DefaultAddons
from camoufox.async_api import AsyncCamoufox
from fastapi import FastAPI

from auction_rss_api.app.settings import settings

PROFILE_DIR = settings.CAMOUFOX_PROFILE_DIR

# "virtual" = headful Firefox on an in-memory Xvfb display (needs xvfb in the image).
# Set CAMOUFOX_MODE=headless to test plain headless on the Pi.
_MODES = {"virtual": "virtual", "headless": True}
CAMOUFOX_MODE = _MODES.get(os.getenv("CAMOUFOX_MODE", "headless"), "headless")


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
            app.state.context = context
            app.state.browser = context

            yield
    finally:
        await app.state.http_client.aclose()