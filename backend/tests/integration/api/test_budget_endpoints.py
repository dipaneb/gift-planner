import pytest
from decimal import Decimal
from fastapi import status

from src.domains.users.models import User
from src.domains.auth.password_handler import get_password_hash


class TestBudgetEndpoints:

    @pytest.fixture
    def registered_user(self, db_session):
        user = User(
            email="budget@example.com",
            password_hash=get_password_hash("SecurePass123!"),
            name="Budget User",
            is_verified=True
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    @pytest.fixture
    def access_token(self, client, registered_user):
        response = client.post(
            "/auth/login",
            data={
                "username": "budget@example.com",
                "password": "SecurePass123!"
            }
        )
        return response.json()["access_token"]

    @pytest.fixture
    def auth_headers(self, access_token):
        return {"Authorization": f"Bearer {access_token}"}

    # ==================
    # PATCH /users/me/budget
    # ==================

    def test_set_budget_success(self, client, auth_headers, registered_user):
        response = client.patch(
            "/users/me/budget",
            json={"budget": 500.00},
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["budget"] == "500.00"
        assert data["id"] == str(registered_user.id)

    def test_update_budget_replaces_existing(self, client, auth_headers):
        client.patch("/users/me/budget", json={"budget": 100.00}, headers=auth_headers)

        response = client.patch(
            "/users/me/budget",
            json={"budget": 250.50},
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["budget"] == "250.50"

    def test_set_budget_zero_returns_422(self, client, auth_headers):
        response = client.patch(
            "/users/me/budget",
            json={"budget": 0},
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_set_budget_negative_returns_422(self, client, auth_headers):
        response = client.patch(
            "/users/me/budget",
            json={"budget": -10.00},
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_set_budget_missing_body_returns_422(self, client, auth_headers):
        response = client.patch(
            "/users/me/budget",
            json={},
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_set_budget_without_token_returns_401(self, client):
        response = client.patch(
            "/users/me/budget",
            json={"budget": 100.00},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # ==================
    # DELETE /users/me/budget
    # ==================

    def test_delete_budget_success(self, client, auth_headers):
        client.patch("/users/me/budget", json={"budget": 100.00}, headers=auth_headers)

        response = client.delete("/users/me/budget", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["budget"] is None

    def test_delete_budget_when_none(self, client, auth_headers):
        response = client.delete("/users/me/budget", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["budget"] is None

    def test_delete_budget_without_token_returns_401(self, client):
        response = client.delete("/users/me/budget")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # ==================
    # GET /users/me (budget visibility)
    # ==================

    def test_me_shows_budget_after_set(self, client, auth_headers):
        client.patch("/users/me/budget", json={"budget": 999.99}, headers=auth_headers)

        response = client.get("/users/me", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["budget"] == "999.99"

    def test_me_shows_null_budget_by_default(self, client, auth_headers):
        response = client.get("/users/me", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["budget"] is None
