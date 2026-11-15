from starlette.types import ASGIApp, Message, Receive, Scope, Send

# The API only returns JSON, so the browser-hardening headers that matter are few.
# (The frontend's own headers, CSP included, are set by Caddy: frontend/nixpacks.toml.)
SECURITY_HEADERS = {
    # Only ever reach the API over HTTPS (1 year)
    "strict-transport-security": "max-age=31536000",
    # Never guess a content type: JSON stays JSON
    "x-content-type-options": "nosniff",
    # Nothing to display in a frame
    "x-frame-options": "DENY",
    "content-security-policy": "default-src 'none'; frame-ancestors 'none'",
    "referrer-policy": "no-referrer",
    # Responses hold personal data (gifts, budget, tokens): no browser or proxy cache
    "cache-control": "no-store",
}


class SecurityHeadersMiddleware:
    """Pure ASGI middleware: adds SECURITY_HEADERS to every HTTP response, without overriding
    a header a route set itself."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def send_with_headers(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                present = {name.lower() for name, _ in headers}
                for name, value in SECURITY_HEADERS.items():
                    if name.encode() not in present:
                        headers.append((name.encode(), value.encode()))
                message["headers"] = headers
            await send(message)

        await self.app(scope, receive, send_with_headers)
