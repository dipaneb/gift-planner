def mask_email(email: str | None) -> str:
    """
    Email address for the logs: enough to tell users apart and spot a provider issue,
    without storing the address itself. "marie.dupont@gmail.com" -> "ma***@gmail.com".
    Logs are kept, copied and read by more people than the database: no personal data in them.
    """
    if not email:
        return "<none>"
    local, _, domain = email.partition("@")
    return f"{local[:2]}***@{domain}" if domain else "***"
