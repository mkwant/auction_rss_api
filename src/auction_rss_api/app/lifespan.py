from contextlib import asynccontextmanager

from fastapi import FastAPI
from playwright.async_api import async_playwright
from playwright_stealth import Stealth


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with Stealth().use_async(async_playwright()) as playwright:

        app.state.browser = await playwright.chromium.launch(
            headless=True,
            args=["--no-sandbox"],
        )

        yield

        await app.state.browser.close()
        await playwright.stop()
