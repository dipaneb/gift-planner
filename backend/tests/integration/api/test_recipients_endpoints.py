import pytest
import uuid
from fastapi.testclient import TestClient


class TestCreateRecipientEndpoint:
    
    def test_create_recipient_success_with_notes(self, client, authenticated_user):
        user, headers = authenticated_user
        
        recipient_data = {
            "name": "Michel (Brother)",
            "notes": "Likes books, plays chess and started photography."
        }
        
        response = client.post("/recipients", json=recipient_data, headers=headers)
        
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["name"] == "Michel (Brother)"
        assert data["notes"] == "Likes books, plays chess and started photography."
        assert data["user_id"] == str(user.id)
    
    def test_create_recipient_success_without_notes(self, client, authenticated_user):
        user, headers = authenticated_user
        
        recipient_data = {
            "name": "Alice (Friend)"
        }
        
        response = client.post("/recipients", json=recipient_data, headers=headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Alice (Friend)"
        assert data["notes"] is None
    
    def test_create_recipient_requires_authentication(self, client):
        recipient_data = {
            "name": "Test Recipient"
        }
        
        response = client.post("/recipients", json=recipient_data)
        assert response.status_code == 401
    
    def test_create_recipient_empty_name_returns_422(self, client, authenticated_user):
        user, headers = authenticated_user
        
        recipient_data = {
            "name": "   "  # Only whitespace
        }
        
        response = client.post("/recipients", json=recipient_data, headers=headers)
        assert response.status_code == 422
    
    def test_create_recipient_missing_name_returns_422(self, client, authenticated_user):
        user, headers = authenticated_user
        
        recipient_data = {
            "notes": "Some notes"
        }
        
        response = client.post("/recipients", json=recipient_data, headers=headers)
        assert response.status_code == 422
    
    def test_create_recipient_name_too_long_returns_422(self, client, authenticated_user):
        user, headers = authenticated_user
        
        recipient_data = {
            "name": "A" * 256  # Exceeds 255 char limit
        }
        
        response = client.post("/recipients", json=recipient_data, headers=headers)
        assert response.status_code == 422
    
    def test_create_recipient_normalizes_whitespace(self, client, authenticated_user):
        user, headers = authenticated_user
        
        recipient_data = {
            "name": "  Alice  ",
            "notes": "  Some notes  "
        }
        
        response = client.post("/recipients", json=recipient_data, headers=headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Alice"
        assert data["notes"] == "Some notes"


class TestGetRecipientsEndpoint:
    
    def test_get_recipients_empty_list(self, client, authenticated_user):
        user, headers = authenticated_user
        
        response = client.get("/recipients", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_get_recipients_returns_user_recipients_only(self, client, authenticated_user, other_user_with_recipients):
        user, headers = authenticated_user
        other_user, other_recipients = other_user_with_recipients
        
        # Create recipient for authenticated user
        recipient_data = {"name": "My Recipient"}
        create_response = client.post("/recipients", json=recipient_data, headers=headers)
        assert create_response.status_code == 201
        
        # Get recipients - should only see own
        response = client.get("/recipients", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "My Recipient"
        assert data[0]["user_id"] == str(user.id)
    
    def test_get_recipients_pagination_default(self, client, authenticated_user_with_recipients):
        user, headers, recipients = authenticated_user_with_recipients
        
        response = client.get("/recipients", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 10  # Default limit
    
    def test_get_recipients_pagination_custom_limit(self, client, authenticated_user_with_recipients):
        user, headers, recipients = authenticated_user_with_recipients
        
        response = client.get("/recipients?limit=2", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
    
    def test_get_recipients_pagination_page_2(self, client, authenticated_user_with_recipients):
        user, headers, recipients = authenticated_user_with_recipients
        
        response = client.get("/recipients?page=2&limit=2", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
    
    def test_get_recipients_sort_ascending(self, client, authenticated_user):
        user, headers = authenticated_user
        
        # Create recipients in specific order
        client.post("/recipients", json={"name": "Zara"}, headers=headers)
        client.post("/recipients", json={"name": "Alice"}, headers=headers)
        client.post("/recipients", json={"name": "Bob"}, headers=headers)
        
        response = client.get("/recipients?sort=asc", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert data[0]["name"] == "Alice"
        assert data[1]["name"] == "Bob"
        assert data[2]["name"] == "Zara"
    
    def test_get_recipients_sort_descending(self, client, authenticated_user):
        user, headers = authenticated_user
        
        # Create recipients in specific order
        client.post("/recipients", json={"name": "Zara"}, headers=headers)
        client.post("/recipients", json={"name": "Alice"}, headers=headers)
        client.post("/recipients", json={"name": "Bob"}, headers=headers)
        
        response = client.get("/recipients?sort=desc", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert data[0]["name"] == "Zara"
        assert data[1]["name"] == "Bob"
        assert data[2]["name"] == "Alice"
    
    def test_get_recipients_requires_authentication(self, client):
        response = client.get("/recipients")
        assert response.status_code == 401


class TestGetRecipientByIdEndpoint:
    
    def test_get_recipient_by_id_success(self, client, authenticated_user):
        user, headers = authenticated_user
        
        # Create recipient
        create_response = client.post(
            "/recipients",
            json={"name": "Test Recipient", "notes": "Some notes"},
            headers=headers
        )
        created = create_response.json()
        recipient_id = created["id"]
        
        # Get by ID
        response = client.get(f"/recipients/{recipient_id}", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == recipient_id
        assert data["name"] == "Test Recipient"
        assert data["notes"] == "Some notes"
    
    def test_get_recipient_not_found_returns_404(self, client, authenticated_user):
        user, headers = authenticated_user
        
        non_existent_id = str(uuid.uuid4())
        response = client.get(f"/recipients/{non_existent_id}", headers=headers)
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_get_recipient_from_other_user_returns_404(self, client, authenticated_user, other_user_with_recipients):
        user, headers = authenticated_user
        other_user, other_recipients = other_user_with_recipients
        
        # Try to access other user's recipient
        other_recipient_id = other_recipients[0]["id"]
        response = client.get(f"/recipients/{other_recipient_id}", headers=headers)
        
        assert response.status_code == 404
    
    def test_get_recipient_requires_authentication(self, client):
        recipient_id = str(uuid.uuid4())
        response = client.get(f"/recipients/{recipient_id}")
        assert response.status_code == 401


class TestUpdateRecipientEndpoint:
    
    def test_update_recipient_name_only(self, client, authenticated_user):
        user, headers = authenticated_user
        
        # Create recipient
        create_response = client.post(
            "/recipients",
            json={"name": "Original Name", "notes": "Original notes"},
            headers=headers
        )
        recipient_id = create_response.json()["id"]
        
        # Update name
        update_data = {"name": "Updated Name"}
        response = client.patch(f"/recipients/{recipient_id}", json=update_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["notes"] == "Original notes"  # Unchanged
    
    def test_update_recipient_notes_only(self, client, authenticated_user):
        user, headers = authenticated_user
        
        # Create recipient
        create_response = client.post(
            "/recipients",
            json={"name": "Name", "notes": "Original notes"},
            headers=headers
        )
        recipient_id = create_response.json()["id"]
        
        # Update notes
        update_data = {"notes": "Updated notes"}
        response = client.patch(f"/recipients/{recipient_id}", json=update_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Name"  # Unchanged
        assert data["notes"] == "Updated notes"
    
    def test_update_recipient_both_fields(self, client, authenticated_user):
        user, headers = authenticated_user
        
        # Create recipient
        create_response = client.post(
            "/recipients",
            json={"name": "Original", "notes": "Original"},
            headers=headers
        )
        recipient_id = create_response.json()["id"]
        
        # Update both
        update_data = {"name": "New Name", "notes": "New notes"}
        response = client.patch(f"/recipients/{recipient_id}", json=update_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "New Name"
        assert data["notes"] == "New notes"
    
    def test_update_recipient_clear_notes(self, client, authenticated_user):
        user, headers = authenticated_user
        
        # Create recipient with notes
        create_response = client.post(
            "/recipients",
            json={"name": "Name", "notes": "Some notes"},
            headers=headers
        )
        recipient_id = create_response.json()["id"]
        
        # Clear notes
        update_data = {"notes": None}
        response = client.patch(f"/recipients/{recipient_id}", json=update_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["notes"] is None
    
    def test_update_recipient_not_found_returns_404(self, client, authenticated_user):
        user, headers = authenticated_user
        
        non_existent_id = str(uuid.uuid4())
        update_data = {"name": "New Name"}
        response = client.patch(f"/recipients/{non_existent_id}", json=update_data, headers=headers)
        
        assert response.status_code == 404
    
    def test_update_recipient_from_other_user_returns_404(self, client, authenticated_user, other_user_with_recipients):
        user, headers = authenticated_user
        other_user, other_recipients = other_user_with_recipients
        
        # Try to update other user's recipient
        other_recipient_id = other_recipients[0]["id"]
        update_data = {"name": "Hacked Name"}
        response = client.patch(f"/recipients/{other_recipient_id}", json=update_data, headers=headers)
        
        assert response.status_code == 404
    
    def test_update_recipient_empty_name_returns_422(self, client, authenticated_user):
        user, headers = authenticated_user
        
        # Create recipient
        create_response = client.post("/recipients", json={"name": "Name"}, headers=headers)
        recipient_id = create_response.json()["id"]
        
        # Try to update with empty name
        update_data = {"name": "   "}
        response = client.patch(f"/recipients/{recipient_id}", json=update_data, headers=headers)
        
        assert response.status_code == 422
    
    def test_update_recipient_requires_authentication(self, client):
        recipient_id = str(uuid.uuid4())
        update_data = {"name": "New Name"}
        response = client.patch(f"/recipients/{recipient_id}", json=update_data)
        assert response.status_code == 401


class TestDeleteRecipientEndpoint:
    
    def test_delete_recipient_success(self, client, authenticated_user):
        user, headers = authenticated_user
        
        # Create recipient
        create_response = client.post("/recipients", json={"name": "To Delete"}, headers=headers)
        recipient_id = create_response.json()["id"]
        
        # Delete
        response = client.delete(f"/recipients/{recipient_id}", headers=headers)
        
        assert response.status_code == 204
        assert response.content == b""
        
        # Verify it's deleted
        get_response = client.get(f"/recipients/{recipient_id}", headers=headers)
        assert get_response.status_code == 404
    
    def test_delete_recipient_not_found_returns_404(self, client, authenticated_user):
        user, headers = authenticated_user
        
        non_existent_id = str(uuid.uuid4())
        response = client.delete(f"/recipients/{non_existent_id}", headers=headers)
        
        assert response.status_code == 404
    
    def test_delete_recipient_from_other_user_returns_404(self, client, authenticated_user, other_user_with_recipients):
        user, headers = authenticated_user
        other_user, other_recipients = other_user_with_recipients
        
        # Try to delete other user's recipient
        other_recipient_id = other_recipients[0]["id"]
        response = client.delete(f"/recipients/{other_recipient_id}", headers=headers)
        
        assert response.status_code == 404
        
        # Verify other user's recipient still exists (by creating auth for other user)
        # This is tested by the fixture, we just ensure we got 404
    
    def test_delete_recipient_requires_authentication(self, client):
        recipient_id = str(uuid.uuid4())
        response = client.delete(f"/recipients/{recipient_id}")
        assert response.status_code == 401
    
    def test_delete_recipient_idempotent(self, client, authenticated_user):
        user, headers = authenticated_user
        
        # Create recipient
        create_response = client.post("/recipients", json={"name": "To Delete"}, headers=headers)
        recipient_id = create_response.json()["id"]
        
        # First delete
        response1 = client.delete(f"/recipients/{recipient_id}", headers=headers)
        assert response1.status_code == 204
        
        # Second delete - should return 404
        response2 = client.delete(f"/recipients/{recipient_id}", headers=headers)
        assert response2.status_code == 404
