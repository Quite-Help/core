import pytest
from unittest.mock import MagicMock

from app.repositories import group_repo
from app.models.group import CreateGroupRequest, GroupLinkRequest
from app.schema.group import Group
from app.schema.alias import Alias


class TestGroupRepository:
    """Test group repository functions."""

    def test_create_group(self, mock_db_session):
        """Test creating a new group."""
        payload = CreateGroupRequest(
            user_alias="test-alias",
            user_group_link="https://t.me/test",
            user_group_id=12345,
            counselor_id=1,
            counselor_group_id=67890,
        )

        group_repo.create_group(mock_db_session, payload)

        # Verify that db.add was called
        assert mock_db_session.add.called

        # Get the group that was added
        call_args = mock_db_session.add.call_args[0][0]
        assert isinstance(call_args, Group)
        assert call_args.user_alias == "test-alias"
        assert call_args.counselor_id == 1
        assert call_args.user_group_id == 12345
        assert call_args.counselor_group_id == 67890
        assert call_args.user_group_link == "https://t.me/test"
        assert call_args.active is True

    def test_create_group_different_values(self, mock_db_session):
        """Test creating groups with different values."""
        payload1 = CreateGroupRequest(
            user_alias="alias1",
            user_group_link="https://t.me/group1",
            user_group_id=111,
            counselor_id=1,
            counselor_group_id=222,
        )
        payload2 = CreateGroupRequest(
            user_alias="alias2",
            user_group_link="https://t.me/group2",
            user_group_id=333,
            counselor_id=2,
            counselor_group_id=444,
        )

        group_repo.create_group(mock_db_session, payload1)
        group_repo.create_group(mock_db_session, payload2)

        assert mock_db_session.add.call_count == 2

        # Check first group
        first_group = mock_db_session.add.call_args_list[0][0][0]
        assert first_group.user_alias == "alias1"
        assert first_group.counselor_id == 1

        # Check second group
        second_group = mock_db_session.add.call_args_list[1][0][0]
        assert second_group.user_alias == "alias2"
        assert second_group.counselor_id == 2

    @pytest.mark.asyncio
    async def test_get_group_by_counselor_and_user_id_found(self, mock_db_session):
        """Test getting group by counselor and user ID when found."""
        alias = Alias(telegram_user_id="12345", alias="test-alias")
        group = Group(
            id=1,
            user_alias="test-alias",
            counselor_id=1,
            user_group_id=111,
            counselor_group_id=222,
            active=True,
        )

        # Mock the alias query
        mock_alias_result = MagicMock()
        mock_alias_result.one_or_none.return_value = alias
        mock_db_session.scalars.return_value = mock_alias_result

        # Mock the group query
        mock_group_result = MagicMock()
        mock_group_result.scalar_one_or_none.return_value = group
        mock_db_session.execute.return_value = mock_group_result

        payload = GroupLinkRequest(telegram_user_id="12345", counselor_id=1)
        result = await group_repo.get_group_by_counselor_and_user_id(
            mock_db_session, payload
        )

        assert result is not None
        assert result.id == 1
        assert result.user_alias == "test-alias"
        assert result.counselor_id == 1

    @pytest.mark.asyncio
    async def test_get_group_by_counselor_and_user_id_alias_not_found(
        self, mock_db_session
    ):
        """Test getting group when alias is not found."""
        # Mock the alias query to return None
        mock_alias_result = MagicMock()
        mock_alias_result.one_or_none.return_value = None
        mock_db_session.scalars.return_value = mock_alias_result

        payload = GroupLinkRequest(telegram_user_id="99999", counselor_id=1)
        result = await group_repo.get_group_by_counselor_and_user_id(
            mock_db_session, payload
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_get_group_by_counselor_and_user_id_group_not_found(
        self, mock_db_session
    ):
        """Test getting group when group is not found."""
        alias = Alias(telegram_user_id="12345", alias="test-alias")

        # Mock the alias query
        mock_alias_result = MagicMock()
        mock_alias_result.one_or_none.return_value = alias
        mock_db_session.scalars.return_value = mock_alias_result

        # Mock the group query to return None
        mock_group_result = MagicMock()
        mock_group_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_group_result

        payload = GroupLinkRequest(telegram_user_id="12345", counselor_id=1)
        result = await group_repo.get_group_by_counselor_and_user_id(
            mock_db_session, payload
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_get_group_by_counselor_group_id_found(self, mock_db_session):
        """Test getting group by counselor group ID when found."""
        group = Group(
            id=1,
            user_alias="test-alias",
            counselor_id=1,
            user_group_id=111,
            counselor_group_id=67890,
            active=True,
        )

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = group
        mock_db_session.execute.return_value = mock_result

        result = await group_repo.get_group_by_counselor_group_id(
            mock_db_session, 67890
        )

        assert result is not None
        assert result.id == 1
        assert result.counselor_group_id == 67890
        mock_db_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_group_by_counselor_group_id_not_found(self, mock_db_session):
        """Test getting group by counselor group ID when not found."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        result = await group_repo.get_group_by_counselor_group_id(
            mock_db_session, 99999
        )

        assert result is None
        mock_db_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_group_by_telegram_user_id_found(self, mock_db_session):
        """Test getting group by telegram user ID when found."""
        group = Group(
            id=1,
            user_alias="test-alias",
            counselor_id=1,
            user_group_id=12345,
            counselor_group_id=67890,
            active=True,
        )

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = group
        mock_db_session.execute.return_value = mock_result

        result = await group_repo.get_group_by_telegram_user_id(mock_db_session, 12345)

        assert result is not None
        assert result.id == 1
        assert result.user_group_id == 12345
        mock_db_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_group_by_telegram_user_id_not_found(self, mock_db_session):
        """Test getting group by telegram user ID when not found."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        result = await group_repo.get_group_by_telegram_user_id(mock_db_session, 99999)

        assert result is None
        mock_db_session.execute.assert_called_once()
