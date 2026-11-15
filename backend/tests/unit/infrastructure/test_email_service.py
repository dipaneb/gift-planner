from unittest.mock import MagicMock, patch

from src.infrastructure.external_services.email_service import MailJetClient


def _sent_payload(**kwargs):
    with patch("src.infrastructure.external_services.email_service.httpx.Client") as client_class:
        http = client_class.return_value.__enter__.return_value
        http.post.return_value = MagicMock()
        MailJetClient("key", "secret").send_email(
            from_email="noreply@example.com",
            from_name="Gift Planner",
            to_email="marie@example.com",
            to_name="Marie",
            subject="Hello",
            html="<p>Hello</p>",
            **kwargs,
        )
        return http.post.call_args.kwargs["json"]["Messages"][0]


def test_reply_to_is_sent_when_given():
    message = _sent_payload(reply_to="support@example.com")
    assert message["ReplyTo"] == {"Email": "support@example.com"}


def test_no_reply_to_by_default():
    assert "ReplyTo" not in _sent_payload()
