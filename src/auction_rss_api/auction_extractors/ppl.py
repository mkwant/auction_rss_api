import asyncio
import re
import time
from typing import List, Optional

import httpx
from bs4 import BeautifulSoup

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractor, AuctionExtractorAsync

BASE = "https://repsearch.ppluk.com/ars/faces/pages/audioSearch.jspx"
PAGE_SIZE = 15  # observed range: 0-14, then 15-29, etc.

_LOOPBACK_RE = re.compile(
    r"AdfLoopbackUtils\.runLoopback\(\s*\d+,\s*'_afrLoop',\s*'([^']*)',"
    r"\s*'_afrWindowMode',\s*'Adf-Window-Id',\s*'_afrPage',\s*'[^']*',\s*'([^']*)',"
)

# Matches <update id="...">CDATA...</update> blocks in a JSF/ADF
# <partial-response> XML document.
_PARTIAL_UPDATE_RE = re.compile(
    pattern=r'<update\s+id="([^"]+)"><!\[CDATA\[(.*?)\]\]></update>',
    flags=re.DOTALL,  # noqa
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:152.0) Gecko/20100101 Firefox/152.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

PplRows = list[dict[str, str]]
PplRowHeader = list[str]


def _extract_hidden_fields(html: str) -> dict:
    """Pull ADF/JSF hidden state fields (ViewState, etc.) out of a full page."""
    soup = BeautifulSoup(markup=html, features="lxml")
    fields = {}
    for inp in soup.select("input[type=hidden]"):
        name = inp.get("name")
        if name:
            fields[str(name)] = inp.get("value", "")
    return fields


def _parse_results_and_headers(html: str) -> tuple[PplRows, PplRowHeader]:
    """Parse a #pt1:searchResultsTable element, whether it's a whole page
    or just the fragment returned inside a partial-response update."""
    soup = BeautifulSoup(markup=html, features="lxml")
    table = soup.find(id="pt1:searchResultsTable")
    if table is None:
        return [], []

    headers = [span.get_text(strip=True) for span in table.select(".af_column_label-text")]

    rows = []
    for tr in table.select("tr.af_table_data-row"):
        cells = [td.get_text(strip=True) for td in tr.find_all("td")]
        if not cells:
            continue
        rows.append(dict(zip(headers, cells)))
    return rows, headers


def _table_event_xml(**kv) -> str:
    parts = "".join(f'<k v="{k}"><s>{v}</s></k>' for k, v in kv.items())
    return f'<m xmlns="http://oracle.com/richClient/comm">{parts}</m>'  # noqa


