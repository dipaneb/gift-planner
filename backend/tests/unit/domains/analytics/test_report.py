import uuid
from datetime import date, datetime, timezone
from unittest.mock import MagicMock

import pytest

from src.domains.analytics.models import Visit, WeeklyReport
from src.domains.analytics.repository import AnalyticsRepository
from src.domains.analytics.report import (
    REPORT_TIMEZONE,
    build_report,
    latest_report_time,
    render_report_email,
)
from src.domains.analytics.scheduler import send_due_report


def paris(*args) -> datetime:
    return datetime(*args, tzinfo=REPORT_TIMEZONE)


class TestLatestReportTime:

    def test_friday_after_report_hour(self):
        assert latest_report_time(paris(2026, 10, 23, 21, 0)) == paris(2026, 10, 23, 20, 0)

    def test_friday_before_report_hour_returns_previous_week(self):
        assert latest_report_time(paris(2026, 10, 23, 19, 59)) == paris(2026, 10, 16, 20, 0)

    def test_middle_of_week(self):
        assert latest_report_time(paris(2026, 10, 28, 9, 0)) == paris(2026, 10, 23, 20, 0)

    def test_accepts_utc_input(self):
        # 19:30 UTC on Friday = 21:30 in Paris (summer time)
        now = datetime(2026, 10, 23, 19, 30, tzinfo=timezone.utc)
        assert latest_report_time(now) == paris(2026, 10, 23, 20, 0)

    def test_dst_change_keeps_paris_hour(self):
        # Clocks go back on Sunday 25/10/2026: the report stays at 20:00 Paris time
        report_time = latest_report_time(paris(2026, 10, 31, 12, 0))
        assert report_time == paris(2026, 10, 30, 20, 0)
        assert report_time.astimezone(timezone.utc).hour == 19


class TestBuildReport:

    @pytest.fixture
    def repo(self, db_session):
        return AnalyticsRepository(db_session)

    def add_visit(self, db_session, when: datetime, from_cv: bool, visitor_id: uuid.UUID | None = None):
        db_session.add(Visit(
            from_cv=from_cv,
            visitor_id=visitor_id or uuid.uuid4(),
            created_at=when.astimezone(timezone.utc),
        ))
        db_session.commit()

    def test_counts_visits_and_visitors_of_the_week(self, db_session, repo):
        recruiter = uuid.uuid4()
        self.add_visit(db_session, paris(2026, 10, 20, 10, 0), True, recruiter)
        self.add_visit(db_session, paris(2026, 10, 21, 10, 0), True, recruiter)
        self.add_visit(db_session, paris(2026, 10, 22, 10, 0), True)
        self.add_visit(db_session, paris(2026, 10, 22, 11, 0), False)
        # Outside of the period
        self.add_visit(db_session, paris(2026, 10, 23, 20, 30), True)
        # Previous week
        self.add_visit(db_session, paris(2026, 10, 14, 10, 0), True)

        report = build_report(repo, paris(2026, 10, 23, 20, 0))

        assert report.cv_visits == 3
        assert report.cv_visitors == 2
        assert report.other_visits == 1
        assert report.other_visitors == 1
        assert report.previous_cv_visits == 1
        assert report.previous_other_visits == 0
        assert report.total_cv_visits == 4

    def test_days_cover_the_whole_period(self, db_session, repo):
        self.add_visit(db_session, paris(2026, 10, 16, 21, 0), True)
        self.add_visit(db_session, paris(2026, 10, 23, 19, 0), False)

        report = build_report(repo, paris(2026, 10, 23, 20, 0))

        assert report.days[0].day == date(2026, 10, 16)
        assert report.days[-1].day == date(2026, 10, 23)
        assert len(report.days) == 8
        assert (report.days[0].cv_visits, report.days[0].other_visits) == (1, 0)
        assert (report.days[-1].cv_visits, report.days[-1].other_visits) == (0, 1)

    def test_render_email(self, db_session, repo):
        self.add_visit(db_session, paris(2026, 10, 20, 10, 0), True)

        subject, html, text = render_report_email(build_report(repo, paris(2026, 10, 23, 20, 0)))

        assert "1 visite(s) depuis ton CV" in subject
        assert "mar. 20/10" in html
        assert "mar. 20/10 : 1 CV, 0 autres" in text


class TestSendDueReport:

    @pytest.fixture
    def repo(self, db_session):
        return AnalyticsRepository(db_session)

    def test_first_run_skips_the_week_before_tracking(self, db_session, repo):
        mailjet = MagicMock()

        assert send_due_report(repo, mailjet, "me@example.com", paris(2026, 10, 28, 9, 0)) is False

        mailjet.send_email.assert_not_called()
        assert db_session.query(WeeklyReport).count() == 1

    def test_sends_once_per_week(self, db_session, repo):
        repo.claim_report(paris(2026, 10, 16, 20, 0).astimezone(timezone.utc))
        mailjet = MagicMock()

        assert send_due_report(repo, mailjet, "me@example.com", paris(2026, 10, 23, 20, 5)) is True
        assert send_due_report(repo, mailjet, "me@example.com", paris(2026, 10, 23, 20, 15)) is False

        mailjet.send_email.assert_called_once()
        assert mailjet.send_email.call_args.kwargs["to_email"] == "me@example.com"

    def test_failed_send_is_retried(self, db_session, repo):
        repo.claim_report(paris(2026, 10, 16, 20, 0).astimezone(timezone.utc))
        mailjet = MagicMock()
        mailjet.send_email.side_effect = [RuntimeError("Mailjet down"), None]

        with pytest.raises(RuntimeError):
            send_due_report(repo, mailjet, "me@example.com", paris(2026, 10, 23, 20, 5))
        assert send_due_report(repo, mailjet, "me@example.com", paris(2026, 10, 23, 20, 15)) is True

        assert mailjet.send_email.call_count == 2
