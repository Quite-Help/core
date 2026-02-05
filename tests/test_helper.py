from unittest.mock import patch
from app.util.helper import generate_alias


class TestGenerateAlias:
    """Test alias generation helper function."""

    @patch("app.util.helper.namer.generate")
    def test_generate_alias_calls_namer(self, mock_namer):
        """Test that generate_alias calls namer.generate."""
        mock_namer.return_value = "test-alias-123"
        result = generate_alias()
        mock_namer.assert_called_once()
        assert result == "test-alias-123"

    @patch("app.util.helper.namer.generate")
    def test_generate_alias_returns_string(self, mock_namer):
        """Test that generate_alias returns a string."""
        mock_namer.return_value = "another-alias"
        result = generate_alias()
        assert isinstance(result, str)
        assert result == "another-alias"

    @patch("app.util.helper.namer.generate")
    def test_generate_alias_different_results(self, mock_namer):
        """Test that generate_alias can return different values."""
        mock_namer.side_effect = ["alias-1", "alias-2", "alias-3"]

        result1 = generate_alias()
        result2 = generate_alias()
        result3 = generate_alias()

        assert result1 == "alias-1"
        assert result2 == "alias-2"
        assert result3 == "alias-3"
        assert mock_namer.call_count == 3
