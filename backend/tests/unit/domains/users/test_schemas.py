import pytest
import uuid
from decimal import Decimal
from pydantic import ValidationError

from src.domains.users.schemas import BudgetUpdate, UserRead


class TestUserReadSchema:
    
    def test_user_read_valid(self):
        user_id = uuid.uuid4()
        user_data = UserRead(
            id=user_id,
            email="test@example.com",
            name="Test User",
            budget=None,
            spent=Decimal("0.00"),
            remaining=None
        )
        
        assert user_data.id == user_id
        assert user_data.email == "test@example.com"
        assert user_data.name == "Test User"
        assert user_data.budget is None
        assert user_data.spent == Decimal("0.00")
        assert user_data.remaining is None
    
    def test_user_read_with_budget(self):
        user_id = uuid.uuid4()
        user_data = UserRead(
            id=user_id,
            email="test@example.com",
            name="Test User",
            budget=Decimal("150.00"),
            spent=Decimal("50.00"),
            remaining=Decimal("100.00")
        )
        
        assert user_data.budget == Decimal("150.00")
        assert user_data.spent == Decimal("50.00")
        assert user_data.remaining == Decimal("100.00")
    
    def test_user_read_without_name(self):
        user_id = uuid.uuid4()
        user_data = UserRead(
            id=user_id,
            email="test@example.com",
            name=None,
            budget=None,
            spent=Decimal("0.00"),
            remaining=None
        )
        
        assert user_data.id == user_id
        assert user_data.email == "test@example.com"
        assert user_data.name is None
    
    def test_user_read_invalid_email(self):
        user_id = uuid.uuid4()
        
        with pytest.raises(ValidationError) as exc_info:
            UserRead(
                id=user_id,
                email="invalid-email",
                name="Test"
            )
        
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("email",) for e in errors)
    
    def test_user_read_missing_id(self):
        with pytest.raises(ValidationError) as exc_info:
            UserRead(
                email="test@example.com",
                name="Test"
            )
        
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("id",) for e in errors)
    
    def test_user_read_missing_email(self):
        with pytest.raises(ValidationError) as exc_info:
            UserRead(
                id=uuid.uuid4(),
                name="Test"
            )
        
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("email",) for e in errors)
    
    def test_user_read_serialization(self):
        user_id = uuid.uuid4()
        user_data = UserRead(
            id=user_id,
            email="test@example.com",
            name="Test User",
            budget=Decimal("100.00"),
            spent=Decimal("30.00"),
            remaining=Decimal("70.00")
        )
        
        serialized = user_data.model_dump()
        
        assert serialized["id"] == user_id
        assert serialized["email"] == "test@example.com"
        assert serialized["name"] == "Test User"
        assert serialized["budget"] == Decimal("100.00")
        assert serialized["spent"] == Decimal("30.00")
        assert serialized["remaining"] == Decimal("70.00")


class TestBudgetUpdateSchema:

    def test_valid_budget(self):
        data = {"budget": 150.00}
        schema = BudgetUpdate(**data)
        assert schema.budget == Decimal("150.00")

    def test_valid_budget_decimal(self):
        data = {"budget": 0.01}
        schema = BudgetUpdate(**data)
        assert schema.budget == Decimal("0.01")

    def test_budget_zero_raises_validation_error(self):
        with pytest.raises(ValidationError) as exc_info:
            BudgetUpdate(budget=0)
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("budget",) for e in errors)

    def test_budget_negative_raises_validation_error(self):
        with pytest.raises(ValidationError) as exc_info:
            BudgetUpdate(budget=-10.00)
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("budget",) for e in errors)

    def test_budget_missing_raises_validation_error(self):
        with pytest.raises(ValidationError) as exc_info:
            BudgetUpdate()
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("budget",) for e in errors)

    def test_budget_large_value(self):
        data = {"budget": 99999999.99}
        schema = BudgetUpdate(**data)
        assert schema.budget == Decimal("99999999.99")
