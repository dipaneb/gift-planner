import logging

from src.core.privacy import mask_email


def test_mask_email_keeps_a_hint_and_the_domain():
    assert mask_email("marie.dupont@gmail.com") == "ma***@gmail.com"


def test_mask_email_short_or_missing_values():
    assert mask_email("a@b.fr") == "a***@b.fr"
    assert mask_email("not-an-email") == "***"
    assert mask_email(None) == "<none>"
    assert mask_email("") == "<none>"


def test_failed_login_does_not_log_the_address(client, caplog):
    with caplog.at_level(logging.INFO):
        client.post("/auth/login", data={"username": "marie.dupont@gmail.com", "password": "Wrong123!"})

    assert "marie.dupont@gmail.com" not in caplog.text
    assert "ma***@gmail.com" in caplog.text
