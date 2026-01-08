from typing import Optional, Dict, Any
import requests
from src.openbd_client import BookInfo


class GoogleBooksClient:
    BASE_URL = "https://www.googleapis.com/books/v1/volumes"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key

    def get_book_info(self, isbn: str) -> Optional[BookInfo]:
        try:
            params = {"q": f"isbn:{isbn}"}
            if self.api_key:
                params["key"] = self.api_key

            response = requests.get(
                self.BASE_URL,
                params=params,
                timeout=10
            )

            if response.status_code != 200:
                return None

            data = response.json()

            return self._parse_response(data, isbn)

        except Exception:
            return None

    def _parse_response(self, data: Dict[str, Any], isbn: str) -> Optional[BookInfo]:
        if not data or data.get('totalItems', 0) == 0:
            return None

        try:
            items = data.get('items', [])
            if not items:
                return None

            volume_info = items[0].get('volumeInfo', {})

            title = volume_info.get('title')
            authors = volume_info.get('authors', [])
            publisher = volume_info.get('publisher')
            published_date = volume_info.get('publishedDate')
            description = volume_info.get('description')
            page_count = volume_info.get('pageCount')

            image_links = volume_info.get('imageLinks', {})
            cover_url = image_links.get('thumbnail')

            return BookInfo(
                isbn=isbn,
                title=title,
                authors=authors if authors else None,
                publisher=publisher,
                published_date=published_date,
                page_count=page_count,
                description=description,
                cover_image_url=cover_url,
                source="google_books"
            )

        except Exception:
            return None
