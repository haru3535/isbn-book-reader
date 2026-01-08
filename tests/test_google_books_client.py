import pytest
import json
import responses
from pathlib import Path
from src.google_books_client import GoogleBooksClient
from src.openbd_client import BookInfo


class TestGoogleBooksClient:
    def setup_method(self):
        self.client = GoogleBooksClient()
        fixtures_path = Path(__file__).parent / 'fixtures' / 'mock_responses.json'
        with open(fixtures_path) as f:
            self.mock_data = json.load(f)

    @responses.activate
    def test_get_book_info_success(self):
        isbn = "9784839974206"
        responses.add(
            responses.GET,
            f"https://www.googleapis.com/books/v1/volumes",
            json=self.mock_data['google_books_success'],
            status=200
        )

        book = self.client.get_book_info(isbn)

        assert book is not None
        assert book.isbn == isbn
        assert book.title == "リーダブルコード"
        assert "Dustin Boswell" in book.authors
        assert book.publisher == "オライリー・ジャパン"
        assert book.page_count == 260
        assert book.source == "google_books"

    @responses.activate
    def test_get_book_info_not_found(self):
        isbn = "9999999999999"
        responses.add(
            responses.GET,
            f"https://www.googleapis.com/books/v1/volumes",
            json=self.mock_data['google_books_not_found'],
            status=200
        )

        book = self.client.get_book_info(isbn)

        assert book is None

    @responses.activate
    def test_get_book_info_api_error(self):
        isbn = "9784839974206"
        responses.add(
            responses.GET,
            f"https://www.googleapis.com/books/v1/volumes",
            json={"error": "Internal server error"},
            status=500
        )

        book = self.client.get_book_info(isbn)

        assert book is None

    @responses.activate
    def test_get_book_info_with_api_key(self):
        isbn = "9784839974206"
        api_key = "test_api_key"
        client = GoogleBooksClient(api_key=api_key)

        responses.add(
            responses.GET,
            f"https://www.googleapis.com/books/v1/volumes",
            json=self.mock_data['google_books_success'],
            status=200
        )

        book = client.get_book_info(isbn)

        assert book is not None
        assert responses.calls[0].request.url.endswith(f"q=isbn%3A{isbn}&key={api_key}")

    def test_parse_response_with_full_data(self):
        data = self.mock_data['google_books_success']

        book = self.client._parse_response(data, "9784839974206")

        assert book is not None
        assert book.isbn == "9784839974206"
        assert book.title == "リーダブルコード"
        assert book.page_count == 260

    def test_parse_response_with_no_items(self):
        data = self.mock_data['google_books_not_found']

        book = self.client._parse_response(data, "9999999999999")

        assert book is None
