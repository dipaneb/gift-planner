from fastapi import status

from src.domains.auth.password_handler import get_password_hash
from src.domains.users.models import User

OLD_PASSWORD = "SecurePass123!"
NEW_PASSWORD = "BrandNew456?"


def _create_user(db_session):
    user = User(
        email="marie@example.com",
        password_hash=get_password_hash(OLD_PASSWORD),
        name="Marie",
        is_verified=True,
    )
    db_session.add(user)
    db_session.commit()
    return user


def _login(client, password=OLD_PASSWORD):
    response = client.post("/auth/login", data={"username": "marie@example.com", "password": password})
    return response


def _change_password(client, access_token, current=OLD_PASSWORD, new=NEW_PASSWORD, confirmed=None):
    return client.patch(
        "/users/me/password",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"current_password": current, "new_password": new, "confirmed_password": confirmed or new},
    )


def _refresh(client, raw_refresh_token):
    return client.post("/auth/refresh", cookies={"refresh_token": raw_refresh_token})


class TestUpdatePassword:
    def test_new_password_works_and_old_one_does_not(self, client, db_session):
        _create_user(db_session)
        login = _login(client)

        assert _change_password(client, login.json()["access_token"]).status_code == status.HTTP_204_NO_CONTENT

        assert _login(client, OLD_PASSWORD).status_code == status.HTTP_401_UNAUTHORIZED
        assert _login(client, NEW_PASSWORD).status_code == status.HTTP_200_OK

    def test_wrong_current_password_is_rejected(self, client, db_session):
        _create_user(db_session)
        login = _login(client)

        response = _change_password(client, login.json()["access_token"], current="NotMyPassword1!")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert _login(client, OLD_PASSWORD).status_code == status.HTTP_200_OK

    def test_weak_new_password_is_rejected(self, client, db_session):
        _create_user(db_session)
        login = _login(client)

        response = _change_password(client, login.json()["access_token"], new="weakpass")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_requires_authentication(self, client):
        response = client.patch(
            "/users/me/password",
            json={"current_password": OLD_PASSWORD, "new_password": NEW_PASSWORD, "confirmed_password": NEW_PASSWORD},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_other_devices_are_logged_out(self, client, db_session):
        """Someone who knew the old password and opened a session must lose it."""
        _create_user(db_session)
        attacker_session = _login(client).cookies.get("refresh_token")
        my_login = _login(client)

        _change_password(client, my_login.json()["access_token"])

        assert _refresh(client, attacker_session).status_code == status.HTTP_401_UNAUTHORIZED

    def test_current_device_stays_logged_in(self, client, db_session):
        _create_user(db_session)
        my_login = _login(client)
        old_cookie = my_login.cookies.get("refresh_token")

        response = _change_password(client, my_login.json()["access_token"])

        new_cookie = response.cookies.get("refresh_token")
        assert new_cookie and new_cookie != old_cookie
        assert _refresh(client, new_cookie).status_code == status.HTTP_200_OK

    def test_new_cookie_has_the_same_scope_as_the_login_cookie(self, client, db_session):
        _create_user(db_session)
        my_login = _login(client)

        response = _change_password(client, my_login.json()["access_token"])

        set_cookie = response.headers["set-cookie"].lower()
        assert "path=/auth" in set_cookie
        assert "httponly" in set_cookie
        assert "samesite=strict" in set_cookie