class PPLRepertoireClient:
    """
    Async client that keeps the session/ViewState/window-id state across
    searches and pages.

    IMPORTANT: javax.faces.ViewState is a single-use, server-rotated token
    -- each response hands back the token the *next* request must use. That
    makes pagination within one search inherently sequential: you cannot
    know the request for page 3 until page 2's response has come back and
    handed you its ViewState. So `search_all()` awaits pages one at a time.

    What *is* safe to parallelize is multiple independent
    PPLRepertoireClient instances (i.e. separate searches/sessions) -- see
    `search_many()` below, or just run several `search_all()` calls under
    `asyncio.gather`.
    """

    def __init__(self) -> None:
        self.client = httpx.AsyncClient(headers=HEADERS, follow_redirects=True, timeout=10)
        self.window_id: Optional[str] = None
        self.view_state: Optional[str] = None
        self.last_query: dict = {}
        self._headers_cache: PplRowHeader = []
        self._current_range = (0, PAGE_SIZE - 1)

    async def __aenter__(self) -> "PPLRepertoireClient":
        return self

    async def __aexit__(self, *exc_info) -> None:
        await self.close()

    async def close(self) -> None:
        await self.client.aclose()

    # ---- bootstrap -------------------------------------------------

    async def _bootstrap(self) -> None:
        stub_resp = await self.client.get(url=BASE, headers={"Referer": BASE})
        stub_resp.raise_for_status()
        m = _LOOPBACK_RE.search(stub_resp.text)
        if not m:
            raise RuntimeError(
                "Could not find AdfLoopbackUtils.runLoopback(...) in the "
                "bootstrap response -- the site's markup may have changed. "
                "First 500 chars of response:\n" + stub_resp.text[:500]
            )
        afr_loop, self.window_id = m.group(1), m.group(2)

        params = {
            "_afrLoop": afr_loop,
            "_afrWindowMode": 0,
            "Adf-Window-Id": self.window_id,
            "_afrPage": 0,
            "_afrFS": 16,
            "_afrMT": "screen",
            "_afrMFW": 1920,
            "_afrMFH": 1080,
            "_afrMFDW": 1920,
            "_afrMFDH": 1080,
            "_afrMFC": 8,
            "_afrMFCI": 0,
            "_afrMFM": 0,
            "_afrMFR": 96,
            "_afrMFG": 0,
            "_afrMFS": 0,
            "_afrMFO": 0,
        }
        resp = await self.client.get(url=BASE, params=params, headers={"Referer": BASE})
        resp.raise_for_status()
        self._update_state(resp.text)

    def _update_state(self, html: str) -> None:
        fields = _extract_hidden_fields(html)
        if "javax.faces.ViewState" in fields:
            self.view_state = fields["javax.faces.ViewState"]

    def _base_form_fields(self) -> dict:
        return {
            "pt1:rec_band_artist": self.last_query.get("artist", ""),
            "pt1:rec_title": self.last_query.get("title", ""),
            "pt1:isrc_code": self.last_query.get("isrc", ""),
            "org.apache.myfaces.trinidad.faces.FORM": "f1",
            "Adf-Window-Id": self.window_id,
            "Adf-Page-Id": "0",
            "javax.faces.ViewState": self.view_state,
        }

    # ---- search / pagination ---------------------------------------

    async def search(self, artist: str = "", title: str = "", isrc: str = "") -> PplRows:
        if self.view_state is None:
            await self._bootstrap()

        self.last_query = {"artist": artist, "title": title, "isrc": isrc}
        data = self._base_form_fields()
        data.update(
            {
                "event": "pt1:search_button",
                "event.pt1:search_button": _table_event_xml(type="action"),
            }
        )
        resp = await self.client.post(
            url=BASE, data=data, headers={"Referer": BASE, "Origin": "https://repsearch.ppluk.com"}
        )
        resp.raise_for_status()
        self._update_state(resp.text)
        rows, headers = _parse_results_and_headers(resp.text)
        if headers:
            self._headers_cache = headers
        self._current_range = (0, PAGE_SIZE - 1)
        return rows

    async def get_page(self, new_start: int, new_end: int) -> PplRows:
        if self.view_state is None:
            raise RuntimeError("Call search() before paginating.")

        old_start, old_end = self._current_range
        event_xml = _table_event_xml(
            oldStart=old_start,
            oldEnd=old_end,
            newStart=new_start,
            newEnd=new_end,
            type="rangeChange",
        )
        data = self._base_form_fields()
        data.update(
            {
                "oracle.adf.view.rich.RENDER": "pt1:searchResultsTable",
                "event": "pt1:searchResultsTable",
                "event.pt1:searchResultsTable": event_xml,
                "oracle.adf.view.rich.PROCESS": "pt1:searchResultsTable",
            }
        )
        resp = await self.client.post(
            url=BASE,
            data=data,
            headers={
                "Referer": BASE,
                "Origin": "https://repsearch.ppluk.com",
                # Standard Apache MyFaces Trinidad convention for requesting
                # a genuine partial-response instead of a full page.
                "Faces-Request": "partial/ajax",
                "X-Requested-With": "XMLHttpRequest",
            },
        )
        resp.raise_for_status()

        rows = self._handle_page_response(resp.text)
        self._current_range = (new_start, new_end)
        return rows

    def _handle_page_response(self, text: str) -> PplRows:
        stripped = text.lstrip()
        if stripped.startswith("<?xml") or "<partial-response" in text[:2000]:
            updates = dict(_PARTIAL_UPDATE_RE.findall(text))

            vs_key = next((k for k in updates if "ViewState" in k), None)
            if vs_key:
                vs_raw = updates[vs_key]
                m = re.search(pattern=r'value="([^"]*)"', string=vs_raw)
                self.view_state = m.group(1) if m else vs_raw.strip()

            table_html = updates.get("pt1:searchResultsTable")
            if table_html is None:
                table_html = next((c for c in updates.values() if 'id="pt1:searchResultsTable"' in c), None)
            if table_html is None:
                raise RuntimeError(
                    "Got a partial-response but couldn't find the results-table "
                    "update. Update ids present: "
                    f"{list(updates.keys())}."
                )
            rows, headers = _parse_results_and_headers(str(table_html))
        else:
            # Not a partial-response -- treat as a normal full-page reload.
            self._update_state(text)
            rows, headers = _parse_results_and_headers(text)

        if headers:
            self._headers_cache = headers
        elif self._headers_cache and rows and isinstance(rows[0], list):
            rows = [dict(zip(self._headers_cache, r)) for r in rows]
        return rows

    async def next_page(self) -> PplRows:
        old_start, old_end = self._current_range
        page_len = old_end - old_start + 1
        return await self.get_page(new_start=old_end + 1, new_end=old_end + page_len)

    async def search_all(self, artist: str = "", title: str = "", isrc: str = "") -> PplRows:
        """
        Search and keep paginating until a short/empty page comes back.

        Pages are awaited sequentially -- and must be, since each page
        request depends on the ViewState token returned by the previous
        one. There is no way to fetch page N+1 before page N's response
        has arrived. This is still non-blocking for the rest of an async
        app (e.g. other searches running under asyncio.gather), it's just
        not internally parallel.
        """
        rows = await self.search(artist=artist, title=title, isrc=isrc)
        all_rows = list(rows)
        while len(rows) == PAGE_SIZE:
            rows = await self.next_page()
            if not rows:
                break
            all_rows.extend(rows)
        return all_rows


