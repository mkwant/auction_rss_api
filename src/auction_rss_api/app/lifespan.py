from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

PROFILE_DIR = Path("/app/profile")  # persistent storage


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure the profile dir exists
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)

    # Use stealth if you want to reduce automation detection
    async with Stealth().use_async(async_playwright()) as playwright:
        # Launch persistent context instead of just a browser
        app.state.context = await playwright.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
            ],
        )
        app.state.browser = app.state.context
        yield

        # Close the context and playwright
        await app.state.context.close()
        await playwright.stop()
