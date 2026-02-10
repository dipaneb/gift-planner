import logging

import httpx

logger = logging.getLogger("api.email")


class MailJetClient():
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret

    def send_email(
        self,
        *,
        from_email: str,
        from_name: str,
        to_email: str,
        to_name: str | None,
        subject: str,
        html: str,
        text: str| None = None
    ) -> None:
        payload = {
            "Messages": [
                {
                    "From": {"Email": from_email, "Name": from_name},
                    "To": [{"Email": to_email, "Name": to_name or to_email}],
                    "Subject": subject,
                    "HTMLPart": html,
                    **({"TextPart": text} if text else {}),
                }
            ]
        }

        with httpx.Client(timeout=10) as client:
            try:
                result = client.post("https://api.mailjet.com/v3.1/send", auth=(self.api_key, self.api_secret), json=payload)
                result.raise_for_status()
                logger.info("Email sent to %s (subject: %s)", to_email, subject)
            except httpx.HTTPStatusError:
                logger.error("Mailjet API error sending to %s: %s", to_email, result.status_code)
                raise
            except httpx.RequestError as exc:
                logger.error("Network error sending email to %s: %s", to_email, exc)
                raise

