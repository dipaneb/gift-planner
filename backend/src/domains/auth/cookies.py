from fastapi import Response

from src.config.settings import get_settings

settings = get_settings()

REFRESH_TOKEN_COOKIE = "refresh_token"
# The cookie is only sent to /auth/* (refresh, logout). Any response can still set it,
# including a response from /users/*, as long as it uses the same path.
REFRESH_TOKEN_COOKIE_PATH = "/auth"


def set_refresh_token_cookie(response: Response, raw_refresh_token: str) -> None:
    response.set_cookie(
        key=REFRESH_TOKEN_COOKIE,
        value=raw_refresh_token,
        httponly=True,
        secure=(settings.ENV == "production"),
        samesite="strict",
        path=REFRESH_TOKEN_COOKIE_PATH,
        max_age=settings.REFRESH_TOKEN_TTL_DAYS * 86400,
    )


def delete_refresh_token_cookie(response: Response) -> None:
    response.delete_cookie(key=REFRESH_TOKEN_COOKIE, path=REFRESH_TOKEN_COOKIE_PATH)
