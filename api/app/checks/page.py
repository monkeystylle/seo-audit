from selectolax.lexbor import LexborHTMLParser

from app.models import CheckResult

TITLE_MIN = 30
TITLE_MAX = 60
META_MIN = 70
META_MAX = 160


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


def check_meta_description(tree: LexborHTMLParser) -> CheckResult:
    node = tree.css_first('meta[name="description"]')
    description = (node.attributes.get("content") or "").strip() if node else ""
    length = len(description)

    if not description:
        return CheckResult(
            id="meta_description",
            label="Meta description",
            status="fail",
            message="The page has no meta description.",
        )

    if length < META_MIN:
        status = "warn"
        message = f"Description is {length} characters. Aim for {META_MIN}–{META_MAX}."
    elif length > META_MAX:
        status = "warn"
        message = f"Description is {length} characters. Google may cut it off after about {META_MAX}."
    else:
        status = "pass"
        message = f"Description is {length} characters."

    return CheckResult(
        id="meta_description",
        label="Meta description",
        status=status,
        message=message,
        value=description,
    )


def check_h1(tree: LexborHTMLParser) -> CheckResult:
    headings = tree.css("h1")
    count = len(headings)

    if count == 0:
        return CheckResult(
            id="h1",
            label="H1 heading",
            status="fail",
            message="The page has no H1 heading.",
        )

    first = headings[0].text(separator=" ", strip=True)

    if count > 1:
        return CheckResult(
            id="h1",
            label="H1 heading",
            status="warn",
            message=f"The page has {count} H1 headings. Use exactly one.",
            value=first,
        )

    return CheckResult(
        id="h1",
        label="H1 heading",
        status="pass",
        message="The page has one H1 heading.",
        value=first,
    )


def check_image_alt(tree: LexborHTMLParser) -> CheckResult:
    images = tree.css("img")
    missing = [img for img in images if "alt" not in img.attributes]

    if not images:
        return CheckResult(
            id="image_alt",
            label="Image alt text",
            status="pass",
            message="The page has no images.",
        )

    if missing:
        return CheckResult(
            id="image_alt",
            label="Image alt text",
            status="warn",
            message=f"{len(missing)} of {len(images)} images are missing an alt attribute.",
            value=missing[0].attributes.get("src"),
        )

    return CheckResult(
        id="image_alt",
        label="Image alt text",
        status="pass",
        message=f"All {len(images)} images have an alt attribute.",
    )


def check_viewport(tree: LexborHTMLParser) -> CheckResult:
    node = tree.css_first('meta[name="viewport"]')
    content = (node.attributes.get("content") or "") if node else ""

    if not node:
        return CheckResult(
            id="viewport",
            label="Mobile viewport",
            status="fail",
            message="The page has no viewport tag, so phones show it zoomed out.",
        )

    if "width=device-width" not in content.replace(" ", ""):
        return CheckResult(
            id="viewport",
            label="Mobile viewport",
            status="warn",
            message="The viewport tag doesn't set width=device-width.",
            value=content,
        )

    return CheckResult(
        id="viewport",
        label="Mobile viewport",
        status="pass",
        message="The page is set up for mobile screens.",
        value=content,
    )


def run_page_checks(tree: LexborHTMLParser) -> list[CheckResult]:
    return [
        check_title(tree),
        check_meta_description(tree),
        check_h1(tree),
        check_image_alt(tree),
        check_viewport(tree),
    ]