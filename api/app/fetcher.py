import httpx

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; SEOAuditBot/0.1)"}


def make_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(follow_redirects=True, timeout=15, headers=HEADERS)


async def fetch_page(url: str) -> httpx.Response:
    async with make_client() as client:
        return await client.get(url)