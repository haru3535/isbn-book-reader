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

        # 優先順位: Amazon → Google Books → openBD
        # Amazon（最も詳細な情報）
        book = self.amazon.get_book_info(isbn)
        if book:
            self._cache[isbn] = book
            return book

        # Google Books（フォールバック）
        book = self.google.get_book_info(isbn)
        if book:
            # openBDから補完情報を取得
            openbd_book = self.openbd.get_book_info(isbn)
            if openbd_book:
                if not book.publisher and openbd_book.publisher:
                    book.publisher = openbd_book.publisher
                if not book.page_count and openbd_book.page_count:
                    book.page_count = openbd_book.page_count
                if not book.published_date and openbd_book.published_date:
                    book.published_date = openbd_book.published_date
                if not book.cover_image_url and openbd_book.cover_image_url:
                    book.cover_image_url = openbd_book.cover_image_url

            # 表紙画像のフォールバック（Amazon画像APIも試す）
            if not book.cover_image_url:
                amazon_cover = self.amazon.get_cover_url_by_isbn(isbn)
                if amazon_cover:
                    book.cover_image_url = amazon_cover

            self._cache[isbn] = book
            return book

        # openBD（最後のフォールバック）
        book = self.openbd.get_book_info(isbn)
        if book:
            # 表紙画像のフォールバック
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
