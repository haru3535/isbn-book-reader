from typing import Optional
import requests
from urllib.parse import quote


class AmazonCoverClient:
    def get_cover_url_by_isbn(self, isbn: str) -> Optional[str]:
        try:
            url = f"https://images-na.ssl-images-amazon.com/images/P/{isbn}.09.LZZZZZZZ.jpg"
            response = requests.head(url, timeout=5)
            if response.status_code == 200:
                return url
        except Exception:
            pass
        return None

    def get_cover_url_by_title(self, title: str, author: Optional[str] = None) -> Optional[str]:
        try:
            search_query = title
            if author:
                search_query = f"{title} {author}"

            search_url = f"https://www.amazon.co.jp/s?k={quote(search_query)}&i=stripbooks"

            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }

            response = requests.get(search_url, headers=headers, timeout=10)
            if response.status_code != 200:
                return None

            html = response.text

            import re
            img_pattern = r'https://m\.media-amazon\.com/images/I/[A-Za-z0-9_\-]+\._[A-Z0-9_]+_\.jpg'
            matches = re.findall(img_pattern, html)

            if matches:
                return matches[0]

        except Exception:
            pass

        return None
