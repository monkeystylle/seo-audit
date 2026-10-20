from selectolax.lexbor import LexborHTMLParser

from app.models import CheckResult

TITLE_MIN = 30
TITLE_MAX = 60


def check_title(tree: LexborHTMLParser) -> CheckResult:
    node = tree.css_first("title")
    title = node.text(strip=True) if node else ""
    length = len(title)

    if not title:
        return CheckResult(
            id="title",
            label="Title tag",
            status="fail",
            message="The page has no title tag.",
        )

    if length < TITLE_MIN:
        status = "warn"
        message = f"Title is {length} characters. Aim for {TITLE_MIN}–{TITLE_MAX}."
    elif length > TITLE_MAX:
        status = "warn"
        message = f"Title is {length} characters. Google may cut it off after about {TITLE_MAX}."
    else:
        status = "pass"
        message = f"Title is {length} characters."

    return CheckResult(
        id="title", label="Title tag", status=status, message=message, value=title
    )