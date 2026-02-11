import pytest
import uuid
from fastapi.testclient import TestClient


class TestRecipientGiftLinkingFromRecipientSide:
    """Tests for linking gifts to recipients via the recipients API."""

    def test_create_recipient_with_gifts(self, client, authenticated_user):
        user, headers = authenticated_user

        # Create a gift first
        gift_resp = client.post("/gifts", json={"name": "Chess set"}, headers=headers)
        assert gift_resp.status_code == 201
        gid = gift_resp.json()["id"]

        # Create recipient with that gift
        recipient_data = {
            "name": "Mom",
            "gift_ids": [gid],
        }
        response = client.post("/recipients", json=recipient_data, headers=headers)

        assert response.status_code == 201
        data = response.json()
        assert data["gift_ids"] == [gid]

    def test_create_recipient_with_multiple_gifts(self, client, authenticated_user):
        user, headers = authenticated_user

        gift1 = client.post("/gifts", json={"name": "Gift A"}, headers=headers).json()
        gift2 = client.post("/gifts", json={"name": "Gift B"}, headers=headers).json()

        recipient_data = {
            "name": "Dad",
            "gift_ids": [gift1["id"], gift2["id"]],
        }
        response = client.post("/recipients", json=recipient_data, headers=headers)

        assert response.status_code == 201
        data = response.json()
        assert set(data["gift_ids"]) == {gift1["id"], gift2["id"]}

    def test_create_recipient_without_gifts(self, client, authenticated_user):
        user, headers = authenticated_user

        recipient_data = {"name": "Colleague"}
        response = client.post("/recipients", json=recipient_data, headers=headers)

        assert response.status_code == 201
        assert response.json()["gift_ids"] == []

    def test_create_recipient_with_invalid_gift_returns_404(self, client, authenticated_user):
        user, headers = authenticated_user

        recipient_data = {
            "name": "Friend",
            "gift_ids": [str(uuid.uuid4())],
        }
        response = client.post("/recipients", json=recipient_data, headers=headers)

        assert response.status_code == 404

    def test_create_recipient_with_other_users_gift_returns_404(
        self, client, authenticated_user, other_user_with_gifts
    ):
        user, headers = authenticated_user
        other_user, other_gifts = other_user_with_gifts

        recipient_data = {
            "name": "Friend",
            "gift_ids": [other_gifts[0]["id"]],
        }
        response = client.post("/recipients", json=recipient_data, headers=headers)

        assert response.status_code == 404

    def test_update_recipient_add_gifts(self, client, authenticated_user):
        user, headers = authenticated_user

        # Create gift and recipient separately
        gift_resp = client.post("/gifts", json={"name": "Scarf"}, headers=headers)
        gid = gift_resp.json()["id"]

        recipient_resp = client.post("/recipients", json={"name": "Mom"}, headers=headers)
        rid = recipient_resp.json()["id"]

        # Update recipient to add gift
        update_data = {"gift_ids": [gid]}
        response = client.patch(f"/recipients/{rid}", json=update_data, headers=headers)

        assert response.status_code == 200
        assert response.json()["gift_ids"] == [gid]

    def test_update_recipient_replace_gifts(self, client, authenticated_user):
        user, headers = authenticated_user

        gift1 = client.post("/gifts", json={"name": "Gift A"}, headers=headers).json()
        gift2 = client.post("/gifts", json={"name": "Gift B"}, headers=headers).json()

        # Create recipient with gift1
        recipient_resp = client.post(
            "/recipients",
            json={"name": "Mom", "gift_ids": [gift1["id"]]},
            headers=headers,
        )
        rid = recipient_resp.json()["id"]

        # Replace with gift2
        update_data = {"gift_ids": [gift2["id"]]}
        response = client.patch(f"/recipients/{rid}", json=update_data, headers=headers)

        assert response.status_code == 200
        assert response.json()["gift_ids"] == [gift2["id"]]

    def test_update_recipient_clear_gifts(self, client, authenticated_user):
        user, headers = authenticated_user

        gift_resp = client.post("/gifts", json={"name": "Scarf"}, headers=headers)
        gid = gift_resp.json()["id"]

        recipient_resp = client.post(
            "/recipients",
            json={"name": "Mom", "gift_ids": [gid]},
            headers=headers,
        )
        rid = recipient_resp.json()["id"]

        # Clear gifts
        update_data = {"gift_ids": []}
        response = client.patch(f"/recipients/{rid}", json=update_data, headers=headers)

        assert response.status_code == 200
        assert response.json()["gift_ids"] == []

    def test_update_recipient_with_invalid_gift_returns_404(self, client, authenticated_user):
        user, headers = authenticated_user

        recipient_resp = client.post("/recipients", json={"name": "Mom"}, headers=headers)
        rid = recipient_resp.json()["id"]

        update_data = {"gift_ids": [str(uuid.uuid4())]}
        response = client.patch(f"/recipients/{rid}", json=update_data, headers=headers)

        assert response.status_code == 404

    def test_update_recipient_with_other_users_gift_returns_404(
        self, client, authenticated_user, other_user_with_gifts
    ):
        user, headers = authenticated_user
        other_user, other_gifts = other_user_with_gifts

        recipient_resp = client.post("/recipients", json={"name": "Mom"}, headers=headers)
        rid = recipient_resp.json()["id"]

        update_data = {"gift_ids": [other_gifts[0]["id"]]}
        response = client.patch(f"/recipients/{rid}", json=update_data, headers=headers)

        assert response.status_code == 404

    def test_update_recipient_without_gift_ids_preserves_existing(self, client, authenticated_user):
        """Updating other fields without sending gift_ids should not change gifts."""
        user, headers = authenticated_user

        gift_resp = client.post("/gifts", json={"name": "Scarf"}, headers=headers)
        gid = gift_resp.json()["id"]

        recipient_resp = client.post(
            "/recipients",
            json={"name": "Mom", "gift_ids": [gid]},
            headers=headers,
        )
        rid = recipient_resp.json()["id"]

        # Update name only — gift_ids omitted
        update_data = {"name": "Mother"}
        response = client.patch(f"/recipients/{rid}", json=update_data, headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Mother"
        assert data["gift_ids"] == [gid]

    def test_get_recipient_by_id_includes_gift_ids(self, client, authenticated_user):
        user, headers = authenticated_user

        gift_resp = client.post("/gifts", json={"name": "Book"}, headers=headers)
        gid = gift_resp.json()["id"]

        recipient_resp = client.post(
            "/recipients",
            json={"name": "Sis", "gift_ids": [gid]},
            headers=headers,
        )
        rid = recipient_resp.json()["id"]

        response = client.get(f"/recipients/{rid}", headers=headers)

        assert response.status_code == 200
        assert response.json()["gift_ids"] == [gid]

    def test_get_recipients_list_includes_gift_ids(self, client, authenticated_user):
        user, headers = authenticated_user

        gift_resp = client.post("/gifts", json={"name": "Puzzle"}, headers=headers)
        gid = gift_resp.json()["id"]

        client.post(
            "/recipients",
            json={"name": "Friend", "gift_ids": [gid]},
            headers=headers,
        )

        response = client.get("/recipients", headers=headers)

        assert response.status_code == 200
        items = response.json()["items"]
        assert len(items) == 1
        assert items[0]["gift_ids"] == [gid]


class TestBidirectionalLinking:
    """Tests verifying that N-N links are visible from both sides."""

    def test_link_from_gift_visible_on_recipient(self, client, authenticated_user):
        """Creating a gift with recipient_ids should reflect in the recipient's gift_ids."""
        user, headers = authenticated_user

        recipient_resp = client.post("/recipients", json={"name": "Mom"}, headers=headers)
        rid = recipient_resp.json()["id"]

        gift_resp = client.post(
            "/gifts",
            json={"name": "Scarf", "recipient_ids": [rid]},
            headers=headers,
        )
        gid = gift_resp.json()["id"]

        # Check recipient now shows this gift
        recipient = client.get(f"/recipients/{rid}", headers=headers).json()
        assert gid in recipient["gift_ids"]

    def test_link_from_recipient_visible_on_gift(self, client, authenticated_user):
        """Creating a recipient with gift_ids should reflect in the gift's recipient_ids."""
        user, headers = authenticated_user

        gift_resp = client.post("/gifts", json={"name": "Camera"}, headers=headers)
        gid = gift_resp.json()["id"]

        recipient_resp = client.post(
            "/recipients",
            json={"name": "Dad", "gift_ids": [gid]},
            headers=headers,
        )
        rid = recipient_resp.json()["id"]

        # Check gift now shows this recipient
        gift = client.get(f"/gifts/{gid}", headers=headers).json()
        assert rid in gift["recipient_ids"]

    def test_update_gift_recipients_visible_on_recipient(self, client, authenticated_user):
        user, headers = authenticated_user

        recipient_resp = client.post("/recipients", json={"name": "Mom"}, headers=headers)
        rid = recipient_resp.json()["id"]

        gift_resp = client.post("/gifts", json={"name": "Scarf"}, headers=headers)
        gid = gift_resp.json()["id"]

        # Link via gift update
        client.patch(f"/gifts/{gid}", json={"recipient_ids": [rid]}, headers=headers)

        # Verify on recipient side
        recipient = client.get(f"/recipients/{rid}", headers=headers).json()
        assert gid in recipient["gift_ids"]

    def test_update_recipient_gifts_visible_on_gift(self, client, authenticated_user):
        user, headers = authenticated_user

        gift_resp = client.post("/gifts", json={"name": "Camera"}, headers=headers)
        gid = gift_resp.json()["id"]

        recipient_resp = client.post("/recipients", json={"name": "Dad"}, headers=headers)
        rid = recipient_resp.json()["id"]

        # Link via recipient update
        client.patch(f"/recipients/{rid}", json={"gift_ids": [gid]}, headers=headers)

        # Verify on gift side
        gift = client.get(f"/gifts/{gid}", headers=headers).json()
        assert rid in gift["recipient_ids"]

    def test_clear_link_from_gift_reflected_on_recipient(self, client, authenticated_user):
        user, headers = authenticated_user

        recipient_resp = client.post("/recipients", json={"name": "Mom"}, headers=headers)
        rid = recipient_resp.json()["id"]

        gift_resp = client.post(
            "/gifts",
            json={"name": "Scarf", "recipient_ids": [rid]},
            headers=headers,
        )
        gid = gift_resp.json()["id"]

        # Clear from gift side
        client.patch(f"/gifts/{gid}", json={"recipient_ids": []}, headers=headers)

        # Verify recipient no longer has this gift
        recipient = client.get(f"/recipients/{rid}", headers=headers).json()
        assert gid not in recipient["gift_ids"]

    def test_clear_link_from_recipient_reflected_on_gift(self, client, authenticated_user):
        user, headers = authenticated_user

        gift_resp = client.post("/gifts", json={"name": "Camera"}, headers=headers)
        gid = gift_resp.json()["id"]

        recipient_resp = client.post(
            "/recipients",
            json={"name": "Dad", "gift_ids": [gid]},
            headers=headers,
        )
        rid = recipient_resp.json()["id"]

        # Clear from recipient side
        client.patch(f"/recipients/{rid}", json={"gift_ids": []}, headers=headers)

        # Verify gift no longer has this recipient
        gift = client.get(f"/gifts/{gid}", headers=headers).json()
        assert rid not in gift["recipient_ids"]

    def test_many_to_many_multiple_gifts_multiple_recipients(self, client, authenticated_user):
        """Multiple recipients can share multiple gifts."""
        user, headers = authenticated_user

        g1 = client.post("/gifts", json={"name": "Gift A"}, headers=headers).json()
        g2 = client.post("/gifts", json={"name": "Gift B"}, headers=headers).json()

        r1 = client.post(
            "/recipients",
            json={"name": "Recipient 1", "gift_ids": [g1["id"], g2["id"]]},
            headers=headers,
        ).json()

        r2 = client.post(
            "/recipients",
            json={"name": "Recipient 2", "gift_ids": [g1["id"]]},
            headers=headers,
        ).json()

        # Verify from recipient side
        r1_data = client.get(f"/recipients/{r1['id']}", headers=headers).json()
        assert set(r1_data["gift_ids"]) == {g1["id"], g2["id"]}

        r2_data = client.get(f"/recipients/{r2['id']}", headers=headers).json()
        assert r2_data["gift_ids"] == [g1["id"]]

        # Verify from gift side
        g1_data = client.get(f"/gifts/{g1['id']}", headers=headers).json()
        assert set(g1_data["recipient_ids"]) == {r1["id"], r2["id"]}

        g2_data = client.get(f"/gifts/{g2['id']}", headers=headers).json()
        assert g2_data["recipient_ids"] == [r1["id"]]

    def test_delete_gift_removes_link_from_recipient(self, client, authenticated_user):
        user, headers = authenticated_user

        gift_resp = client.post("/gifts", json={"name": "Camera"}, headers=headers)
        gid = gift_resp.json()["id"]

        recipient_resp = client.post(
            "/recipients",
            json={"name": "Dad", "gift_ids": [gid]},
            headers=headers,
        )
        rid = recipient_resp.json()["id"]

        # Delete the gift
        delete_resp = client.delete(f"/gifts/{gid}", headers=headers)
        assert delete_resp.status_code == 204

        # Recipient should no longer list the gift
        recipient = client.get(f"/recipients/{rid}", headers=headers).json()
        assert gid not in recipient["gift_ids"]

    def test_delete_recipient_removes_link_from_gift(self, client, authenticated_user):
        user, headers = authenticated_user

        recipient_resp = client.post("/recipients", json={"name": "Mom"}, headers=headers)
        rid = recipient_resp.json()["id"]

        gift_resp = client.post(
            "/gifts",
            json={"name": "Scarf", "recipient_ids": [rid]},
            headers=headers,
        )
        gid = gift_resp.json()["id"]

        # Delete the recipient
        delete_resp = client.delete(f"/recipients/{rid}", headers=headers)
        assert delete_resp.status_code == 204

        # Gift should no longer list the recipient
        gift = client.get(f"/gifts/{gid}", headers=headers).json()
        assert rid not in gift["recipient_ids"]
