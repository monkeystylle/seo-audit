from urllib.robotparser import RobotFileParser

import httpx
from selectolax.lexbor import LexborHTMLParser

from app.fetcher import fetch_page
from app.models import CheckResult

SITEMAP_PATHS = ["/sitemap.xml", "/sitemap_index.xml", "/wp-sitemap.xml"]


async def check_https(host: str) -> CheckResult:
    try:
        res = await fetch_page(f"http://{host}/")
    except httpx.HTTPError:
        return CheckResult(
            id="https",
            label="HTTPS redirect",
            status="warn",
            message="Couldn't load the http:// version of the site to test the redirect.",
        )

    if res.url.scheme == "https":
        return CheckResult(
            id="https",
            label="HTTPS redirect",
            status="pass",
            message="http:// redirects to https://.",
            value=str(res.url),
        )

    return CheckResult(
        id="https",
        label="HTTPS redirect",
        status="fail",
        message="The http:// version doesn't redirect to https://.",
        value=str(res.url),
    )


async def check_robots(origin: str, page_url: str) -> tuple[CheckResult, list[str]]:
    try:
        res = await fetch_page(f"{origin}/robots.txt")
    except httpx.HTTPError:
        res = None

    if res is None or res.status_code != 200:
        result = CheckResult(
            id="robots",
            label="robots.txt",
            status="warn",
            message="No robots.txt found. Google can still crawl the site, but most sites have one.",
        )
        return result, []

    parser = RobotFileParser()
    parser.parse(res.text.splitlines())
    sitemaps = parser.site_maps() or []

    if not parser.can_fetch("Googlebot", page_url):
        result = CheckResult(
            id="robots",
            label="robots.txt",
            status="fail",
            message="robots.txt blocks Google from crawling this page.",
            value=f"{origin}/robots.txt",
        )
        return result, sitemaps

    result = CheckResult(
        id="robots",
        label="robots.txt",
        status="pass",
        message="robots.txt allows Google to crawl this page.",
        value=f"{origin}/robots.txt",
    )
    return result, sitemaps


async def check_sitemap(origin: str, from_robots: list[str]) -> CheckResult:
    candidates = from_robots + [origin + path for path in SITEMAP_PATHS]

    for url in candidates:
        try:
            res = await fetch_page(url)
        except httpx.HTTPError:
            continue

        if res.status_code == 200 and ("<urlset" in res.text or "<sitemapindex" in res.text):
            return CheckResult(
                id="sitemap",
                label="Sitemap",
                status="pass",
                message="The site has an XML sitemap.",
                value=str(res.url),
            )

    return CheckResult(
        id="sitemap",
        label="Sitemap",
        status="warn",
        message="No sitemap found in robots.txt or at the usual addresses.",
    )


def check_noindex(tree: LexborHTMLParser, res: httpx.Response) -> CheckResult:
    meta = tree.css_first('meta[name="robots"]')
    meta_content = (meta.attributes.get("content") or "").lower() if meta else ""
    header = res.headers.get("x-robots-tag", "").lower()

    if "noindex" in meta_content or "noindex" in header:
        return CheckResult(
            id="noindex",
            label="Indexing allowed",
            status="fail",
            message="This page tells Google not to show it in search results.",
            value=meta_content or header,
        )

    return CheckResult(
        id="noindex",
        label="Indexing allowed",
        status="pass",
        message="Google is allowed to show this page in search results.",
    )


async def run_site_checks(res: httpx.Response, tree: LexborHTMLParser) -> list[CheckResult]:
    origin = f"{res.url.scheme}://{res.url.host}"
    robots_result, sitemaps = await check_robots(origin, str(res.url))

    return [
        await check_https(res.url.host),
        robots_result,
        await check_sitemap(origin, sitemaps),
        check_noindex(tree, res),
    ]