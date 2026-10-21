from collections import defaultdict

from app.models import CheckResult, CrawledPage

MAX_DETAILS = 10


def plural(count: int, word: str) -> str:
    return f"{count} {word}" if count == 1 else f"{count} {word}s"


def limit_details(items: list[str]) -> list[str]:
    if len(items) <= MAX_DETAILS:
        return items
    extra = len(items) - MAX_DETAILS
    return items[:MAX_DETAILS] + [f"…and {extra} more"]


def check_broken_pages(pages: list[CrawledPage]) -> CheckResult:
    broken = [page for page in pages if page.status_code == 0 or page.status_code >= 400]

    if not broken:
        return CheckResult(
            id="broken_pages",
            label="Broken pages",
            status="pass",
            message=f"All {len(pages)} pages loaded without errors.",
        )

    details = []
    for page in broken:
        code = page.status_code or "no response"
        details.append(f"{page.url} ({code}), linked from {page.found_on}")

    return CheckResult(
        id="broken_pages",
        label="Broken pages",
        status="fail",
        message=f"{plural(len(broken), 'page')} returned an error.",
        details=limit_details(details),
    )


def check_duplicates(
    pages: list[CrawledPage], field: str, check_id: str, label: str
) -> CheckResult:
    groups: dict[str, list[str]] = defaultdict(list)

    for page in pages:
        text = getattr(page, field)
        if text:
            groups[text].append(page.url)

    duplicates = {text: urls for text, urls in groups.items() if len(urls) > 1}

    if not duplicates:
        return CheckResult(
            id=check_id,
            label=label,
            status="pass",
            message="No two pages share the same text.",
        )

    details = []
    for text, urls in duplicates.items():
        details.append(f"“{text}” is used on {len(urls)} pages: {', '.join(urls)}")

    return CheckResult(
        id=check_id,
        label=label,
        status="warn",
        message=f"{plural(len(duplicates), 'group')} of pages share the same text.",
        details=limit_details(details),
    )


def check_missing_descriptions(pages: list[CrawledPage]) -> CheckResult:
    html_pages = [page for page in pages if page.status_code == 200]
    missing = [page.url for page in html_pages if not page.meta_description]

    if not missing:
        return CheckResult(
            id="missing_descriptions",
            label="Pages missing a meta description",
            status="pass",
            message="Every page has a meta description.",
        )

    return CheckResult(
        id="missing_descriptions",
        label="Pages missing a meta description",
        status="fail",
        message=f"{len(missing)} of {len(html_pages)} pages have no meta description.",
        details=limit_details(missing),
    )


def check_missing_h1(pages: list[CrawledPage]) -> CheckResult:
    html_pages = [page for page in pages if page.status_code == 200]
    missing = [page.url for page in html_pages if page.h1_count == 0]

    if not missing:
        return CheckResult(
            id="missing_h1",
            label="Pages missing an H1",
            status="pass",
            message="Every page has an H1 heading.",
        )

    return CheckResult(
        id="missing_h1",
        label="Pages missing an H1",
        status="warn",
        message=f"{len(missing)} of {len(html_pages)} pages have no H1 heading.",
        details=limit_details(missing),
    )


def run_crawl_checks(pages: list[CrawledPage]) -> list[CheckResult]:
    return [
        check_broken_pages(pages),
        check_duplicates(pages, "title", "duplicate_titles", "Duplicate titles"),
        check_duplicates(
            pages, "meta_description", "duplicate_descriptions", "Duplicate descriptions"
        ),
        check_missing_descriptions(pages),
        check_missing_h1(pages),
    ]