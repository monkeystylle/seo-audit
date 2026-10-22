from typing import Literal

import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from selectolax.lexbor import LexborHTMLParser

from app.checks.crawl import run_crawl_checks
from app.checks.page import run_page_checks
from app.checks.site import run_site_checks
from app.crawler import crawl
from app.fetcher import fetch_page
from app.models import AuditReport, CrawlReport, SpeedReport
from app.speed import PageSpeedError, run_pagespeed

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


@app.get("/crawl", response_model=CrawlReport)
async def crawl_site(url: str, limit: int = Query(default=50, ge=1, le=200)):
    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"

    try:
        res = await fetch_page(url)
    except httpx.HTTPError:
        raise HTTPException(status_code=400, detail=f"Could not reach {url}")

    start_url = str(res.url)
    pages = await crawl(start_url, limit)

    return CrawlReport(
        start_url=start_url,
        pages_crawled=len(pages),
        checks=run_crawl_checks(pages),
        pages=pages,
    )


@app.get("/speed", response_model=SpeedReport)
async def speed(url: str, strategy: Literal["mobile", "desktop"] = "mobile"):
    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"

    try:
        return await run_pagespeed(url, strategy)
    except PageSpeedError as error:
        raise HTTPException(status_code=502, detail=str(error))
    except httpx.TimeoutException as error:
        raise HTTPException(
            status_code=504,
            detail=f"PageSpeed took too long to respond ({type(error).__name__})",
        )
    except httpx.HTTPError as error:
        raise HTTPException(
            status_code=502, detail=f"Couldn't connect to PageSpeed: {error!r}"
        )