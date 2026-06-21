"""Email templates for different languages."""

EMAIL_TEMPLATES = {
    "en": {
        "register": {
            "subject": "Verify your email address",
            "html": lambda link, hours: f"""
                <p>Welcome! Please verify your email address by clicking the link below:</p>
                <p><a href="{link}">Verify Email</a></p>
                <p>This link expires in {hours} {"hour" if hours == 1 else "hours"}.</p>
            """,
            "text": lambda link, hours: f"Verify your email: {link}\nThis link expires in {hours} {'hour' if hours == 1 else 'hours'}.",
        },
        "reset_password": {
            "subject": "Reset your password",
            "html": lambda link, minutes: f"""
                <p>Click the link to reset your password:</p>
                <p><a href="{link}">Reset password</a></p>
                <p>This link expires in {minutes} minutes.</p>
            """,
            "text": lambda link, minutes: f"Reset your password: {link}\nThis link expires in {minutes} minutes.",
        },
    },
    "fr": {
        "register": {
            "subject": "Vérifiez votre adresse e-mail",
            "html": lambda link, hours: f"""
                <p>Bienvenue ! Veuillez vérifier votre adresse e-mail en cliquant sur le lien ci-dessous :</p>
                <p><a href="{link}">Vérifier l'e-mail</a></p>
                <p>Ce lien expire dans {hours} {"heure" if hours == 1 else "heures"}.</p>
            """,
            "text": lambda link, hours: f"Vérifiez votre e-mail : {link}\nCe lien expire dans {hours} {'heure' if hours == 1 else 'heures'}.",
        },
        "reset_password": {
            "subject": "Réinitialisez votre mot de passe",
            "html": lambda link, minutes: f"""
                <p>Cliquez sur le lien pour réinitialiser votre mot de passe :</p>
                <p><a href="{link}">Réinitialiser le mot de passe</a></p>
                <p>Ce lien expire dans {minutes} minutes.</p>
            """,
            "text": lambda link, minutes: f"Réinitialisez votre mot de passe : {link}\nCe lien expire dans {minutes} minutes.",
        },
    },
}


def get_email_template(template_type: str, locale: str = "en"):
    """Get email template for specific type and locale.
    
    Args:
        template_type: Type of template ('register' or 'reset_password')
        locale: Language locale ('en' or 'fr')
    
    Returns:
        Dictionary with subject, html, and text template functions
    """
    if locale not in EMAIL_TEMPLATES:
        locale = "en"
    
    if template_type not in EMAIL_TEMPLATES[locale]:
        # Fallback to English if template type not found
        locale = "en"
    
    return EMAIL_TEMPLATES[locale][template_type]
