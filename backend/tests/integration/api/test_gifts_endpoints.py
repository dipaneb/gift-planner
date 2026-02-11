import pytest
import uuid
from fastapi.testclient import TestClient


class TestCreateGiftEndpoint:

    def test_create_gift_success_minimal(self, client, authenticated_user):
        user, headers = authenticated_user

        gift_data = {
            "name": "Chess set",
        }

        response = client.post("/gifts", json=gift_data, headers=headers)

        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["name"] == "Chess set"
        assert data["url"] is None
        assert data["price"] is None
        assert data["status"] == "idee"
        assert data["quantity"] == 1
        assert data["recipient_ids"] == []
        assert data["user_id"] == str(user.id)

    def test_create_gift_success_with_all_fields(self, client, authenticated_user):
        user, headers = authenticated_user

        gift_data = {
            "name": "Canon EOS R50",
            "url": "https://www.amazon.fr/dp/B0BVNQ3Q3W",
            "price": 799.99,
            "status": "achete",
            "quantity": 2,
        }

        response = client.post("/gifts", json=gift_data, headers=headers)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Canon EOS R50"
        assert data["url"] == "https://www.amazon.fr/dp/B0BVNQ3Q3W"
        assert float(data["price"]) == 799.99
        assert data["status"] == "achete"
        assert data["quantity"] == 2

    def test_create_gift_with_recipients(self, client, authenticated_user):
        user, headers = authenticated_user

        # Create a recipient first
        recipient_resp = client.post("/recipients", json={"name": "Mom"}, headers=headers)
        assert recipient_resp.status_code == 201
        rid = recipient_resp.json()["id"]

        gift_data = {
            "name": "Scarf",
            "recipient_ids": [rid],
        }

        response = client.post("/gifts", json=gift_data, headers=headers)

        assert response.status_code == 201
        data = response.json()
        assert data["recipient_ids"] == [rid]

    def test_create_gift_with_multiple_recipients(self, client, authenticated_user):
        user, headers = authenticated_user

        r1 = client.post("/recipients", json={"name": "Mom"}, headers=headers)
        r2 = client.post("/recipients", json={"name": "Dad"}, headers=headers)
        rid1 = r1.json()["id"]
        rid2 = r2.json()["id"]

        gift_data = {
            "name": "Family vacation",
            "recipient_ids": [rid1, rid2],
        }

        response = client.post("/gifts", json=gift_data, headers=headers)

        assert response.status_code == 201
        data = response.json()
        assert sorted(data["recipient_ids"]) == sorted([rid1, rid2])

    def test_create_gift_with_invalid_recipient_returns_404(self, client, authenticated_user):
        user, headers = authenticated_user

        gift_data = {
            "name": "Scarf",
            "recipient_ids": [str(uuid.uuid4())],
        }

        response = client.post("/gifts", json=gift_data, headers=headers)

        assert response.status_code == 404

    def test_create_gift_with_other_user_recipient_returns_404(self, client, authenticated_user, other_user_with_recipients):
        user, headers = authenticated_user
        other_user, other_recipients = other_user_with_recipients

        other_rid = other_recipients[0]["id"]

        gift_data = {
            "name": "Scarf",
            "recipient_ids": [other_rid],
        }

        response = client.post("/gifts", json=gift_data, headers=headers)

        assert response.status_code == 404

    def test_create_gift_requires_authentication(self, client):
        gift_data = {
            "name": "Test Gift",
        }

        response = client.post("/gifts", json=gift_data)
        assert response.status_code == 401

    def test_create_gift_empty_name_returns_422(self, client, authenticated_user):
        user, headers = authenticated_user

        gift_data = {
            "name": "   ",
        }

        response = client.post("/gifts", json=gift_data, headers=headers)
        assert response.status_code == 422

    def test_create_gift_missing_name_returns_422(self, client, authenticated_user):
        user, headers = authenticated_user

        gift_data = {
            "price": 10.00,
        }

        response = client.post("/gifts", json=gift_data, headers=headers)
        assert response.status_code == 422

    def test_create_gift_name_too_long_returns_422(self, client, authenticated_user):
        user, headers = authenticated_user

        gift_data = {
            "name": "A" * 256,
        }

        response = client.post("/gifts", json=gift_data, headers=headers)
        assert response.status_code == 422

    def test_create_gift_price_below_minimum_returns_422(self, client, authenticated_user):
        user, headers = authenticated_user

        gift_data = {
            "name": "Gift",
            "price": 0,
        }

        response = client.post("/gifts", json=gift_data, headers=headers)
        assert response.status_code == 422

    def test_create_gift_quantity_zero_returns_422(self, client, authenticated_user):
        user, headers = authenticated_user

        gift_data = {
            "name": "Gift",
            "quantity": 0,
        }

        response = client.post("/gifts", json=gift_data, headers=headers)
        assert response.status_code == 422

    def test_create_gift_invalid_status_returns_422(self, client, authenticated_user):
        user, headers = authenticated_user

        gift_data = {
            "name": "Gift",
            "status": "invalid_status",
        }

        response = client.post("/gifts", json=gift_data, headers=headers)
        assert response.status_code == 422

    def test_create_gift_normalizes_whitespace(self, client, authenticated_user):
        user, headers = authenticated_user

        gift_data = {
            "name": "  Canon EOS  ",
            "url": "  https://example.com  ",
        }

        response = client.post("/gifts", json=gift_data, headers=headers)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Canon EOS"
        assert data["url"] == "https://example.com"


