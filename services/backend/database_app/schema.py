from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class Base(BaseModel):
    pass


class ErrorInfo(Base):
    loc: list[str | int]
    msg: str
    type: str

    def __init__(self, loc: list[str], msg: str, type_: str, **kwargs: Any) -> None:
        # Mypy doesn't see it, but args should be passed to super().__init__, not assigned here,
        # else pydantic.ValidationError raised
        super().__init__(loc=loc, msg=msg, type=type_, **kwargs)  # type: ignore[call-arg]


class ErrorResponseBody(Base):
    detail: list[ErrorInfo]

    def __init__(self, detail: list[ErrorInfo], **kwargs: Any) -> None:
        # Mypy doesn't see it, but args should be passed to super().__init__, not assigned here,
        # else pydantic.ValidationError raised
        super().__init__(detail=detail, **kwargs)  # type: ignore[call-arg]
