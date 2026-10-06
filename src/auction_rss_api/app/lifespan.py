from contextlib import asynccontextmanager
from pathlib import Path

import httpx2
from fastapi import FastAPI
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

PROFILE_DIR = Path("/app/profile")


@asynccontextmanager
async def lifespan(app: FastAPI):
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)

    app.state.http_client = httpx2.AsyncClient(
        follow_redirects=True,
    )

    try:
        async with Stealth().use_async(async_playwright()) as playwright:
            app.state.context = await playwright.chromium.launch_persistent_context(
                user_data_dir=str(PROFILE_DIR),
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                ],
            )

            app.state.browser = app.state.context

            try:
                yield
            finally:
                await app.state.context.close()

    finally:
        await app.state.http_client.aclose()
