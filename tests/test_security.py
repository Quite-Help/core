import pytest
from fastapi import HTTPException
from unittest.mock import MagicMock
from jose import jwt
from datetime import datetime, timedelta, timezone

from app.core.security import hash_password, verify_password, check_auth
from app.core.config import settings
from app.schema.account import Role


class TestPasswordHashing:
    """Test password hashing and verification functions."""

    def test_hash_password_returns_string(self):
        """Test that hash_password returns a string."""
        password = "test_password_123"
        hashed = hash_password(password)
        assert isinstance(hashed, str)
        assert len(hashed) > 0

    def test_hash_password_produces_different_hashes(self):
        """Test that the same password produces different hashes (salt)."""
        password = "test_password_123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        assert hash1 != hash2

    def test_verify_password_correct_password(self):
        """Test that verify_password returns True for correct password."""
        password = "test_password_123"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect_password(self):
        """Test that verify_password raises exception for incorrect password."""
        from argon2.exceptions import VerifyMismatchError

        password = "test_password_123"
        wrong_password = "wrong_password"
        hashed = hash_password(password)
        with pytest.raises(VerifyMismatchError):
            verify_password(wrong_password, hashed)

    def test_verify_password_raises_on_invalid_hash(self):
        """Test that verify_password raises exception for invalid hash."""
        with pytest.raises(Exception):
            verify_password("password", "invalid_hash_format")


class TestCheckAuth:
    """Test authentication check decorator."""

    def test_check_auth_valid_token_no_roles_required(self):
        """Test check_auth with valid token and no role requirements."""
        payload = {
            "sub": "1",
            "roles": [Role.ADMIN.value],
            "exp": datetime.now(timezone.utc) + timedelta(minutes=60),
        }
        token = jwt.encode(
            payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
        )

        security = MagicMock()
        security.credentials = token

        auth_func = check_auth([])
        result = auth_func(security)

        assert result is not None
        assert result["sub"] == "1"

    def test_check_auth_valid_token_with_required_role(self):
        """Test check_auth with valid token and required role present."""
        payload = {
            "sub": "1",
            "roles": [Role.ADMIN.value, Role.SUPER_ADMIN.value],
            "exp": datetime.now(timezone.utc) + timedelta(minutes=60),
        }
        token = jwt.encode(
            payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
        )

        security = MagicMock()
        security.credentials = token

        auth_func = check_auth([Role.ADMIN])
        result = auth_func(security)

        assert result is not None
        assert result["sub"] == "1"

    def test_check_auth_valid_token_missing_required_role(self):
        """Test check_auth with valid token but missing required role."""
        payload = {
            "sub": "1",
            "roles": [Role.ADMIN.value],
            "exp": datetime.now(timezone.utc) + timedelta(minutes=60),
        }
        token = jwt.encode(
            payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
        )

        security = MagicMock()
        security.credentials = token

        auth_func = check_auth([Role.SUPER_ADMIN])

        with pytest.raises(HTTPException) as exc_info:
            auth_func(security)

        assert exc_info.value.status_code == 403
        assert "Insufficient role" in exc_info.value.detail

    def test_check_auth_invalid_token(self):
        """Test check_auth with invalid token."""
        security = MagicMock()
        security.credentials = "invalid.token.here"

        auth_func = check_auth([])

        with pytest.raises(HTTPException) as exc_info:
            auth_func(security)

        assert exc_info.value.status_code == 401
        assert "Invalid token" in exc_info.value.detail

    def test_check_auth_expired_token(self):
        """Test check_auth with expired token."""
        payload = {
            "sub": "1",
            "roles": [Role.ADMIN.value],
            "exp": datetime.now(timezone.utc) - timedelta(minutes=60),
        }
        token = jwt.encode(
            payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
        )

        security = MagicMock()
        security.credentials = token

        auth_func = check_auth([])

        with pytest.raises(HTTPException) as exc_info:
            auth_func(security)

        assert exc_info.value.status_code == 401

    def test_check_auth_multiple_required_roles(self):
        """Test check_auth with multiple required roles."""
        payload = {
            "sub": "1",
            "roles": [Role.ADMIN.value, Role.SUPER_ADMIN.value, Role.SERVICE.value],
            "exp": datetime.now(timezone.utc) + timedelta(minutes=60),
        }
        token = jwt.encode(
            payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
        )

        security = MagicMock()
        security.credentials = token

        auth_func = check_auth([Role.ADMIN, Role.SUPER_ADMIN])
        result = auth_func(security)

        assert result is not None

    def test_check_auth_no_roles_in_token(self):
        """Test check_auth with token that has no roles."""
        payload = {
            "sub": "1",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=60),
        }
        token = jwt.encode(
            payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
        )

        security = MagicMock()
        security.credentials = token

        auth_func = check_auth([Role.ADMIN])

        with pytest.raises(HTTPException) as exc_info:
            auth_func(security)

        assert exc_info.value.status_code == 403
