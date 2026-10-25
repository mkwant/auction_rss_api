from playwright.async_api import TimeoutError as PlaywrightTimeoutError


class WafChallengeError(RuntimeError):
    """The AWS WAF challenge page was returned instead of real content."""


async def fetch_buyee_html(browser, url: str, ready_selector: str) -> str:
    page = await browser.new_page()
    try:
        # Warm-up: let the WAF challenge solve and set its token cookie
        await page.goto("https://buyee.jp", wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(3000)  # ms

        await page.goto(url, wait_until="domcontentloaded", timeout=30000)

        try:
            await page.wait_for_selector(ready_selector, timeout=30000)
        except PlaywrightTimeoutError:
            # Challenge may still be reloading; give it one more chance
            try:
                await page.wait_for_load_state("networkidle", timeout=15000)
            except PlaywrightTimeoutError:
                pass

        html = await page.content()
    finally:
        await page.close()

    # Still on the challenge page -> real failure; no results -> fine
    if 'id="challenge-container"' in html:
        raise WafChallengeError(f"WAF challenge not solved for {url}")

    return html
