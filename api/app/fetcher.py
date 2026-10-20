import httpx

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; SEOAuditBot/0.1)"}


async def fetch_page(url: str) -> httpx.Response:
    async with httpx.AsyncClient(
        follow_redirects=True, timeout=15, headers=HEADERS
    ) as client:
        return await client.get(url)