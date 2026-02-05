import tests.env_set_test  # noqa: F401
import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt
from datetime import datetime, timedelta, timezone

from app.core.config import settings
from app.schema.account import Account, Role


@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    session = AsyncMock(spec=AsyncSession)
    session.scalars = AsyncMock()
    session.execute = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    return session


@pytest.fixture
def sample_account():
    """Create a sample account for testing."""
    account = Account(
        id=1, username="testuser", password="hashed_password", display_name="Test User"
    )
    account.add_role(Role.ADMIN)
    return account


@pytest.fixture
def admin_account():
    """Create an admin account for testing."""
    account = Account(
        id=2, username="admin", password="hashed_password", display_name="Admin User"
    )
    account.add_role(Role.ADMIN)
    account.add_role(Role.SUPER_ADMIN)
    return account


@pytest.fixture
def valid_jwt_token():
    """Create a valid JWT token for testing."""
    payload = {
        "sub": "1",
        "roles": [Role.ADMIN.value],
        "exp": datetime.now(timezone.utc) + timedelta(minutes=60),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


@pytest.fixture
def invalid_jwt_token():
    """Create an invalid JWT token for testing."""
    return "invalid.token.here"
