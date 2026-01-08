import pytest
import json
import responses
from pathlib import Path
from src.openbd_client import OpenBDClient, BookInfo


class TestOpenBDClient:
    def setup_method(self):
        self.client = OpenBDClient()
        fixtures_path = Path(__file__).parent / 'fixtures' / 'mock_responses.json'
        with open(fixtures_path) as f:
            self.mock_data = json.load(f)

    @responses.activate
    def test_get_book_info_success(self):
        isbn = "9784839974206"
        responses.add(
            responses.GET,
            f"https://api.openbd.jp/v1/get?isbn={isbn}",
            json=self.mock_data['openbd_success'],
            status=200
        )

        book = self.client.get_book_info(isbn)

        assert book is not None
        assert book.isbn == isbn
        assert book.title == "リーダブルコード"
        assert "Dustin Boswell" in book.authors[0]
        assert book.publisher == "オライリー・ジャパン"
        assert book.page_count == 260
        assert book.cover_image_url == "https://cover.openbd.jp/9784839974206.jpg"
        assert book.source == "openbd"

    @responses.activate
    def test_get_book_info_not_found(self):
        isbn = "9999999999999"
        responses.add(
            responses.GET,
            f"https://api.openbd.jp/v1/get?isbn={isbn}",
            json=self.mock_data['openbd_not_found'],
            status=200
        )

        book = self.client.get_book_info(isbn)

        assert book is None

    @responses.activate
    def test_get_book_info_api_error(self):
        isbn = "9784839974206"
        responses.add(
            responses.GET,
            f"https://api.openbd.jp/v1/get?isbn={isbn}",
            json={"error": "Internal server error"},
            status=500
        )

        book = self.client.get_book_info(isbn)

        assert book is None

    def test_parse_response_with_full_data(self):
        data = self.mock_data['openbd_success'][0]

        book = self.client._parse_response(data)

        assert book is not None
        assert book.isbn == "9784839974206"
        assert book.title == "リーダブルコード"
        assert book.page_count == 260

    def test_parse_response_with_null(self):
        book = self.client._parse_response(None)

        assert book is None
