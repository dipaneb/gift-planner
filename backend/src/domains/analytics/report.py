"""Weekly visits report: which period it covers, the numbers, and the email content."""
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from .models import Visit
from .repository import AnalyticsRepository

REPORT_TIMEZONE = ZoneInfo("Europe/Paris")
REPORT_WEEKDAY = 4  # Friday (Monday = 0)
REPORT_HOUR = 20

FRENCH_WEEKDAYS = ["lun.", "mar.", "mer.", "jeu.", "ven.", "sam.", "dim."]


def latest_report_time(now: datetime) -> datetime:
    """Return the most recent scheduled report time (Friday 20:00 Paris time) that is <= now."""
    local_now = now.astimezone(REPORT_TIMEZONE)
    days_since_report_day = (local_now.weekday() - REPORT_WEEKDAY) % 7
    report_time = (local_now - timedelta(days=days_since_report_day)).replace(
        hour=REPORT_HOUR, minute=0, second=0, microsecond=0
    )
    if report_time > local_now:
        report_time -= timedelta(days=7)
    return report_time


def _week_before(report_time: datetime) -> datetime:
    # Arithmetic on an aware datetime keeps the wall clock time, so DST changes are handled.
    return report_time - timedelta(days=7)


def _as_utc(value: datetime) -> datetime:
    # SQLite (tests) returns naive datetimes, stored in UTC.
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value


@dataclass
class DayStats:
    day: date
    cv_visits: int = 0
    other_visits: int = 0


@dataclass
class WeeklyReportData:
    start: datetime
    end: datetime
    cv_visits: int
    cv_visitors: int
    other_visits: int
    other_visitors: int
    previous_cv_visits: int
    previous_other_visits: int
    total_cv_visits: int
    days: list[DayStats]


def build_report(repo: AnalyticsRepository, report_time: datetime) -> WeeklyReportData:
    """Compute the stats of the week ending at report_time."""
    start = _week_before(report_time)
    previous_start = _week_before(start)

    visits = repo.get_visits_between(start.astimezone(timezone.utc), report_time.astimezone(timezone.utc))
    previous_visits = repo.get_visits_between(previous_start.astimezone(timezone.utc), start.astimezone(timezone.utc))

    cv = [v for v in visits if v.from_cv]
    other = [v for v in visits if not v.from_cv]

    # One row per calendar day (Paris time) touched by the period, including empty days.
    days: dict[date, DayStats] = {}
    day = start.date()
    while day <= report_time.date():
        days[day] = DayStats(day=day)
        day += timedelta(days=1)
    for visit in visits:
        visit_day = _as_utc(visit.created_at).astimezone(REPORT_TIMEZONE).date()
        if visit.from_cv:
            days[visit_day].cv_visits += 1
        else:
            days[visit_day].other_visits += 1

    return WeeklyReportData(
        start=start,
        end=report_time,
        cv_visits=len(cv),
        cv_visitors=_count_visitors(cv),
        other_visits=len(other),
        other_visitors=_count_visitors(other),
        previous_cv_visits=sum(1 for v in previous_visits if v.from_cv),
        previous_other_visits=sum(1 for v in previous_visits if not v.from_cv),
        total_cv_visits=repo.count_cv_visits_before(report_time.astimezone(timezone.utc)),
        days=list(days.values()),
    )


def _count_visitors(visits: list[Visit]) -> int:
    return len({v.visitor_id for v in visits})


def _format_day(day: date) -> str:
    return f"{FRENCH_WEEKDAYS[day.weekday()]} {day.strftime('%d/%m')}"


def _format_evolution(current: int, previous: int) -> str:
    diff = current - previous
    if diff == 0:
        return "= vs semaine précédente"
    return f"{diff:+d} vs semaine précédente ({previous})"


def render_report_email(report: WeeklyReportData) -> tuple[str, str, str]:
    """Return (subject, html, text) for the report email."""
    period = f"du {report.start.strftime('%d/%m %Hh')} au {report.end.strftime('%d/%m %Hh')}"
    subject = f"Gift Planner – {report.cv_visits} visite(s) depuis ton CV cette semaine"

    day_rows_html = "".join(
        f"""<tr>
              <td style="padding:6px 12px; border-bottom:1px solid #e5e7eb;">{_format_day(d.day)}</td>
              <td style="padding:6px 12px; border-bottom:1px solid #e5e7eb; text-align:right; font-weight:700; color:#44ba82;">{d.cv_visits}</td>
              <td style="padding:6px 12px; border-bottom:1px solid #e5e7eb; text-align:right;">{d.other_visits}</td>
            </tr>"""
        for d in report.days
    )

    html = f"""<!DOCTYPE html>
<html lang="fr">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="margin:0; padding:24px 16px; background-color:#f4f5f7; font-family: Arial, Helvetica, sans-serif; color:#1f2937;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="max-width:600px; margin:0 auto; background-color:#ffffff; border-radius:12px; border:1px solid #e5e7eb;">
    <tr>
      <td style="background-color:#44ba82; padding:20px 24px; border-radius:12px 12px 0 0; color:#ffffff; font-size:18px; font-weight:700;">
        Rapport hebdo des visites
      </td>
    </tr>
    <tr>
      <td style="padding:24px;">
        <p style="margin:0 0 20px 0; color:#6b7280; font-size:14px;">Période {period} (heure de Paris)</p>

        <p style="margin:0; font-size:14px; color:#6b7280;">Depuis ton CV</p>
        <p style="margin:4px 0 0 0; font-size:28px; font-weight:700; color:#44ba82;">{report.cv_visits} visite(s)</p>
        <p style="margin:4px 0 20px 0; font-size:14px;">{report.cv_visitors} visiteur(s) unique(s) · {_format_evolution(report.cv_visits, report.previous_cv_visits)}</p>

        <p style="margin:0; font-size:14px; color:#6b7280;">Autres sources</p>
        <p style="margin:4px 0 0 0; font-size:20px; font-weight:700;">{report.other_visits} visite(s)</p>
        <p style="margin:4px 0 24px 0; font-size:14px;">{report.other_visitors} visiteur(s) unique(s) · {_format_evolution(report.other_visits, report.previous_other_visits)}</p>

        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="font-size:14px; border-collapse:collapse;">
          <tr>
            <th style="padding:6px 12px; text-align:left; border-bottom:2px solid #e5e7eb;">Jour</th>
            <th style="padding:6px 12px; text-align:right; border-bottom:2px solid #e5e7eb;">CV</th>
            <th style="padding:6px 12px; text-align:right; border-bottom:2px solid #e5e7eb;">Autres</th>
          </tr>
          {day_rows_html}
        </table>

        <p style="margin:24px 0 0 0; font-size:14px; color:#6b7280;">Total depuis le début : {report.total_cv_visits} visite(s) depuis ton CV.</p>
      </td>
    </tr>
  </table>
</body>
</html>"""

    day_rows_text = "\n".join(
        f"  {_format_day(d.day)} : {d.cv_visits} CV, {d.other_visits} autres" for d in report.days
    )
    text = f"""Rapport hebdo des visites
Période {period} (heure de Paris)

Depuis ton CV : {report.cv_visits} visite(s), {report.cv_visitors} visiteur(s) unique(s) ({_format_evolution(report.cv_visits, report.previous_cv_visits)})
Autres sources : {report.other_visits} visite(s), {report.other_visitors} visiteur(s) unique(s) ({_format_evolution(report.other_visits, report.previous_other_visits)})

Jour par jour :
{day_rows_text}

Total depuis le début : {report.total_cv_visits} visite(s) depuis ton CV.
"""
    return subject, html, text