async def search_all_concurrent(
        artist: str = "",
        title: str = "",
        isrc: str = "",
        concurrency: int = 8,
) -> PplRows:
    """
    Fetch every page of one search using several independent sessions in
    parallel instead of walking pages one at a time in a single session.

    This only works because direct offset jumps were verified against the
    live site to return the actual rows at that offset (not just page 1
    again) -- the per-request cap is on *width* (max 15 rows), not on
    requiring sequential stepping. So worker `i` can bootstrap its own
    session and go straight for pages i, i+concurrency, i+2*concurrency,
    ... without ever touching the pages in between.

    Trade-off: each worker pays its own bootstrap cost (2 GETs) plus one
    forced page-0 search (the initial search POST always returns page 0,
    regardless of what you actually want -- there's no way to make the
    first request return a different offset). For `concurrency` workers
    that's `concurrency - 1` wasted "page 0" fetches. Worth it as long as
    the number of pages saved by parallelism outweighs that overhead --
    true for anything more than a couple of pages, and increasingly so
    the more pages there are.

    Be mindful this multiplies session/request volume against the server;
    keep `concurrency` modest (single digits to low tens) rather than
    trying to open one session per page.
    """
    stop_event = asyncio.Event()
    results: dict[int, PplRows] = {}

    async def worker(worker_id: int) -> None:
        async with PPLRepertoireClient() as client:
            page0 = await client.search(artist=artist, title=title, isrc=isrc)
            if worker_id == 0:
                results[0] = page0
            if len(page0) < PAGE_SIZE:
                stop_event.set()
                return

            offset_index = worker_id
            if offset_index == 0:
                offset_index += concurrency

            while not stop_event.is_set():
                start = offset_index * PAGE_SIZE
                end = start + PAGE_SIZE - 1
                page = await client.get_page(start, end)
                if not page:
                    stop_event.set()
                    break
                results[offset_index] = page
                if len(page) < PAGE_SIZE:
                    stop_event.set()
                    break
                offset_index += concurrency

    await asyncio.gather(*(worker(i) for i in range(concurrency)))

    all_rows: PplRows = []
    for idx in sorted(results):
        all_rows.extend(results[idx])
    return all_rows


async def search_many(queries: list[dict]) -> list[PplRows]:
    """
    Run several independent searches concurrently, each in its own
    session. Unlike pages within a single search, separate searches don't
    share any server-side state, so this genuinely parallelizes.

    queries: e.g. [{"artist": "David Bowie"}, {"isrc": "USJT12500320"}]
    """

    async def _one(q: dict) -> PplRows:
        async with PPLRepertoireClient() as client:
            return await client.search_all(**q)

    return await asyncio.gather(*(_one(q) for q in queries))


class PPLRepertoireSearch(AuctionExtractorAsync):
    artist: str = ""
    title: str = ""
    isrc: str = ""
    concurrency: int = 8

    @property
    def search_link(self) -> str:
        return BASE

    @property
    def site_desc(self) -> str:
        return "PPL Repertoire Search"

    async def get_auctions(self) -> List[Auction]:
        rows = await search_all_concurrent(
            artist=self.artist, title=self.title, isrc=self.isrc, concurrency=self.concurrency
        )

        auctions = []

        for row in rows:
            unique_id = row["ISRC"]
            title = f"{row['Artist Name']} - {row['Recording Title']}"
            description = (
                f"ISRC: {row['ISRC']}\n"
                f"Rightsholder: {row['Recording Rightsholder']}\n"
                f"Release date: {row['Release Date']}\n"
                f"Duration: {row['Duration']}"
            )

            auctions.append(
                Auction(
                    auction_id=unique_id,
                    title=title,
                    link=BASE,
                    description=description,
                )
            )

        return auctions
