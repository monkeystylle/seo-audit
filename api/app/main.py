import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from selectolax.lexbor import LexborHTMLParser

from app.checks.page import run_page_checks
from app.checks.site import run_site_checks
from app.fetcher import fetch_page
from app.models import AuditReport

app = FastAPI(title="SEO Audit API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/audit", response_model=AuditReport)
async def audit(url: str):
    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"

    try:
        res = await fetch_page(url)
    except httpx.HTTPError:
        raise HTTPException(status_code=400, detail=f"Could not reach {url}")

    tree = LexborHTMLParser(res.text)

    return AuditReport(
        url=str(res.url),
        status_code=res.status_code,
        site_checks=await run_site_checks(res, tree),
        page_checks=run_page_checks(tree),
    )