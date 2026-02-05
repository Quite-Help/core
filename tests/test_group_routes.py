import pytest
from unittest.mock import patch
from fastapi import HTTPException

from app.routes.group import create_group, resolve_group, get_group_link
from app.models.group import (
    CreateGroupRequest,
    ResolveGroupRequest,
    ResolveGroupResponse,
    GroupLinkRequest,
    GroupLinkResponse,
)
from app.schema.group import Group
from app.schema.counselor import Counselor


class TestCreateGroup:
    """Test the POST /groups endpoint."""

    def test_create_group_success(self, mock_db_session):
        """Test successful creation of a group."""
        payload = CreateGroupRequest(
            user_alias="test-alias",
            user_group_link="https://t.me/test",
            user_group_id=12345,
            counselor_id=1,
            counselor_group_id=67890,
        )

        with patch("app.routes.group.group_repo.create_group") as mock_create:
            create_group(payload, _={}, db=mock_db_session)

            mock_create.assert_called_once_with(mock_db_session, payload)

    def test_create_group_calls_repository(self, mock_db_session):
        """Test that create_group calls the repository function."""
        payload = CreateGroupRequest(
            user_alias="another-alias",
            user_group_link="https://t.me/another",
            user_group_id=11111,
            counselor_id=2,
            counselor_group_id=22222,
        )

        with patch("app.routes.group.group_repo.create_group") as mock_create:
            create_group(payload, _={}, db=mock_db_session)

            assert mock_create.called
            call_args = mock_create.call_args
            assert call_args[0][0] == mock_db_session
            assert call_args[0][1] == payload


class TestResolveGroup:
    """Test the POST /groups/resolve endpoint."""

    @pytest.mark.asyncio
    async def test_resolve_group_by_user_group_id(self, mock_db_session):
        """Test resolving group by user group ID."""
        user_group = Group(
            id=1,
            user_alias="test-alias",
            counselor_id=1,
            user_group_id=12345,
            counselor_group_id=67890,
            active=True,
        )

        with patch(
            "app.routes.group.group_repo.get_group_by_telegram_user_id"
        ) as mock_get_user_group:
            mock_get_user_group.return_value = user_group

            payload = ResolveGroupRequest(group_id=12345)
            result = await resolve_group(payload, _={}, db=mock_db_session)

            assert isinstance(result, ResolveGroupResponse)
            assert result.target_group_id == 67890
            assert result.display_name == "test-alias"
            mock_get_user_group.assert_called_once_with(mock_db_session, 12345)

    @pytest.mark.asyncio
    async def test_resolve_group_by_counselor_group_id(self, mock_db_session):
        """Test resolving group by counselor group ID."""
        counselor_group = Group(
            id=1,
            user_alias="test-alias",
            counselor_id=1,
            user_group_id=12345,
            counselor_group_id=67890,
            active=True,
        )
        counselor = Counselor(
            id=1, first_name="John", last_name="Doe", bio="Bio", telegram_id=111
        )

        with (
            patch(
                "app.routes.group.group_repo.get_group_by_telegram_user_id"
            ) as mock_get_user_group,
            patch(
                "app.routes.group.group_repo.get_group_by_counselor_group_id"
            ) as mock_get_counselor_group,
            patch("app.routes.group.counselor_repo.get_by_id") as mock_get_counselor,
        ):
            mock_get_user_group.return_value = None
            mock_get_counselor_group.return_value = counselor_group
            mock_get_counselor.return_value = counselor

            payload = ResolveGroupRequest(group_id=67890)
            # Note: The route has a bug - it uses counselor.firstName/lastName
            # but the model uses first_name/last_name. This will cause an AttributeError.
            # The test expects this error to reveal the bug.
            result = await resolve_group(payload, _={}, db=mock_db_session)                
            
            mock_get_user_group.assert_called_once_with(mock_db_session, 67890)
            mock_get_counselor_group.assert_called_once_with(mock_db_session, 67890)
            mock_get_counselor.assert_called_once_with(mock_db_session, 1)
            assert result.display_name == f"{counselor.first_name} {counselor.last_name}"
            assert result.target_group_id == counselor_group.user_group_id

    @pytest.mark.asyncio
    async def test_resolve_group_not_found(self, mock_db_session):
        """Test that 404 is raised when group is not found."""
        with (
            patch(
                "app.routes.group.group_repo.get_group_by_telegram_user_id"
            ) as mock_get_user_group,
            patch(
                "app.routes.group.group_repo.get_group_by_counselor_group_id"
            ) as mock_get_counselor_group,
        ):
            mock_get_user_group.return_value = None
            mock_get_counselor_group.return_value = None

            payload = ResolveGroupRequest(group_id=99999)

            with pytest.raises(HTTPException) as exc_info:
                await resolve_group(payload, _={}, db=mock_db_session)

            assert exc_info.value.status_code == 404
            assert "group not found" in str(exc_info.value.detail)
            mock_get_user_group.assert_called_once_with(mock_db_session, 99999)
            mock_get_counselor_group.assert_called_once_with(mock_db_session, 99999)


class TestGetGroupLink:
    """Test the POST /groups/link endpoint."""

    @pytest.mark.asyncio
    async def test_get_group_link_success(self, mock_db_session):
        """Test successful retrieval of group link."""
        group = Group(
            id=1,
            user_alias="test-alias",
            counselor_id=1,
            user_group_id=12345,
            counselor_group_id=67890,
            user_group_link="https://t.me/test-group",
            active=True,
        )

        with patch(
            "app.routes.group.group_repo.get_group_by_counselor_and_user_id"
        ) as mock_get_group:
            mock_get_group.return_value = group

            payload = GroupLinkRequest(telegram_user_id="12345", counselor_id=1)
            result = await get_group_link(payload, _={}, db=mock_db_session)

            assert isinstance(result, GroupLinkResponse)
            assert result.group_link == "https://t.me/test-group"
            mock_get_group.assert_called_once_with(mock_db_session, payload)

    @pytest.mark.asyncio
    async def test_get_group_link_not_found(self, mock_db_session):
        """Test that 404 is raised when group is not found."""
        with patch(
            "app.routes.group.group_repo.get_group_by_counselor_and_user_id"
        ) as mock_get_group:
            mock_get_group.return_value = None

            payload = GroupLinkRequest(telegram_user_id="99999", counselor_id=999)

            with pytest.raises(HTTPException) as exc_info:
                await get_group_link(payload, _={}, db=mock_db_session)

            assert exc_info.value.status_code == 404
            assert "group not found" in str(exc_info.value.detail)
            mock_get_group.assert_called_once_with(mock_db_session, payload)

    @pytest.mark.asyncio
    async def test_get_group_link_none_link(self, mock_db_session):
        """Test group link when user_group_link is None."""
        group = Group(
            id=1,
            user_alias="test-alias",
            counselor_id=1,
            user_group_id=12345,
            counselor_group_id=67890,
            user_group_link=None,
            active=True,
        )

        with patch(
            "app.routes.group.group_repo.get_group_by_counselor_and_user_id"
        ) as mock_get_group:
            mock_get_group.return_value = group

            payload = GroupLinkRequest(telegram_user_id="12345", counselor_id=1)
            result = await get_group_link(payload, _={}, db=mock_db_session)

            assert isinstance(result, GroupLinkResponse)
            assert result.group_link is None
