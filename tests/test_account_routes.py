import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException
from jose import jwt

from app.core.config import settings
from app.routes.account import (
    get_token,
    bootstrap_core_api_with_an_account_with_all_roles,
)
from app.models.account import LoginRequest
from app.core.security import hash_password
from app.schema.account import Account, Role


class TestGetToken:
    """Test the /account/token endpoint."""

    @pytest.mark.asyncio
    async def test_get_token_success(self, mock_db_session):
        """Test successful token generation with valid credentials."""
        password = "test_password"
        hashed = hash_password(password)
        account = Account(
            id=1, username="testuser", password=hashed, display_name="Test User"
        )
        account.add_role(Role.ADMIN)

        # Mock the database query
        mock_result = MagicMock()
        mock_result.first.return_value = account
        mock_db_session.scalars.return_value = mock_result

        login_request = LoginRequest(username="testuser", password=password)

        response = await get_token(login_request, mock_db_session)

        assert response.access_token is not None
        assert isinstance(response.access_token, str)

        # Verify token can be decoded with actual settings
        decoded = jwt.decode(
            response.access_token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
        assert decoded["sub"] == "1"
        # Roles are stored as strings in JWT
        assert "admin" in decoded.get("roles", [])

    @pytest.mark.asyncio
    async def test_get_token_invalid_username(self, mock_db_session):
        """Test token generation with invalid username."""
        mock_result = MagicMock()
        mock_result.first.return_value = None
        mock_db_session.scalars.return_value = mock_result

        login_request = LoginRequest(username="nonexistent", password="password")

        with pytest.raises(HTTPException) as exc_info:
            await get_token(login_request, mock_db_session)

        assert exc_info.value.status_code == 401
        assert "Invalid credentials" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_token_invalid_password(self, mock_db_session):
        """Test token generation with invalid password."""
        password = "correct_password"
        hashed = hash_password(password)
        account = Account(
            id=1, username="testuser", password=hashed, display_name="Test User"
        )

        mock_result = MagicMock()
        mock_result.first.return_value = account
        mock_db_session.scalars.return_value = mock_result

        login_request = LoginRequest(username="testuser", password="wrong_password")

        with pytest.raises(HTTPException) as exc_info:
            await get_token(login_request, mock_db_session)

        assert exc_info.value.status_code == 401
        assert "Invalid credentials" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_token_includes_roles_in_token(self, mock_db_session):
        """Test that token includes account roles."""
        password = "test_password"
        hashed = hash_password(password)
        account = Account(
            id=1, username="testuser", password=hashed, display_name="Test User"
        )
        account.add_role(Role.ADMIN)
        account.add_role(Role.SUPER_ADMIN)

        mock_result = MagicMock()
        mock_result.first.return_value = account
        mock_db_session.scalars.return_value = mock_result

        login_request = LoginRequest(username="testuser", password=password)

        response = await get_token(login_request, mock_db_session)

        # Verify token contains roles
        assert response.access_token is not None
        decoded = jwt.decode(
            response.access_token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
        # Roles are stored as strings in JWT
        assert "admin" in decoded.get("roles", [])
        assert "super_admin" in decoded.get("roles", [])


class TestBootstrapAccount:
    """Test the /account/tmp/bootstrap endpoint."""

    @pytest.mark.asyncio
    async def test_bootstrap_creates_admin_account_when_none_exists(
        self, mock_db_session
    ):
        """Test that bootstrap creates admin account when it doesn't exist."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        await bootstrap_core_api_with_an_account_with_all_roles(mock_db_session)

        # Verify that db.add was called
        assert mock_db_session.add.called
        # Note: The bootstrap function doesn't call commit (it's handled by get_db dependency)
        # So we just verify that add was called

    @pytest.mark.asyncio
    async def test_bootstrap_does_not_create_when_admin_exists(self, mock_db_session):
        """Test that bootstrap does not create account when admin already exists."""
        existing_admin = Account(
            id=1, username="admin", password="hashed", display_name="Admin"
        )

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = existing_admin
        mock_db_session.execute.return_value = mock_result

        await bootstrap_core_api_with_an_account_with_all_roles(mock_db_session)

        # Verify that db.add was NOT called
        mock_db_session.add.assert_not_called()

    @pytest.mark.asyncio
    async def test_bootstrap_account_has_all_roles(self, mock_db_session):
        """Test that bootstrap creates account with all required roles."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        await bootstrap_core_api_with_an_account_with_all_roles(mock_db_session)

        # Get the account that was added
        call_args = mock_db_session.add.call_args[0][0]
        assert isinstance(call_args, Account)
        assert call_args.username == "admin"
        assert call_args.display_name == "Admin"
        assert Role.ADMIN in call_args.roles
        assert Role.SUPER_ADMIN in call_args.roles
        assert Role.SERVICE in call_args.roles
