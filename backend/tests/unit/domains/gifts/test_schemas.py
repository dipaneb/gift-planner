import pytest
import uuid
from decimal import Decimal
from pydantic import ValidationError

from src.domains.gifts.schemas import GiftCreate, GiftUpdate, GiftResponse
from src.domains.gifts.enums import GiftStatusEnum


class TestGiftCreate:

    def test_valid_gift_minimal(self):
        data = {
            "name": "Chess set",
        }

        gift = GiftCreate(**data)

        assert gift.name == "Chess set"
        assert gift.url is None
        assert gift.price is None
        assert gift.status == GiftStatusEnum.idee
        assert gift.quantity == 1
        assert gift.recipient_ids == []

    def test_valid_gift_with_all_fields(self):
        rid = uuid.uuid4()
        data = {
            "name": "Canon EOS R50",
            "url": "https://www.amazon.fr/dp/B0BVNQ3Q3W",
            "price": 799.99,
            "status": "achete",
            "quantity": 2,
            "recipient_ids": [str(rid)],
        }

        gift = GiftCreate(**data)

        assert gift.name == "Canon EOS R50"
        assert gift.url == "https://www.amazon.fr/dp/B0BVNQ3Q3W"
        assert gift.price == Decimal("799.99")
        assert gift.status == GiftStatusEnum.achete
        assert gift.quantity == 2
        assert gift.recipient_ids == [rid]

    def test_missing_name_raises_validation_error(self):
        data = {
            "price": 10.00,
        }

        with pytest.raises(ValidationError) as exc_info:
            GiftCreate(**data)

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("name",) for error in errors)

    def test_name_normalization_strips_whitespace(self):
        data = {
            "name": "  Chess set  ",
        }

        gift = GiftCreate(**data)

        assert gift.name == "Chess set"

    def test_empty_name_after_strip_raises_validation_error(self):
        data = {
            "name": "   ",
        }

        with pytest.raises(ValidationError) as exc_info:
            GiftCreate(**data)

        errors = exc_info.value.errors()
        assert any("empty" in str(error["msg"]).lower() for error in errors)

    def test_name_too_long_raises_validation_error(self):
        data = {
            "name": "A" * 256,
        }

        with pytest.raises(ValidationError) as exc_info:
            GiftCreate(**data)

        errors = exc_info.value.errors()
        assert any(error["type"] == "string_too_long" for error in errors)

    def test_name_max_length_is_valid(self):
        data = {
            "name": "A" * 255,
        }

        gift = GiftCreate(**data)

        assert len(gift.name) == 255

    def test_url_normalization_strips_whitespace(self):
        data = {
            "name": "Gift",
            "url": "  https://example.com  ",
        }

        gift = GiftCreate(**data)

        assert gift.url == "https://example.com"

    def test_url_empty_after_strip_becomes_none(self):
        data = {
            "name": "Gift",
            "url": "   ",
        }

        gift = GiftCreate(**data)

        assert gift.url is None

    def test_url_too_long_raises_validation_error(self):
        data = {
            "name": "Gift",
            "url": "https://" + "a" * 248,
        }

        with pytest.raises(ValidationError) as exc_info:
            GiftCreate(**data)

        errors = exc_info.value.errors()
        assert any(error["type"] == "string_too_long" for error in errors)

    def test_price_below_minimum_raises_validation_error(self):
        data = {
            "name": "Gift",
            "price": 0,
        }

        with pytest.raises(ValidationError) as exc_info:
            GiftCreate(**data)

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("price",) for error in errors)

    def test_price_at_minimum_is_valid(self):
        data = {
            "name": "Gift",
            "price": 0.01,
        }

        gift = GiftCreate(**data)

        assert gift.price == Decimal("0.01")

    def test_quantity_below_minimum_raises_validation_error(self):
        data = {
            "name": "Gift",
            "quantity": 0,
        }

        with pytest.raises(ValidationError) as exc_info:
            GiftCreate(**data)

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("quantity",) for error in errors)

    def test_quantity_at_minimum_is_valid(self):
        data = {
            "name": "Gift",
            "quantity": 1,
        }

        gift = GiftCreate(**data)

        assert gift.quantity == 1

    def test_invalid_status_raises_validation_error(self):
        data = {
            "name": "Gift",
            "status": "invalid_status",
        }

        with pytest.raises(ValidationError) as exc_info:
            GiftCreate(**data)

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("status",) for error in errors)

    def test_all_valid_statuses(self):
        for status_val in GiftStatusEnum:
            data = {
                "name": "Gift",
                "status": status_val.value,
            }

            gift = GiftCreate(**data)

            assert gift.status == status_val


