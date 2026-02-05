import pytest
from unittest.mock import patch
from fastapi import HTTPException

from app.routes.counselor import get_counselors, get_counselor, create_counselor
from app.models.counselor import CreateCounselorRequest, CounselorInfo, CounselorResponse
from app.schema.counselor import Counselor


class TestGetCounselors:
    """Test the GET /counselors endpoint."""

    @pytest.mark.asyncio
    async def test_get_counselors_returns_list(self, mock_db_session):
        """Test that get_counselors returns a list of counselor info."""
        counselor1 = Counselor(
            id=1, first_name="John", last_name="Doe", bio="Bio 1", telegram_id=111
        )
        counselor2 = Counselor(
            id=2, first_name="Jane", last_name="Smith", bio="Bio 2", telegram_id=222
        )

        with patch("app.routes.counselor.counselor_repo.get_all") as mock_get_all:
            mock_get_all.return_value = [counselor1, counselor2]

            result = await get_counselors(mock_db_session, _={})

            assert isinstance(result, list)
            assert len(result) == 2
            assert isinstance(result[0], CounselorInfo)
            assert result[0].id == 1
            assert result[0].name == "John Doe"
            assert result[1].id == 2
            assert result[1].name == "Jane Smith"
            mock_get_all.assert_called_once_with(mock_db_session)

    @pytest.mark.asyncio
    async def test_get_counselors_returns_empty_list(self, mock_db_session):
        """Test that get_counselors returns empty list when no counselors exist."""
        with patch("app.routes.counselor.counselor_repo.get_all") as mock_get_all:
            mock_get_all.return_value = []

            result = await get_counselors(mock_db_session, _={})

            assert isinstance(result, list)
            assert len(result) == 0
            mock_get_all.assert_called_once_with(mock_db_session)


class TestGetCounselor:
    """Test the GET /counselors/{counselorId} endpoint."""

    @pytest.mark.asyncio
    async def test_get_counselor_success(self, mock_db_session):
        """Test successful retrieval of a counselor by ID."""
        counselor = Counselor(
            id=1,
            first_name="John",
            last_name="Doe",
            bio="Test bio",
            telegram_id=12345,
        )

        with patch("app.routes.counselor.counselor_repo.get_by_id") as mock_get_by_id:
            mock_get_by_id.return_value = counselor

            result = await get_counselor(1, mock_db_session, _={})

            assert isinstance(result, CounselorResponse)
            assert result.id == 1
            assert result.name == "John Doe"
            assert result.bio == "Test bio"
            assert result.telegram_user_id == 12345
            mock_get_by_id.assert_called_once_with(mock_db_session, 1)

    @pytest.mark.asyncio
    async def test_get_counselor_not_found(self, mock_db_session):
        """Test that 404 is raised when counselor doesn't exist."""
        with patch("app.routes.counselor.counselor_repo.get_by_id") as mock_get_by_id:
            mock_get_by_id.return_value = None

            with pytest.raises(HTTPException) as exc_info:
                await get_counselor(999, mock_db_session, _={})

            assert exc_info.value.status_code == 404
            assert "Counselor not found" in str(exc_info.value.detail)
            mock_get_by_id.assert_called_once_with(mock_db_session, 999)


class TestCreateCounselor:
    """Test the POST /counselors endpoint."""

    def test_create_counselor_success(self, mock_db_session):
        """Test successful creation of a counselor."""
        payload = CreateCounselorRequest(
            first_name="John",
            last_name="Doe",
            bio="A new counselor",
            telegram_id=12345,
        )

        with patch("app.routes.counselor.counselor_repo.create_counselor") as mock_create:
            create_counselor(payload, mock_db_session, _={})

            mock_create.assert_called_once_with(mock_db_session, payload)

    def test_create_counselor_calls_repository(self, mock_db_session):
        """Test that create_counselor calls the repository function."""
        payload = CreateCounselorRequest(
            first_name="Jane",
            last_name="Smith",
            bio="Another counselor",
            telegram_id=67890,
        )

        with patch("app.routes.counselor.counselor_repo.create_counselor") as mock_create:
            create_counselor(payload, mock_db_session, _={})

            assert mock_create.called
            call_args = mock_create.call_args
            assert call_args[0][0] == mock_db_session
            assert call_args[0][1] == payload
