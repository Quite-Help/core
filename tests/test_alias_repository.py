import pytest
from unittest.mock import MagicMock

from app.repositories import alias_repo
from app.schema.alias import Alias


class TestAliasRepository:
    """Test alias repository functions."""

    @pytest.mark.asyncio
    async def test_get_by_telegram_user_id_found(self, mock_db_session):
        """Test getting alias by telegram user ID when found."""
        alias = Alias(telegram_user_id="12345", alias="test-alias")

        mock_result = MagicMock()
        mock_result.one_or_none.return_value = alias
        mock_db_session.scalars.return_value = mock_result

        result = await alias_repo.get_by_telegram_user_id(mock_db_session, "12345")

        # Repository returns result.first() which Alias type
        assert isinstance(result, Alias)
        assert result.telegram_user_id == "12345"
        assert result.alias == "test-alias"
        mock_db_session.scalars.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_telegram_user_id_not_found(self, mock_db_session):
        """Test getting alias by telegram user ID when not found."""
        mock_result = MagicMock()
        mock_result.one_or_none.return_value = None
        mock_db_session.scalars.return_value = mock_result

        result = await alias_repo.get_by_telegram_user_id(
            mock_db_session, "nonexistent"
        )

        assert result is None
        mock_db_session.scalars.assert_called_once()

    def test_create_user_alias(self, mock_db_session):
        """Test creating a new user alias."""
        alias_repo.create_user_alias(mock_db_session, "12345", "new-alias")

        # Verify that db.add was called
        assert mock_db_session.add.called

        # Get the alias that was added
        call_args = mock_db_session.add.call_args[0][0]
        assert isinstance(call_args, Alias)
        assert call_args.telegram_user_id == "12345"
        assert call_args.alias == "new-alias"

    def test_create_user_alias_different_values(self, mock_db_session):
        """Test creating aliases with different values."""
        alias_repo.create_user_alias(mock_db_session, "user1", "alias1")
        alias_repo.create_user_alias(mock_db_session, "user2", "alias2")

        assert mock_db_session.add.call_count == 2

        # Check first call
        first_alias = mock_db_session.add.call_args_list[0][0][0]
        assert first_alias.telegram_user_id == "user1"
        assert first_alias.alias == "alias1"

        # Check second call
        second_alias = mock_db_session.add.call_args_list[1][0][0]
        assert second_alias.telegram_user_id == "user2"
        assert second_alias.alias == "alias2"