class TestGetGiftsEndpoint:

    def test_get_gifts_empty_list(self, client, authenticated_user):
        user, headers = authenticated_user

        response = client.get("/gifts", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["meta"]["total"] == 0

    def test_get_gifts_returns_user_gifts_only(self, client, authenticated_user, other_user_with_gifts):
        user, headers = authenticated_user
        other_user, other_gifts = other_user_with_gifts

        # Create gift for authenticated user
        client.post("/gifts", json={"name": "My Gift"}, headers=headers)

        response = client.get("/gifts", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["meta"]["total"] == 1
        assert data["items"][0]["name"] == "My Gift"
        assert data["items"][0]["user_id"] == str(user.id)

    def test_get_gifts_pagination_default(self, client, authenticated_user_with_gifts):
        user, headers, gifts = authenticated_user_with_gifts

        response = client.get("/gifts", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) <= 10
        assert data["meta"]["total"] == 5

    def test_get_gifts_pagination_custom_limit(self, client, authenticated_user_with_gifts):
        user, headers, gifts = authenticated_user_with_gifts

        response = client.get("/gifts?limit=2", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["meta"]["total"] == 5
        assert data["meta"]["totalPages"] == 3

    def test_get_gifts_pagination_page_2(self, client, authenticated_user_with_gifts):
        user, headers, gifts = authenticated_user_with_gifts

        response = client.get("/gifts?page=2&limit=2", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) > 0
        assert data["meta"]["page"] == 2

    def test_get_gifts_sort_ascending(self, client, authenticated_user):
        user, headers = authenticated_user

        client.post("/gifts", json={"name": "Zara gift"}, headers=headers)
        client.post("/gifts", json={"name": "Alice gift"}, headers=headers)
        client.post("/gifts", json={"name": "Bob gift"}, headers=headers)

        response = client.get("/gifts?sort=asc", headers=headers)

        assert response.status_code == 200
        data = response.json()
        names = [item["name"] for item in data["items"]]
        assert names == ["Alice gift", "Bob gift", "Zara gift"]

    def test_get_gifts_sort_descending(self, client, authenticated_user):
        user, headers = authenticated_user

        client.post("/gifts", json={"name": "Zara gift"}, headers=headers)
        client.post("/gifts", json={"name": "Alice gift"}, headers=headers)
        client.post("/gifts", json={"name": "Bob gift"}, headers=headers)

        response = client.get("/gifts?sort=desc", headers=headers)

        assert response.status_code == 200
        data = response.json()
        names = [item["name"] for item in data["items"]]
        assert names == ["Zara gift", "Bob gift", "Alice gift"]

    def test_get_gifts_list_includes_recipient_ids(self, client, authenticated_user):
        user, headers = authenticated_user

        r = client.post("/recipients", json={"name": "Mom"}, headers=headers)
        rid = r.json()["id"]

        client.post(
            "/gifts",
            json={"name": "Scarf", "recipient_ids": [rid]},
            headers=headers,
        )

        response = client.get("/gifts", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) >= 1
        scarf = next(g for g in data["items"] if g["name"] == "Scarf")
        assert scarf["recipient_ids"] == [rid]

    def test_get_gifts_requires_authentication(self, client):
        response = client.get("/gifts")
        assert response.status_code == 401


class TestGetGiftByIdEndpoint:

    def test_get_gift_by_id_success(self, client, authenticated_user):
        user, headers = authenticated_user

        create_response = client.post(
            "/gifts",
            json={"name": "Test Gift", "price": 29.99, "status": "achete"},
            headers=headers
        )
        created = create_response.json()
        gift_id = created["id"]

        response = client.get(f"/gifts/{gift_id}", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == gift_id
        assert data["name"] == "Test Gift"
        assert float(data["price"]) == 29.99
        assert data["status"] == "achete"

    def test_get_gift_by_id_includes_recipient_ids(self, client, authenticated_user):
        user, headers = authenticated_user

        r = client.post("/recipients", json={"name": "Mom"}, headers=headers)
        rid = r.json()["id"]

        create_response = client.post(
            "/gifts",
            json={"name": "Scarf", "recipient_ids": [rid]},
            headers=headers,
        )
        gift_id = create_response.json()["id"]

        response = client.get(f"/gifts/{gift_id}", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["recipient_ids"] == [rid]

    def test_get_gift_not_found_returns_404(self, client, authenticated_user):
        user, headers = authenticated_user

        non_existent_id = str(uuid.uuid4())
        response = client.get(f"/gifts/{non_existent_id}", headers=headers)

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_gift_from_other_user_returns_404(self, client, authenticated_user, other_user_with_gifts):
        user, headers = authenticated_user
        other_user, other_gifts = other_user_with_gifts

        other_gift_id = other_gifts[0]["id"]
        response = client.get(f"/gifts/{other_gift_id}", headers=headers)

        assert response.status_code == 404

    def test_get_gift_requires_authentication(self, client):
        gift_id = str(uuid.uuid4())
        response = client.get(f"/gifts/{gift_id}")
        assert response.status_code == 401


class TestUpdateGiftEndpoint:

    def test_update_gift_name_only(self, client, authenticated_user):
        user, headers = authenticated_user

        create_response = client.post(
            "/gifts",
            json={"name": "Original Name", "price": 15.00},
            headers=headers
        )
        gift_id = create_response.json()["id"]

        update_data = {"name": "Updated Name"}
        response = client.patch(f"/gifts/{gift_id}", json=update_data, headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert float(data["price"]) == 15.00  # Unchanged

    def test_update_gift_status(self, client, authenticated_user):
        user, headers = authenticated_user

        create_response = client.post(
            "/gifts",
            json={"name": "Gift", "status": "idee"},
            headers=headers
        )
        gift_id = create_response.json()["id"]

        update_data = {"status": "achete"}
        response = client.patch(f"/gifts/{gift_id}", json=update_data, headers=headers)

        assert response.status_code == 200
        assert response.json()["status"] == "achete"

    def test_update_gift_multiple_fields(self, client, authenticated_user):
        user, headers = authenticated_user

        create_response = client.post(
            "/gifts",
            json={"name": "Original", "price": 10.00, "quantity": 1},
            headers=headers
        )
        gift_id = create_response.json()["id"]

        update_data = {"name": "New Name", "price": 49.99, "quantity": 3, "status": "commande"}
        response = client.patch(f"/gifts/{gift_id}", json=update_data, headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "New Name"
        assert float(data["price"]) == 49.99
        assert data["quantity"] == 3
        assert data["status"] == "commande"

    def test_update_gift_recipients(self, client, authenticated_user):
        user, headers = authenticated_user

        # Create recipient
        recipient_resp = client.post("/recipients", json={"name": "Mom"}, headers=headers)
        rid = recipient_resp.json()["id"]

        # Create gift without recipients
        create_response = client.post("/gifts", json={"name": "Scarf"}, headers=headers)
        gift_id = create_response.json()["id"]

        # Update to add recipient
        update_data = {"recipient_ids": [rid]}
        response = client.patch(f"/gifts/{gift_id}", json=update_data, headers=headers)

        assert response.status_code == 200
        assert response.json()["recipient_ids"] == [rid]

    def test_update_gift_clear_recipients(self, client, authenticated_user):
        user, headers = authenticated_user

        # Create recipient and gift with that recipient
        recipient_resp = client.post("/recipients", json={"name": "Mom"}, headers=headers)
        rid = recipient_resp.json()["id"]

        create_response = client.post(
            "/gifts",
            json={"name": "Scarf", "recipient_ids": [rid]},
            headers=headers
        )
        gift_id = create_response.json()["id"]

        # Clear recipients
        update_data = {"recipient_ids": []}
        response = client.patch(f"/gifts/{gift_id}", json=update_data, headers=headers)

        assert response.status_code == 200
        assert response.json()["recipient_ids"] == []

    def test_update_gift_replace_recipients(self, client, authenticated_user):
        user, headers = authenticated_user

        r1 = client.post("/recipients", json={"name": "Mom"}, headers=headers)
        r2 = client.post("/recipients", json={"name": "Dad"}, headers=headers)
        rid1 = r1.json()["id"]
        rid2 = r2.json()["id"]

        create_response = client.post(
            "/gifts",
            json={"name": "Scarf", "recipient_ids": [rid1]},
            headers=headers,
        )
        gift_id = create_response.json()["id"]

        # Replace recipient
        update_data = {"recipient_ids": [rid2]}
        response = client.patch(f"/gifts/{gift_id}", json=update_data, headers=headers)

        assert response.status_code == 200
        assert response.json()["recipient_ids"] == [rid2]

    def test_update_gift_with_invalid_recipient_returns_404(self, client, authenticated_user):
        user, headers = authenticated_user

        create_response = client.post("/gifts", json={"name": "Scarf"}, headers=headers)
        gift_id = create_response.json()["id"]

        update_data = {"recipient_ids": [str(uuid.uuid4())]}
        response = client.patch(f"/gifts/{gift_id}", json=update_data, headers=headers)

        assert response.status_code == 404

    def test_update_gift_with_other_user_recipient_returns_404(self, client, authenticated_user, other_user_with_recipients):
        user, headers = authenticated_user
        other_user, other_recipients = other_user_with_recipients

        create_response = client.post("/gifts", json={"name": "Scarf"}, headers=headers)
        gift_id = create_response.json()["id"]

        other_rid = other_recipients[0]["id"]
        update_data = {"recipient_ids": [other_rid]}
        response = client.patch(f"/gifts/{gift_id}", json=update_data, headers=headers)

        assert response.status_code == 404

    def test_update_gift_preserves_recipients_when_updating_other_fields(self, client, authenticated_user):
        user, headers = authenticated_user

        r = client.post("/recipients", json={"name": "Mom"}, headers=headers)
        rid = r.json()["id"]

        create_response = client.post(
            "/gifts",
            json={"name": "Scarf", "recipient_ids": [rid]},
            headers=headers,
        )
        gift_id = create_response.json()["id"]

        # Update name only — recipients should be preserved
        update_data = {"name": "Silk Scarf"}
        response = client.patch(f"/gifts/{gift_id}", json=update_data, headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Silk Scarf"
        assert data["recipient_ids"] == [rid]

    def test_update_gift_clear_url(self, client, authenticated_user):
        user, headers = authenticated_user

        create_response = client.post(
            "/gifts",
            json={"name": "Gift", "url": "https://example.com"},
            headers=headers
        )
        gift_id = create_response.json()["id"]

        update_data = {"url": None}
        response = client.patch(f"/gifts/{gift_id}", json=update_data, headers=headers)

        assert response.status_code == 200
        assert response.json()["url"] is None

    def test_update_gift_not_found_returns_404(self, client, authenticated_user):
        user, headers = authenticated_user

        non_existent_id = str(uuid.uuid4())
        update_data = {"name": "New Name"}
        response = client.patch(f"/gifts/{non_existent_id}", json=update_data, headers=headers)

        assert response.status_code == 404

    def test_update_gift_from_other_user_returns_404(self, client, authenticated_user, other_user_with_gifts):
        user, headers = authenticated_user
        other_user, other_gifts = other_user_with_gifts

        other_gift_id = other_gifts[0]["id"]
        update_data = {"name": "Hacked Name"}
        response = client.patch(f"/gifts/{other_gift_id}", json=update_data, headers=headers)

        assert response.status_code == 404

    def test_update_gift_empty_name_returns_422(self, client, authenticated_user):
        user, headers = authenticated_user

        create_response = client.post("/gifts", json={"name": "Gift"}, headers=headers)
        gift_id = create_response.json()["id"]

        update_data = {"name": "   "}
        response = client.patch(f"/gifts/{gift_id}", json=update_data, headers=headers)

        assert response.status_code == 422

    def test_update_gift_price_below_minimum_returns_422(self, client, authenticated_user):
        user, headers = authenticated_user

        create_response = client.post("/gifts", json={"name": "Gift", "price": 10.00}, headers=headers)
        gift_id = create_response.json()["id"]

        update_data = {"price": 0}
        response = client.patch(f"/gifts/{gift_id}", json=update_data, headers=headers)

        assert response.status_code == 422

    def test_update_gift_invalid_status_returns_422(self, client, authenticated_user):
        user, headers = authenticated_user

        create_response = client.post("/gifts", json={"name": "Gift"}, headers=headers)
        gift_id = create_response.json()["id"]

        update_data = {"status": "invalid"}
        response = client.patch(f"/gifts/{gift_id}", json=update_data, headers=headers)

        assert response.status_code == 422

    def test_update_gift_requires_authentication(self, client):
        gift_id = str(uuid.uuid4())
        update_data = {"name": "New Name"}
        response = client.patch(f"/gifts/{gift_id}", json=update_data)
        assert response.status_code == 401


class TestDeleteGiftEndpoint:

    def test_delete_gift_success(self, client, authenticated_user):
        user, headers = authenticated_user

        create_response = client.post("/gifts", json={"name": "To Delete"}, headers=headers)
        gift_id = create_response.json()["id"]

        response = client.delete(f"/gifts/{gift_id}", headers=headers)

        assert response.status_code == 204
        assert response.content == b""

        # Verify it's deleted
        get_response = client.get(f"/gifts/{gift_id}", headers=headers)
        assert get_response.status_code == 404

    def test_delete_gift_not_found_returns_404(self, client, authenticated_user):
        user, headers = authenticated_user

        non_existent_id = str(uuid.uuid4())
        response = client.delete(f"/gifts/{non_existent_id}", headers=headers)

        assert response.status_code == 404

    def test_delete_gift_from_other_user_returns_404(self, client, authenticated_user, other_user_with_gifts):
        user, headers = authenticated_user
        other_user, other_gifts = other_user_with_gifts

        other_gift_id = other_gifts[0]["id"]
        response = client.delete(f"/gifts/{other_gift_id}", headers=headers)

        assert response.status_code == 404

    def test_delete_gift_requires_authentication(self, client):
        gift_id = str(uuid.uuid4())
        response = client.delete(f"/gifts/{gift_id}")
        assert response.status_code == 401

    def test_delete_gift_idempotent(self, client, authenticated_user):
        user, headers = authenticated_user

        create_response = client.post("/gifts", json={"name": "To Delete"}, headers=headers)
        gift_id = create_response.json()["id"]

        # First delete
        response1 = client.delete(f"/gifts/{gift_id}", headers=headers)
        assert response1.status_code == 204

        # Second delete - should return 404
        response2 = client.delete(f"/gifts/{gift_id}", headers=headers)
        assert response2.status_code == 404
