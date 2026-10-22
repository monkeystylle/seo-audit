import httpx

from app.config import PAGESPEED_API_KEY
from app.models import CheckResult, SpeedReport

PAGESPEED_URL = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
PAGESPEED_TIMEOUT = 300

METRICS = [
    ("largest-contentful-paint", "Largest Contentful Paint"),
    ("cumulative-layout-shift", "Cumulative Layout Shift"),
    ("total-blocking-time", "Total Blocking Time"),
    ("first-contentful-paint", "First Contentful Paint"),
    ("speed-index", "Speed Index"),
]


class PageSpeedError(Exception):
    pass


def score_to_status(score: float | None) -> str:
    if score is None:
        return "warn"
    if score >= 0.9:
        return "pass"
    if score >= 0.5:
        return "warn"
    return "fail"


async def run_pagespeed(url: str, strategy: str) -> SpeedReport:
    if not PAGESPEED_API_KEY:
        raise PageSpeedError("PAGESPEED_API_KEY is missing from api/.env")

    params = {
        "url": url,
        "strategy": strategy,
        "category": "performance",
        "key": PAGESPEED_API_KEY,
    }

    async with httpx.AsyncClient(timeout=PAGESPEED_TIMEOUT) as client:
        res = await client.get(PAGESPEED_URL, params=params)

    data = res.json()

    if res.status_code != 200:
        message = data.get("error", {}).get("message", "PageSpeed request failed")
        raise PageSpeedError(message)

    lighthouse = data["lighthouseResult"]
    score = lighthouse["categories"]["performance"]["score"] or 0
    audits = lighthouse["audits"]

    checks = []
    for audit_id, label in METRICS:
        audit = audits.get(audit_id)
        if audit is None:
            continue

        checks.append(
            CheckResult(
                id=audit_id,
                label=label,
                status=score_to_status(audit.get("score")),
                message=audit.get("displayValue", "No value"),
            )
        )

    return SpeedReport(
        url=url,
        strategy=strategy,
        score=round(score * 100),
        checks=checks,
    )