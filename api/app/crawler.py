import asyncio
from urllib.parse import urldefrag, urljoin, urlparse

import httpx
from selectolax.lexbor import LexborHTMLParser

from app.fetcher import make_client
from app.models import CrawledPage

BATCH_SIZE = 5
SKIP_EXTENSIONS = (
    ".pdf", ".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg",
    ".zip", ".mp4", ".mp3", ".doc", ".docx", ".xls", ".xlsx",
)


def normalize_url(url: str) -> str:
    url = urldefrag(url).url
    if urlparse(url).path == "":
        url += "/"
    return url


def extract_links(tree: LexborHTMLParser, page_url: str, host: str) -> list[str]:
    links = []
    for node in tree.css("a[href]"):
        href = node.attributes.get("href") or ""
        absolute = normalize_url(urljoin(page_url, href))
        parsed = urlparse(absolute)

        if parsed.scheme not in ("http", "https"):
            continue
        if parsed.netloc != host:
            continue
        if parsed.path.lower().endswith(SKIP_EXTENSIONS):
            continue

        links.append(absolute)
    return links


async def fetch_one(
    client: httpx.AsyncClient, url: str, found_on: str | None, host: str
) -> tuple[CrawledPage, list[str]]:
    try:
        res = await client.get(url)
    except httpx.HTTPError:
        return CrawledPage(url=url, status_code=0, found_on=found_on), []

    page = CrawledPage(url=url, status_code=res.status_code, found_on=found_on)

    is_html = "text/html" in res.headers.get("content-type", "")
    if res.status_code != 200 or not is_html:
        return page, []

    tree = LexborHTMLParser(res.text)

    title = tree.css_first("title")
    description = tree.css_first('meta[name="description"]')

    page.title = title.text(strip=True) if title else None
    page.meta_description = (
        (description.attributes.get("content") or "").strip() if description else None
    )
    page.h1_count = len(tree.css("h1"))

    return page, extract_links(tree, str(res.url), host)


async def crawl(start_url: str, limit: int) -> list[CrawledPage]:
    start_url = normalize_url(start_url)
    host = urlparse(start_url).netloc
    seen = {start_url}
    queue: list[tuple[str, str | None]] = [(start_url, None)]
    pages: list[CrawledPage] = []

    async with make_client() as client:
        while queue:
            batch = queue[:BATCH_SIZE]
            queue = queue[BATCH_SIZE:]

            results = await asyncio.gather(
                *(fetch_one(client, url, found_on, host) for url, found_on in batch)
            )

            for page, links in results:
                pages.append(page)
                for link in links:
                    if link not in seen and len(seen) < limit:
                        seen.add(link)
                        queue.append((link, page.url))

    return pages