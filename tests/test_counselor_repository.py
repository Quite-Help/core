import pytest
from unittest.mock import MagicMock

from app.repositories import counselor_repo
from app.models.counselor import CreateCounselorRequest
from app.schema.counselor import Counselor


class TestCounselorRepository:
    """Test counselor repository functions."""

    @pytest.mark.asyncio
    async def test_get_all_returns_list(self, mock_db_session):
        """Test getting all counselors returns a list."""
        counselor1 = Counselor(
            id=1, first_name="John", last_name="Doe", bio="Test bio", telegram_id=12345
        )
        counselor2 = Counselor(
            id=2,
            first_name="Jane",
            last_name="Smith",
            bio="Another bio",
            telegram_id=67890,
        )

        mock_result = MagicMock()
        mock_result.all.return_value = [counselor1, counselor2]
        mock_db_session.scalars.return_value = mock_result

        result = await counselor_repo.get_all(mock_db_session)

        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0].id == 1
        assert result[1].id == 2
        mock_db_session.scalars.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_all_returns_empty_list(self, mock_db_session):
        """Test getting all counselors returns empty list when none exist."""
        mock_result = MagicMock()
        mock_result.all.return_value = []
        mock_db_session.scalars.return_value = mock_result

        result = await counselor_repo.get_all(mock_db_session)

        assert isinstance(result, list)
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_get_by_id_found(self, mock_db_session):
        """Test getting counselor by ID when found."""
        counselor = Counselor(
            id=1, first_name="John", last_name="Doe", bio="Test bio", telegram_id=12345
        )

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = counselor
        mock_db_session.execute.return_value = mock_result

        result = await counselor_repo.get_by_id(mock_db_session, 1)

        assert result is not None
        assert result.id == 1
        assert result.first_name == "John"
        assert result.last_name == "Doe"
        mock_db_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, mock_db_session):
        """Test getting counselor by ID when not found."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        result = await counselor_repo.get_by_id(mock_db_session, 999)

        assert result is None
        mock_db_session.execute.assert_called_once()

    def test_create_counselor(self, mock_db_session):
        """Test creating a new counselor."""
        payload = CreateCounselorRequest(
            first_name="John", last_name="Doe", bio="A test bio", telegram_id=12345
        )

        counselor_repo.create_counselor(mock_db_session, payload)

        # Verify that db.add was called
        assert mock_db_session.add.called

        # Get the counselor that was added
        call_args = mock_db_session.add.call_args[0][0]
        assert isinstance(call_args, Counselor)
        assert call_args.first_name == "John"
        assert call_args.last_name == "Doe"
        assert call_args.bio == "A test bio"
        assert call_args.telegram_id == 12345

    def test_create_counselor_different_values(self, mock_db_session):
        """Test creating counselors with different values."""
        payload1 = CreateCounselorRequest(
            first_name="John", last_name="Doe", bio="Bio 1", telegram_id=111
        )
        payload2 = CreateCounselorRequest(
            first_name="Jane", last_name="Smith", bio="Bio 2", telegram_id=222
        )

        counselor_repo.create_counselor(mock_db_session, payload1)
        counselor_repo.create_counselor(mock_db_session, payload2)

        assert mock_db_session.add.call_count == 2

        # Check first counselor
        first_counselor = mock_db_session.add.call_args_list[0][0][0]
        assert first_counselor.first_name == "John"
        assert first_counselor.telegram_id == 111

        # Check second counselor
        second_counselor = mock_db_session.add.call_args_list[1][0][0]
        assert second_counselor.first_name == "Jane"
        assert second_counselor.telegram_id == 222
