import os

import pytest


_env_vars = {
    "DATABASE_URL": "postgresql+asyncpg://mock_user:mock_password@mockserver:5432/mockdb",
    "JWT_SECRET": "mock_secret",
    "JWT_ALGORITHM": "HS256",
}

for key, value in _env_vars.items():
    os.environ.setdefault(key, value)


def pytest_configure():
    """Configure pytest - set environment variables before test collection."""
    # Ensure all required environment variables are set
    for key, value in _env_vars.items():
        os.environ[key] = value


@pytest.fixture(scope="session", autouse=True)
def setup_env_vars():
    """Set up environment variables for all tests (session-scoped, autouse)."""
    for key, value in _env_vars.items():
        os.environ[key] = value
    yield
    # Cleanup is optional - we don't need to remove them
