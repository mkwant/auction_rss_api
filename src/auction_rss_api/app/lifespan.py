from contextlib import asynccontextmanager

from fastapi import FastAPI
from playwright.async_api import async_playwright


@asynccontextmanager
async def lifespan(app: FastAPI):
    playwright = await async_playwright().start()

    app.state.browser = await playwright.chromium.launch(
        headless=True,
        args=["--no-sandbox"],
    )

    yield

    await app.state.browser.close()
    await playwright.stop()
