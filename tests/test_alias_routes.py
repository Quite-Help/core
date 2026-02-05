import pytest
from unittest.mock import patch

from app.routes.alias import create_or_get_alias
from app.models.alias import AliasRequest
from app.schema.alias import Alias


class TestCreateOrGetAlias:
    """Test the /aliases endpoint."""

    @pytest.mark.asyncio
    async def test_create_or_get_alias_returns_existing_alias(self, mock_db_session):
        """Test that endpoint returns existing alias when found."""
        existing_alias = Alias(telegram_user_id="12345", alias="existing-alias")

        with patch("app.routes.alias.alias_repo.get_by_telegram_user_id") as mock_get:
            mock_get.return_value = existing_alias

            payload = AliasRequest(telegram_user_id="12345")

            result = await create_or_get_alias(payload, mock_db_session, _={})

            assert result.alias == existing_alias.alias
            mock_get.assert_called_once_with(mock_db_session, "12345")

    @pytest.mark.asyncio
    async def test_create_or_get_alias_creates_new_alias(self, mock_db_session):
        """Test that endpoint creates new alias when none exists."""
        # Mock the repository call to return empty list (no existing alias)
        with (
            patch("app.routes.alias.alias_repo.get_by_telegram_user_id") as mock_get,
            patch("app.routes.alias.alias_repo.create_user_alias") as mock_create,
            patch("app.routes.alias.generate_alias") as mock_generate,
        ):
            mock_get.return_value = None
            mock_generate.return_value = "new-generated-alias"

            payload = AliasRequest(telegram_user_id="12345")

            response = await create_or_get_alias(payload, mock_db_session, _={})

            assert response.alias == "new-generated-alias"
            mock_get.assert_called_once_with(mock_db_session, "12345")
            mock_generate.assert_called_once()
            assert mock_create.called
            assert mock_create.call_args[0] == (
                mock_db_session,
                "12345",
                "new-generated-alias",
            )

    @pytest.mark.asyncio
    async def test_create_or_get_alias_generates_unique_alias(self, mock_db_session):
        """Test that endpoint generates a new alias using helper function."""
        with (
            patch("app.routes.alias.alias_repo.get_by_telegram_user_id") as mock_get,
            patch("app.routes.alias.alias_repo.create_user_alias"),
            patch("app.routes.alias.generate_alias") as mock_generate,
        ):
            mock_get.return_value = None
            mock_generate.return_value = "unique-alias-xyz"

            payload = AliasRequest(telegram_user_id="67890")

            response = await create_or_get_alias(payload, mock_db_session, _={})

            mock_generate.assert_called_once()
            assert response.alias == "unique-alias-xyz"
