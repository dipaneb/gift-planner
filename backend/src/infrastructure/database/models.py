# Import ALL models so SQLAlchemy can register them on Base.metadata.
# Alembic's autogenerate and create_all() only see the tables of imported models:
# removing one of these imports would make a migration drop its table.
# __all__ marks them as used, so linters do not "clean them up".
from src.domains.analytics.models import Visit, WeeklyReport
from src.domains.auth.models import PasswordResetToken, RefreshToken
from src.domains.gifts.models import Gift
from src.domains.groups.models import Group
from src.domains.recipients.models import Recipient
from src.domains.users.models import User

__all__ = [
    "Gift",
    "Group",
    "PasswordResetToken",
    "Recipient",
    "RefreshToken",
    "User",
    "Visit",
    "WeeklyReport",
]
