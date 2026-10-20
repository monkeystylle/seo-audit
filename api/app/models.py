from typing import Literal

from pydantic import BaseModel


class CheckResult(BaseModel):
    id: str
    label: str
    status: Literal["pass", "warn", "fail"]
    message: str
    value: str | None = None


class PageAudit(BaseModel):
    url: str
    status_code: int
    checks: list[CheckResult]