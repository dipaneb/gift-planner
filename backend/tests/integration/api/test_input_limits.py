"""Out-of-range or dangerous values must be rejected with a 422, never reach the database."""
import pytest


class TestGiftLimits:
    @pytest.mark.parametrize("payload", [
        {"price": "1000000.01"},
        {"price": "99999999999"},   # used to overflow NUMERIC(10, 2) -> 500
        {"quantity": 1001},
        {"quantity": 3_000_000_000},  # used to overflow INTEGER -> 500
    ])
    def test_out_of_range_values_are_rejected_on_create(self, client, authenticated_user, payload):
        _, headers = authenticated_user
        response = client.post("/gifts", json={"name": "Gift", **payload}, headers=headers)
        assert response.status_code == 422

    def test_maximum_values_are_accepted(self, client, authenticated_user):
        _, headers = authenticated_user
        response = client.post("/gifts", json={"name": "Gift", "price": "1000000", "quantity": 1000}, headers=headers)
        assert response.status_code == 201

    def test_out_of_range_values_are_rejected_on_update(self, client, authenticated_user):
        _, headers = authenticated_user
        gift = client.post("/gifts", json={"name": "Gift"}, headers=headers).json()
        response = client.patch(f"/gifts/{gift['id']}", json={"price": "99999999999"}, headers=headers)
        assert response.status_code == 422


class TestGiftUrl:
    @pytest.mark.parametrize("url", [
        "javascript:alert(document.cookie)",
        "JavaScript:alert(1)",
        "data:text/html,<script>alert(1)</script>",
        "ftp://example.com/file",
        "https://",
    ])
    def test_dangerous_or_invalid_urls_are_rejected(self, client, authenticated_user, url):
        _, headers = authenticated_user
        response = client.post("/gifts", json={"name": "Gift", "url": url}, headers=headers)
        assert response.status_code == 422

    def test_dangerous_url_is_rejected_on_update(self, client, authenticated_user):
        _, headers = authenticated_user
        gift = client.post("/gifts", json={"name": "Gift"}, headers=headers).json()
        response = client.patch(f"/gifts/{gift['id']}", json={"url": "javascript:alert(1)"}, headers=headers)
        assert response.status_code == 422

    def test_url_without_scheme_gets_https(self, client, authenticated_user):
        _, headers = authenticated_user
        response = client.post("/gifts", json={"name": "Gift", "url": "amazon.fr/dp/B0BVNQ3Q3W"}, headers=headers)
        assert response.status_code == 201
        assert response.json()["url"] == "https://amazon.fr/dp/B0BVNQ3Q3W"


class TestBudgetLimits:
    def test_budget_above_maximum_is_rejected(self, client, authenticated_user):
        _, headers = authenticated_user
        response = client.patch("/users/me/budget", json={"budget": "99999999999"}, headers=headers)
        assert response.status_code == 422
