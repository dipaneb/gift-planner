import re
from typing import Annotated

from fastapi import Depends

from .models import Visit
from .repository import AnalyticsRepository
from .schemas import VisitCreate

# Crawlers and link-preview fetchers (LinkedIn, Slack, Teams...) that run JavaScript.
# Most of them don't, so they never reach this endpoint, but some do.
BOT_USER_AGENT = re.compile(r"bot|crawl|spider|slurp|preview|headless|lighthouse", re.IGNORECASE)


class AnalyticsService:
    def __init__(self, repo: Annotated[AnalyticsRepository, Depends()]):
        self.repo = repo

    def record_visit(self, data: VisitCreate, user_agent: str | None) -> None:
        """Store a visit, unless it comes from a bot."""
        if user_agent and BOT_USER_AGENT.search(user_agent):
            return

        self.repo.create_visit(Visit(
            from_cv=data.from_cv,
            visitor_id=data.visitor_id,
            user_agent=user_agent[:512] if user_agent else None,
        ))
