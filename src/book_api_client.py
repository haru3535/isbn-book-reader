from typing import Optional
from src.openbd_client import OpenBDClient, BookInfo
from src.google_books_client import GoogleBooksClient
from src.amazon_cover_client import AmazonCoverClient


class BookAPIClient:
    def __init__(self, google_api_key: Optional[str] = None):
        self.openbd = OpenBDClient()
        self.google = GoogleBooksClient(api_key=google_api_key)
        self.amazon = AmazonCoverClient()
        self._cache = {}

    def get_book_info(self, isbn: str, use_cache: bool = True) -> Optional[BookInfo]:
        if use_cache and isbn in self._cache:
            return self._cache[isbn]

        book = self.openbd.get_book_info(isbn)
        if book:
            if not book.cover_image_url:
                google_book = self.google.get_book_info(isbn)
                if google_book and google_book.cover_image_url:
                    book.cover_image_url = google_book.cover_image_url

            if not book.cover_image_url:
                amazon_cover = self.amazon.get_cover_url_by_isbn(isbn)
                if amazon_cover:
                    book.cover_image_url = amazon_cover

            if not book.cover_image_url and book.title:
                author = book.authors[0] if book.authors else None
                amazon_cover = self.amazon.get_cover_url_by_title(book.title, author)
                if amazon_cover:
                    book.cover_image_url = amazon_cover

            self._cache[isbn] = book
            return book

        book = self.google.get_book_info(isbn)
        if book:
            if not book.cover_image_url:
                amazon_cover = self.amazon.get_cover_url_by_isbn(isbn)
                if amazon_cover:
                    book.cover_image_url = amazon_cover

            if not book.cover_image_url and book.title:
                author = book.authors[0] if book.authors else None
                amazon_cover = self.amazon.get_cover_url_by_title(book.title, author)
                if amazon_cover:
                    book.cover_image_url = amazon_cover

            self._cache[isbn] = book
            return book

        return None
