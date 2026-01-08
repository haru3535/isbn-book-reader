import pytest
from unittest.mock import Mock
from src.book_api_client import BookAPIClient
from src.openbd_client import BookInfo


class TestBookAPIClient:
    def setup_method(self):
        self.client = BookAPIClient()

    def test_openbd_priority(self):
        mock_openbd = Mock()
        mock_google = Mock()

        openbd_book = BookInfo(isbn="9784839974206", title="Test Book", source="openbd")
        mock_openbd.get_book_info.return_value = openbd_book
        mock_google.get_book_info.return_value = None

        client = BookAPIClient()
        client.openbd = mock_openbd
        client.google = mock_google

        result = client.get_book_info("9784839974206")

        assert result == openbd_book
        assert result.source == "openbd"
        mock_openbd.get_book_info.assert_called_once_with("9784839974206")
        mock_google.get_book_info.assert_not_called()

    def test_fallback_to_google_when_openbd_returns_none(self):
        mock_openbd = Mock()
        mock_google = Mock()

        mock_openbd.get_book_info.return_value = None
        google_book = BookInfo(isbn="9784839974206", title="Test Book", source="google_books")
        mock_google.get_book_info.return_value = google_book

        client = BookAPIClient()
        client.openbd = mock_openbd
        client.google = mock_google

        result = client.get_book_info("9784839974206")

        assert result == google_book
        assert result.source == "google_books"
        mock_openbd.get_book_info.assert_called_once_with("9784839974206")
        mock_google.get_book_info.assert_called_once_with("9784839974206")

    def test_both_apis_return_none(self):
        mock_openbd = Mock()
        mock_google = Mock()

        mock_openbd.get_book_info.return_value = None
        mock_google.get_book_info.return_value = None

        client = BookAPIClient()
        client.openbd = mock_openbd
        client.google = mock_google

        result = client.get_book_info("9999999999999")

        assert result is None
        mock_openbd.get_book_info.assert_called_once_with("9999999999999")
        mock_google.get_book_info.assert_called_once_with("9999999999999")

    def test_cache_mechanism(self):
        mock_openbd = Mock()
        mock_google = Mock()

        book = BookInfo(isbn="9784839974206", title="Test Book", source="openbd")
        mock_openbd.get_book_info.return_value = book

        client = BookAPIClient()
        client.openbd = mock_openbd
        client.google = mock_google

        result1 = client.get_book_info("9784839974206", use_cache=True)
        result2 = client.get_book_info("9784839974206", use_cache=True)

        assert result1 == book
        assert result2 == book
        mock_openbd.get_book_info.assert_called_once()

    def test_cache_disabled(self):
        mock_openbd = Mock()
        mock_google = Mock()

        book = BookInfo(isbn="9784839974206", title="Test Book", source="openbd")
        mock_openbd.get_book_info.return_value = book

        client = BookAPIClient()
        client.openbd = mock_openbd
        client.google = mock_google

        result1 = client.get_book_info("9784839974206", use_cache=False)
        result2 = client.get_book_info("9784839974206", use_cache=False)

        assert result1 == book
        assert result2 == book
        assert mock_openbd.get_book_info.call_count == 2
