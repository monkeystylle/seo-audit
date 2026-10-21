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