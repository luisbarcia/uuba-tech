from pydantic import BaseModel
from typing import Any


class ProblemDetail(BaseModel):
    """RFC 9457 Problem Details for HTTP APIs."""

    type: str
    title: str
    status: int
    detail: str
    instance: str = ""
    request_id: str = ""
    errors: list[dict[str, Any]] = []


class PaginationMeta(BaseModel):
    total: int
    page_size: int
    has_more: bool
    offset: int = 0


class ListResponse(BaseModel):
    object: str = "list"
    data: list[Any]
    pagination: PaginationMeta
