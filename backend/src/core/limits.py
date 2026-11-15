"""Bounds shared by the schemas, so that out-of-range values are rejected with a 422
instead of reaching the database and failing there with a 500."""
from decimal import Decimal
from urllib.parse import urlsplit

# Gift prices and budgets are stored as NUMERIC(10, 2) (max 99,999,999.99).
# A million euros is far beyond any gift, and leaves room for price x quantity.
MAX_AMOUNT = Decimal("1000000")
# quantity is an INTEGER column; a thousand copies of a gift is already generous.
MAX_QUANTITY = 1000

ALLOWED_URL_SCHEMES = {"http", "https"}


def normalize_gift_url(value: str | None) -> str | None:
    """
    Clean a gift link: empty means no link, a missing scheme defaults to https
    ("amazon.fr/..." is what people paste), and only http(s) links are accepted.
    The link is rendered as <a href>: a "javascript:..." URL would run code on click.
    """
    if value is None:
        return None
    value = value.strip()
    if not value:
        return None
    if not urlsplit(value).scheme:
        value = f"https://{value}"
    parts = urlsplit(value)
    if parts.scheme.lower() not in ALLOWED_URL_SCHEMES or not parts.netloc:
        raise ValueError("URL must start with http:// or https://")
    return value
