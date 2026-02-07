from typing import Annotated, Literal

from fastapi import Depends, Query
from pydantic import BaseModel


def pagination_parameters(
    sort: Literal["asc", "desc", "default"] = Query(default="default", description="Sort order by name"),
    page: int = Query(default=1, ge=1, description="Page number"),
    limit: int = Query(default=10, ge=1, le=100, description="Items per page"),
):
    """
    Dependency for pagination parameters.
    Returns dict with sort, page, and limit.
    """
    return {"sort": sort, "page": page, "limit": limit}


PaginationDeps = Annotated[dict, Depends(pagination_parameters)]


class PaginationMeta(BaseModel):
    """Pagination metadata."""
    page: int
    limit: int
    total: int
    totalPages: int
    hasPrev: bool
    hasNext: bool
