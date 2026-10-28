from datetime import datetime
from typing import Annotated

from fastapi import Depends
from sqlalchemy import select, delete, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.infrastructure.database.session import get_db
from .models import Visit, WeeklyReport


class AnalyticsRepository:
    def __init__(self, db: Annotated[Session, Depends(get_db)]):
        self.db = db

    def create_visit(self, visit: Visit) -> Visit:
        self.db.add(visit)
        self.db.commit()
        return visit

    def get_visits_between(self, start: datetime, end: datetime) -> list[Visit]:
        stmt = select(Visit).where(Visit.created_at >= start, Visit.created_at < end)
        return list(self.db.execute(stmt).scalars().all())

    def count_cv_visits_before(self, end: datetime) -> int:
        stmt = select(func.count(Visit.id)).where(Visit.from_cv.is_(True), Visit.created_at < end)
        return self.db.execute(stmt).scalar() or 0

    def has_any_report(self) -> bool:
        return self.db.execute(select(WeeklyReport.period_end).limit(1)).first() is not None

    def claim_report(self, period_end: datetime) -> bool:
        """
        Mark the report as being sent.
        Returns False if it was already claimed (sent before, or by another worker).
        """
        self.db.add(WeeklyReport(period_end=period_end))
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            return False
        return True

    def release_report(self, period_end: datetime) -> None:
        """Remove the claim so the report is retried (used when sending failed)."""
        self.db.execute(delete(WeeklyReport).where(WeeklyReport.period_end == period_end))
        self.db.commit()
