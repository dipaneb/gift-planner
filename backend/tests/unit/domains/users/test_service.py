import uuid
from decimal import Decimal
from unittest.mock import Mock

from src.domains.users.service import UserService
from src.domains.users.models import User


def _make_user(user_id=None, email="test@example.com", budget=None):
    """Helper to build a User with sensible defaults."""
    user = User(
        id=user_id or uuid.uuid4(),
        email=email,
        password_hash="hashed",
        name="Test User",
    )
    user.budget = budget
    return user


class TestUserServiceUpdateBudget:

    def test_update_budget_success(self):
        mock_repo = Mock()
        service = UserService(mock_repo)

        user_id = uuid.uuid4()
        expected_user = _make_user(user_id=user_id, budget=Decimal("200.00"))
        mock_repo.set_budget.return_value = expected_user

        result = service.update_budget(user_id, Decimal("200.00"))

        assert result.budget == Decimal("200.00")
        mock_repo.set_budget.assert_called_once_with(user_id, Decimal("200.00"))

    def test_update_budget_replaces_existing(self):
        mock_repo = Mock()
        service = UserService(mock_repo)

        user_id = uuid.uuid4()
        expected_user = _make_user(user_id=user_id, budget=Decimal("300.00"))
        mock_repo.set_budget.return_value = expected_user

        result = service.update_budget(user_id, Decimal("300.00"))

        assert result.budget == Decimal("300.00")
        mock_repo.set_budget.assert_called_once_with(user_id, Decimal("300.00"))


class TestUserServiceDeleteBudget:

    def test_delete_budget_success(self):
        mock_repo = Mock()
        service = UserService(mock_repo)

        user_id = uuid.uuid4()
        expected_user = _make_user(user_id=user_id, budget=None)
        mock_repo.set_budget.return_value = expected_user

        result = service.delete_budget(user_id)

        assert result.budget is None
        mock_repo.set_budget.assert_called_once_with(user_id, None)
