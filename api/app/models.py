from typing import Literal

from pydantic import BaseModel


class CheckResult(BaseModel):
    id: str
    label: str
    status: Literal["pass", "warn", "fail"]
    message: str
    value: str | None = None


class AuditReport(BaseModel):
    url: str
    status_code: int
    site_checks: list[CheckResult]
    page_checks: list[CheckResult]

class CrawledPage(BaseModel):
    url: str
    status_code: int
    found_on: str | None = None
    title: str | None = None
    meta_description: str | None = None
    h1_count: int = 0


class CrawlReport(BaseModel):
    start_url: str
    pages_crawled: int
    pages: list[CrawledPage]