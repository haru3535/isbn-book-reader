from typing import Optional, List
import requests
import re
from urllib.parse import quote
from src.openbd_client import BookInfo


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

    def get_book_info(self, isbn: str) -> Optional[BookInfo]:
        """Amazonの商品ページから書籍情報を取得"""
        try:
            # Amazon商品ページURL
            url = f"https://www.amazon.co.jp/dp/{isbn}"

            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept-Language': 'ja-JP,ja;q=0.9',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
            }

            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code != 200:
                return None

            html = response.text

            # タイトル取得
            title = None
            title_match = re.search(r'<span id="productTitle"[^>]*>([^<]+)</span>', html)
            if title_match:
                title = title_match.group(1).strip()

            # 著者取得
            authors = None
            author_match = re.search(r'<span class="author notFaded"[^>]*>.*?<a[^>]*>([^<]+)</a>', html, re.DOTALL)
            if author_match:
                authors = [author_match.group(1).strip()]

            # 出版社取得
            publisher = None
            publisher_match = re.search(r'出版社[^:]*:\s*([^(;]+)', html)
            if publisher_match:
                publisher = publisher_match.group(1).strip()

            # 発行日取得
            published_date = None
            date_match = re.search(r'発売日[^:]*:\s*(\d{4})/(\d{1,2})/(\d{1,2})', html)
            if date_match:
                year, month, day = date_match.groups()
                published_date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"

            # ページ数取得
            page_count = None
            page_match = re.search(r'(\d+)ページ', html)
            if page_match:
                try:
                    page_count = int(page_match.group(1))
                except ValueError:
                    pass

            # 表紙画像取得
            cover_url = None
            img_match = re.search(r'<img[^>]*id="landingImage"[^>]*src="([^"]+)"', html)
            if img_match:
                cover_url = img_match.group(1)
                # 高解像度画像に変更
                cover_url = re.sub(r'\._[A-Z0-9_]+_', '._SL500_', cover_url)

            # 説明取得
            description = None
            desc_match = re.search(r'<div[^>]*id="bookDescription_feature_div"[^>]*>.*?<span[^>]*>([^<]+)</span>', html, re.DOTALL)
            if desc_match:
                description = desc_match.group(1).strip()

            # データが十分取得できた場合のみBookInfoを返す
            if title or authors:
                return BookInfo(
                    isbn=isbn,
                    title=title,
                    authors=authors,
                    publisher=publisher,
                    published_date=published_date,
                    page_count=page_count,
                    description=description,
                    cover_image_url=cover_url,
                    source="Amazon"
                )

        except Exception as e:
            print(f"[DEBUG] Amazon scraping error for ISBN {isbn}: {str(e)}")
            pass

        return None
