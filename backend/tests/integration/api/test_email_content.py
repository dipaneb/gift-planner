"""
What ends up inside the emails we send.

Anyone can register with someone else's email address and choose any name. Those emails
leave from our domain, so they must never carry attacker-controlled HTML or text to an
address whose owner has not proven they own it.
"""
from fastapi import status

from src.domains.auth.password_handler import get_password_hash
from src.domains.users.models import User
from src.infrastructure.external_services.email_templates import get_email_template

PHISHING_NAME = '<a href="https://evil.example">Claim your gift card</a>'


def _sent_email(mock_mailjet):
    send_email = mock_mailjet.return_value.send_email
    send_email.assert_called_once()
    return send_email.call_args.kwargs


def _register(client, name=PHISHING_NAME, locale="fr"):
    return client.post("/auth/register", json={
        "email": "victim@example.com",
        "password": "SecurePass123!",
        "confirmed_password": "SecurePass123!",
        "name": name,
        "locale": locale,
    })


def _add_user(db_session, *, name, is_verified):
    user = User(
        email="someone@example.com",
        password_hash=get_password_hash("SecurePass123!"),
        name=name,
        is_verified=is_verified,
    )
    db_session.add(user)
    db_session.commit()
    return user


class TestVerificationEmail:
    def test_name_chosen_at_registration_is_not_in_the_email(self, client, mock_mailjet):
        assert _register(client).status_code == status.HTTP_201_CREATED

        email = _sent_email(mock_mailjet)
        assert "evil.example" not in email["html"]
        assert "evil.example" not in email["text"]
        assert "Claim your gift card" not in email["html"]
        # Displayed by the mail client in the "To:" header
        assert email["to_name"] is None

    def test_unknown_locale_is_not_copied_into_the_link(self, client, mock_mailjet):
        assert _register(client, name="Marie", locale='">').status_code == status.HTTP_201_CREATED

        email = _sent_email(mock_mailjet)
        assert "locale=" not in email["text"]
        assert '">"' not in email["html"]

    def test_supported_locale_is_kept_in_the_link(self, client, mock_mailjet):
        _register(client, name="Marie", locale="fr")

        assert "&locale=fr" in _sent_email(mock_mailjet)["text"]


class TestResetPasswordEmail:
    def test_unverified_account_gets_no_name(self, client, db_session, mock_mailjet):
        _add_user(db_session, name=PHISHING_NAME, is_verified=False)

        client.post("/auth/forgot-password", json={"email": "someone@example.com"})

        email = _sent_email(mock_mailjet)
        assert "evil.example" not in email["html"]
        assert "evil.example" not in email["text"]
        assert email["to_name"] is None

    def test_verified_account_is_greeted_by_its_name(self, client, db_session, mock_mailjet):
        _add_user(db_session, name="Marie", is_verified=True)

        client.post("/auth/forgot-password", json={"email": "someone@example.com", "locale": "fr"})

        email = _sent_email(mock_mailjet)
        assert "Bonjour Marie," in email["html"]
        assert "Bonjour Marie," in email["text"]
        assert email["to_name"] == "Marie"

    def test_verified_account_name_is_html_escaped(self, client, db_session, mock_mailjet):
        _add_user(db_session, name="Tom <b>& Jerry</b>", is_verified=True)

        client.post("/auth/forgot-password", json={"email": "someone@example.com"})

        html = _sent_email(mock_mailjet)["html"]
        assert "Tom &lt;b&gt;&amp; Jerry&lt;/b&gt;" in html
        assert "<b>" not in html


class TestTemplatesEscaping:
    def test_every_html_template_escapes_the_name(self):
        for template_type in ("register", "reset_password"):
            for locale in ("en", "fr"):
                html = get_email_template(template_type, locale)["html"]("https://app/x?token=abc", 1, PHISHING_NAME)
                assert "<a href=\"https://evil.example\">" not in html
                assert "&lt;a href=&quot;https://evil.example&quot;&gt;" in html
