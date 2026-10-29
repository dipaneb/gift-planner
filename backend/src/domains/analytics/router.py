from typing import Annotated

from fastapi import APIRouter, Depends, Request, status

from src.core.rate_limit import limiter
from .schemas import VisitCreate
from .service import AnalyticsService

router = APIRouter(prefix="/visits", tags=["analytics"])


@router.post("", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("10/minute")
def record_visit(
    request: Request,
    visit: VisitCreate,
    analytics_service: Annotated[AnalyticsService, Depends()],
):
    """Record a visit on the site (called once per browser session, no authentication)."""
    analytics_service.record_visit(visit, request.headers.get("user-agent"))