class TestGiftUpdate:

    def test_update_name_only(self):
        data = {
            "name": "Updated Name",
        }

        update = GiftUpdate(**data)

        assert update.name == "Updated Name"
        assert update.url is None
        assert update.price is None
        assert update.status is None
        assert update.quantity is None
        assert update.recipient_ids is None

    def test_update_status_only(self):
        data = {
            "status": "achete",
        }

        update = GiftUpdate(**data)

        assert update.status == GiftStatusEnum.achete

    def test_update_multiple_fields(self):
        data = {
            "name": "Updated",
            "price": 49.99,
            "status": "commande",
            "quantity": 3,
        }

        update = GiftUpdate(**data)

        assert update.name == "Updated"
        assert update.price == Decimal("49.99")
        assert update.status == GiftStatusEnum.commande
        assert update.quantity == 3

    def test_update_with_no_fields(self):
        data = {}

        update = GiftUpdate(**data)

        assert update.name is None
        assert update.url is None
        assert update.price is None
        assert update.status is None
        assert update.quantity is None
        assert update.recipient_ids is None

    def test_update_name_normalization(self):
        data = {
            "name": "  Updated Name  ",
        }

        update = GiftUpdate(**data)

        assert update.name == "Updated Name"

    def test_update_empty_name_after_strip_raises_validation_error(self):
        data = {
            "name": "   ",
        }

        with pytest.raises(ValidationError) as exc_info:
            GiftUpdate(**data)

        errors = exc_info.value.errors()
        assert any("empty" in str(error["msg"]).lower() for error in errors)

    def test_update_name_too_long_raises_validation_error(self):
        data = {
            "name": "A" * 256,
        }

        with pytest.raises(ValidationError) as exc_info:
            GiftUpdate(**data)

        errors = exc_info.value.errors()
        assert any(error["type"] == "string_too_long" for error in errors)

    def test_update_price_below_minimum_raises_validation_error(self):
        data = {
            "price": 0,
        }

        with pytest.raises(ValidationError) as exc_info:
            GiftUpdate(**data)

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("price",) for error in errors)

    def test_update_quantity_below_minimum_raises_validation_error(self):
        data = {
            "quantity": 0,
        }

        with pytest.raises(ValidationError) as exc_info:
            GiftUpdate(**data)

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("quantity",) for error in errors)

    def test_update_invalid_status_raises_validation_error(self):
        data = {
            "status": "invalid",
        }

        with pytest.raises(ValidationError) as exc_info:
            GiftUpdate(**data)

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("status",) for error in errors)

    def test_update_recipient_ids(self):
        rid = uuid.uuid4()
        data = {
            "recipient_ids": [str(rid)],
        }

        update = GiftUpdate(**data)

        assert update.recipient_ids == [rid]

    def test_update_clear_recipient_ids(self):
        data = {
            "recipient_ids": [],
        }

        update = GiftUpdate(**data)

        assert update.recipient_ids == []

    def test_model_dump_exclude_unset(self):
        """Test that only provided fields are included in model_dump(exclude_unset=True)"""
        data = {
            "name": "Updated Name",
        }

        update = GiftUpdate(**data)
        dump = update.model_dump(exclude_unset=True)

        assert "name" in dump
        assert "url" not in dump
        assert "price" not in dump
        assert "status" not in dump
        assert "quantity" not in dump
        assert "recipient_ids" not in dump


class TestGiftResponse:

    def test_valid_response(self):
        data = {
            "id": str(uuid.uuid4()),
            "user_id": str(uuid.uuid4()),
            "name": "Test Gift",
            "url": "https://example.com",
            "price": 29.99,
            "status": "idee",
            "quantity": 1,
            "recipient_ids": [],
        }

        response = GiftResponse(**data)

        assert isinstance(response.id, uuid.UUID)
        assert isinstance(response.user_id, uuid.UUID)
        assert response.name == "Test Gift"
        assert response.url == "https://example.com"
        assert response.price == Decimal("29.99")
        assert response.status == GiftStatusEnum.idee
        assert response.quantity == 1
        assert response.recipient_ids == []

    def test_response_with_null_optional_fields(self):
        data = {
            "id": str(uuid.uuid4()),
            "user_id": str(uuid.uuid4()),
            "name": "Test Gift",
            "url": None,
            "price": None,
            "status": "idee",
            "quantity": 1,
            "recipient_ids": [],
        }

        response = GiftResponse(**data)

        assert response.url is None
        assert response.price is None

    def test_response_with_recipient_ids(self):
        rid1 = uuid.uuid4()
        rid2 = uuid.uuid4()
        data = {
            "id": str(uuid.uuid4()),
            "user_id": str(uuid.uuid4()),
            "name": "Test Gift",
            "url": None,
            "price": None,
            "status": "idee",
            "quantity": 1,
            "recipient_ids": [str(rid1), str(rid2)],
        }

        response = GiftResponse(**data)

        assert response.recipient_ids == [rid1, rid2]

    def test_missing_required_fields_raises_validation_error(self):
        data = {
            "id": str(uuid.uuid4()),
        }

        with pytest.raises(ValidationError) as exc_info:
            GiftResponse(**data)

        errors = exc_info.value.errors()
        field_names = [error["loc"][0] for error in errors]
        assert "user_id" in field_names
        assert "name" in field_names
        assert "status" in field_names
        assert "quantity" in field_names

    def test_invalid_uuid_raises_validation_error(self):
        data = {
            "id": "not-a-uuid",
            "user_id": str(uuid.uuid4()),
            "name": "Test",
            "url": None,
            "price": None,
            "status": "idee",
            "quantity": 1,
        }

        with pytest.raises(ValidationError) as exc_info:
            GiftResponse(**data)

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("id",) for error in errors)

    def test_response_serialization(self):
        """Test that response can be serialized to dict"""
        gift_id = uuid.uuid4()
        user_id = uuid.uuid4()

        data = {
            "id": str(gift_id),
            "user_id": str(user_id),
            "name": "Test Gift",
            "url": "https://example.com",
            "price": 29.99,
            "status": "achete",
            "quantity": 2,
            "recipient_ids": [],
        }

        response = GiftResponse(**data)
        serialized = response.model_dump()

        assert serialized["id"] == gift_id
        assert serialized["user_id"] == user_id
        assert serialized["name"] == "Test Gift"
        assert serialized["status"] == GiftStatusEnum.achete
        assert serialized["quantity"] == 2
