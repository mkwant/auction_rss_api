import re
from typing import List

import httpx
from bs4 import BeautifulSoup

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractor

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
    """Keeps the session/ViewState/window-id state across searches and pages."""

    def __init__(self) -> None:
        self.client = httpx.Client(headers=HEADERS, follow_redirects=True, timeout=10)
        self.window_id = None
        self.view_state = None
        self.last_query = {}
        self._headers_cache = []
        self._current_range = (0, PAGE_SIZE - 1)

    # ---- bootstrap -------------------------------------------------

    def _bootstrap(self) -> None:
        stub_resp = self.client.get(url=BASE, headers={"Referer": BASE})
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
        resp = self.client.get(url=BASE, params=params, headers={"Referer": BASE})
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

    def search(self, artist: str = "", title: str = "", isrc: str = "") -> PplRows:
        if self.view_state is None:
            self._bootstrap()

        self.last_query = {"artist": artist, "title": title, "isrc": isrc}
        data = self._base_form_fields()
        data.update(
            {
                "event": "pt1:search_button",
                "event.pt1:search_button": _table_event_xml(type="action"),
            }
        )
        resp = self.client.post(url=BASE, data=data, headers={"Referer": BASE, "Origin": "https://repsearch.ppluk.com"})
        resp.raise_for_status()
        self._update_state(resp.text)
        rows, headers = _parse_results_and_headers(resp.text)
        if headers:
            self._headers_cache = headers
        self._current_range = (0, PAGE_SIZE - 1)
        return rows

    def get_page(self, new_start: int, new_end: int) -> PplRows:
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
        resp = self.client.post(
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

    def next_page(self) -> PplRows:
        old_start, old_end = self._current_range
        page_len = old_end - old_start + 1
        return self.get_page(new_start=old_end + 1, new_end=old_end + page_len)

    def search_all(self, artist: str = "", title: str = "", isrc: str = "") -> PplRows:
        """Search and keep paginating until a short/empty page comes back."""
        rows = self.search(artist=artist, title=title, isrc=isrc)
        all_rows = list(rows)
        while len(rows) == PAGE_SIZE:
            rows = self.next_page()
            if not rows:
                break
            all_rows.extend(rows)
        return all_rows


class PPLRepertoireSearch(AuctionExtractor):
    artist: str = ""
    title: str = ""
    isrc: str = ""

    @property
    def search_link(self) -> str:
        return BASE

    @property
    def site_desc(self) -> str:
        return "PPL Repertoire Search"

    def get_auctions(self) -> List[Auction]:
        client = PPLRepertoireClient()
        rows = client.search_all(artist=self.artist, title=self.title, isrc=self.isrc)

        auctions = []

        for row in rows:
            unique_id = row["ISRC"]
            title = f"{row['Artist Name']} - {row['Recording Title']}"
            description = f"ISRC: {row['ISRC']}\nRightsholder: {row['Recording Rightsholder']}\nRelease date: {row['Release Date']}\nDuration: {row['Duration']}"

            auctions.append(
                Auction(
                    auction_id=unique_id,
                    title=title,
                    link=BASE,
                    description=description,
                )
            )

        return auctions
