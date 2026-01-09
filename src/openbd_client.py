from typing import Optional, List, Dict, Any
from dataclasses import dataclass
import requests


@dataclass
class BookInfo:
    isbn: str
    title: Optional[str] = None
    authors: Optional[List[str]] = None
    publisher: Optional[str] = None
    published_date: Optional[str] = None
    page_count: Optional[int] = None
    description: Optional[str] = None
    cover_image_url: Optional[str] = None
    source: str = "unknown"


class OpenBDClient:
    BASE_URL = "https://api.openbd.jp/v1"

    def get_book_info(self, isbn: str) -> Optional[BookInfo]:
        try:
            response = requests.get(
                f"{self.BASE_URL}/get",
                params={"isbn": isbn},
                timeout=10
            )

            if response.status_code != 200:
                return None

            data = response.json()

            if not data or data[0] is None:
                return None

            return self._parse_response(data[0])

        except Exception:
            return None

    def _parse_response(self, data: Optional[Dict[str, Any]]) -> Optional[BookInfo]:
        if not data:
            return None

        try:
            summary = data.get('summary', {})
            onix = data.get('onix', {})

            isbn = summary.get('isbn', '')
            title = summary.get('title')
            author_str = summary.get('author', '')
            authors = [author_str] if author_str else None
            publisher = summary.get('publisher')
            pubdate = summary.get('pubdate')
            published_date = None
            if pubdate:
                if len(pubdate) == 8:
                    # YYYYMMDD形式
                    published_date = f"{pubdate[0:4]}-{pubdate[4:6]}-{pubdate[6:8]}"
                elif len(pubdate) == 6:
                    # YYYYMM形式（日は01とする）
                    published_date = f"{pubdate[0:4]}-{pubdate[4:6]}-01"
                elif len(pubdate) == 4:
                    # YYYY形式（月日は01-01とする）
                    published_date = f"{pubdate[0:4]}-01-01"

            cover_url = summary.get('cover')
            if cover_url == '':
                cover_url = None

            page_count = None
            descriptive_detail = onix.get('DescriptiveDetail', {})
            extents = descriptive_detail.get('Extent', [])
            for extent in extents:
                if extent.get('ExtentUnit') == '03':
                    try:
                        page_count = int(extent.get('ExtentValue', 0))
                    except (ValueError, TypeError):
                        pass

            description = None
            collateral_detail = onix.get('CollateralDetail', {})
            text_contents = collateral_detail.get('TextContent', [])
            if text_contents:
                description = text_contents[0].get('Text')

            return BookInfo(
                isbn=isbn,
                title=title,
                authors=authors,
                publisher=publisher,
                published_date=published_date,
                page_count=page_count,
                description=description,
                cover_image_url=cover_url,
                source="openbd"
            )

        except Exception:
            return None
