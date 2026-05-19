"""HTTP-Fetcher für die überwachten Unternehmens-Websites.

Liefert das gerenderte HTML zurück. Bewusst klein gehalten: ein realistischer
User-Agent, ein Timeout, ein paar Retries — ein einzelnes blockierendes oder
fehlerhaftes Ziel soll den Gesamtlauf nicht stoppen.
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)
DEFAULT_TIMEOUT = 25  # seconds
DEFAULT_RETRIES = 2


@dataclass
class FetchResult:
    final_url: str
    status_code: int
    html: str


def _session() -> requests.Session:
    s = requests.Session()
    retry = Retry(
        total=DEFAULT_RETRIES,
        backoff_factor=1.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    s.mount("https://", adapter)
    s.mount("http://", adapter)
    s.headers.update({
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "de-DE,de;q=0.9,en;q=0.8",
    })
    return s


def fetch(url: str, timeout: int = DEFAULT_TIMEOUT) -> FetchResult:
    """Fetch a URL. Raises requests.HTTPError on 4xx/5xx after retries."""
    started = time.monotonic()
    with _session() as s:
        resp = s.get(url, timeout=timeout, allow_redirects=True)
    elapsed = time.monotonic() - started
    logger.info("GET %s → %d (%.2fs, %d bytes)", url, resp.status_code, elapsed, len(resp.content))
    resp.raise_for_status()
    # Trust the server's declared charset; fall back to utf-8 if missing.
    if not resp.encoding or resp.encoding.lower() == "iso-8859-1":
        resp.encoding = resp.apparent_encoding or "utf-8"
    return FetchResult(final_url=resp.url, status_code=resp.status_code, html=resp.text)
