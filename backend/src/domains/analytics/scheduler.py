"""
Sends the weekly visits report from inside the API process (no cron on the server).

Every few minutes, the loop checks whether the latest scheduled report (Friday 20:00,
Paris time) was sent, and sends it if not. Each report is claimed in the database
before being sent, so it goes out once even with several workers, and a report missed
while the API was down is sent as soon as it restarts.
"""
import asyncio
import logging
from datetime import datetime, timezone

from src.config.database import SessionLocal
from src.config.settings import get_settings
from src.infrastructure.external_services.email_service import MailJetClient
from .repository import AnalyticsRepository
from .report import build_report, latest_report_time, render_report_email

logger = logging.getLogger("api.analytics")

CHECK_INTERVAL_SECONDS = 10 * 60


def send_due_report(repo: AnalyticsRepository, mailjet_client: MailJetClient, to_email: str, now: datetime) -> bool:
    """Send the latest scheduled report if it was not sent yet. Returns True if it was sent."""
    report_time = latest_report_time(now)
    period_end = report_time.astimezone(timezone.utc)

    # First run ever: the past week predates the tracking, skip it and start with the next one.
    if not repo.has_any_report():
        repo.claim_report(period_end)
        return False

    if not repo.claim_report(period_end):
        return False

    try:
        subject, html, text = render_report_email(build_report(repo, report_time))
        settings = get_settings()
        mailjet_client.send_email(
            from_email=settings.MAIL_FROM_EMAIL,
            from_name=settings.MAIL_FROM_NAME,
            to_email=to_email,
            to_name=None,
            subject=subject,
            html=html,
            text=text,
        )
    except Exception:
        # Release the claim so the next check retries.
        repo.release_report(period_end)
        raise

    logger.info("Weekly visits report sent (period ending %s)", period_end.isoformat())
    return True


def _check_once(to_email: str) -> None:
    settings = get_settings()
    db = SessionLocal()
    try:
        send_due_report(
            AnalyticsRepository(db),
            MailJetClient(settings.MAILJET_API_KEY, settings.MAILJET_API_SECRET_KEY),
            to_email,
            datetime.now(timezone.utc),
        )
    finally:
        db.close()


async def run_weekly_report_loop(to_email: str) -> None:
    while True:
        try:
            await asyncio.to_thread(_check_once, to_email)
        except Exception:
            logger.exception("Failed to send the weekly visits report, will retry")
        await asyncio.sleep(CHECK_INTERVAL_SECONDS)
