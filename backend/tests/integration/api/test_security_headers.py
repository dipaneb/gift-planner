import pytest

from src.core.middlewares.security_headers import SECURITY_HEADERS


@pytest.mark.parametrize("method, path", [
    ("get", "/users/me"),                 # 401, authenticated route
    ("post", "/auth/refresh"),            # 401, auth route
    ("get", "/does-not-exist"),           # 404
])
def test_security_headers_on_every_response(client, method, path):
    response = getattr(client, method)(path)

    for name, value in SECURITY_HEADERS.items():
        assert response.headers[name] == value


def test_cors_preflight_still_works(client):
    response = client.options(
        "/auth/refresh",
        headers={"Origin": "http://localhost:5173", "Access-Control-Request-Method": "POST"},
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"
