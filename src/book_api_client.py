from typing import Optional
import requests
from src.openbd_client import OpenBDClient, BookInfo
from src.google_books_client import GoogleBooksClient
from src.amazon_cover_client import AmazonCoverClient


class BookAPIClient:
    @staticmethod
    def is_valid_image_url(url: Optional[str], check_exists: bool = True) -> bool:
        """画像URLが有効な形式かチェック

        Args:
            url: チェックする画像URL
            check_exists: 実際にURLにアクセスして画像が存在するかチェックするか（デフォルト: True）

        Returns:
            bool: 有効な画像URLの場合True
        """
        if not url:
            return False

        # 画像拡張子のリスト
        valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']
        url_lower = url.lower()

        # URLが画像拡張子で終わっているかチェック
        # クエリパラメータがあってもOK（例: image.jpg?size=large）
        has_valid_extension = False
        for ext in valid_extensions:
            if ext in url_lower:
                has_valid_extension = True
                break

        if not has_valid_extension:
            return False

        # 実際に画像が存在するかチェック（オプション）
        if check_exists:
            try:
                response = requests.head(url, timeout=3, allow_redirects=True)
                # ステータスコードが200で、Content-Lengthが500バイト以上
                # （ダミー画像を除外）
                if response.status_code == 200:
                    content_length = response.headers.get('Content-Length')
                    if content_length and int(content_length) >= 500:
                        return True
                    # Content-Lengthがない場合は、GETで確認
                    elif not content_length:
                        response = requests.get(url, timeout=3, stream=True)
                        # 最初の1000バイトを読み込んで確認
                        chunk = next(response.iter_content(1000), None)
                        if chunk and len(chunk) >= 500:
                            return True
                return False
            except Exception:
                # ネットワークエラーの場合は拡張子チェックの結果を返す
                return has_valid_extension

        return has_valid_extension
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
        print(f"[DEBUG] Trying Amazon for ISBN {isbn}...")
        book = self.amazon.get_book_info(isbn)
        if book:
            print(f"[DEBUG] Got book from Amazon: title={book.title}, pages={book.page_count}")
            self._cache[isbn] = book
            return book
        print(f"[DEBUG] Amazon failed, trying Google Books...")

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
                # openBDの画像が有効な形式の場合のみ使用
                if not self.is_valid_image_url(book.cover_image_url) and openbd_book.cover_image_url:
                    if self.is_valid_image_url(openbd_book.cover_image_url):
                        book.cover_image_url = openbd_book.cover_image_url

            # ページ数や画像が不足している場合、Amazonでタイトル検索
            needs_amazon = (
                not book.page_count or
                not self.is_valid_image_url(book.cover_image_url)
            )

            if needs_amazon and book.title:
                print(f"[DEBUG] Missing data (pages={book.page_count}, valid_image={self.is_valid_image_url(book.cover_image_url)}), trying Amazon title search...")
                author = book.authors[0] if book.authors else None
                amazon_book = self.amazon.get_book_info_by_title(book.title, author, isbn)

                if amazon_book:
                    # Amazonから取得したデータで補完
                    if not book.page_count and amazon_book.page_count:
                        print(f"[DEBUG]補完: Pages {amazon_book.page_count}")
                        book.page_count = amazon_book.page_count
                    if not book.published_date and amazon_book.published_date:
                        print(f"[DEBUG] 補完: Published {amazon_book.published_date}")
                        book.published_date = amazon_book.published_date
                    if not self.is_valid_image_url(book.cover_image_url) and self.is_valid_image_url(amazon_book.cover_image_url):
                        print(f"[DEBUG] 補完: Cover image from Amazon")
                        book.cover_image_url = amazon_book.cover_image_url
                    if not book.description and amazon_book.description:
                        book.description = amazon_book.description

            self._cache[isbn] = book
            return book

        # openBD（最後のフォールバック）
        book = self.openbd.get_book_info(isbn)
        if book:
            # ページ数や画像が不足している場合、Amazonでタイトル検索
            needs_amazon = (
                not book.page_count or
                not self.is_valid_image_url(book.cover_image_url)
            )

            if needs_amazon and book.title:
                print(f"[DEBUG] Missing data from openBD (pages={book.page_count}, valid_image={self.is_valid_image_url(book.cover_image_url)}), trying Amazon title search...")
                author = book.authors[0] if book.authors else None
                amazon_book = self.amazon.get_book_info_by_title(book.title, author, isbn)

                if amazon_book:
                    # Amazonから取得したデータで補完
                    if not book.page_count and amazon_book.page_count:
                        print(f"[DEBUG] 補完: Pages {amazon_book.page_count}")
                        book.page_count = amazon_book.page_count
                    if not book.published_date and amazon_book.published_date:
                        print(f"[DEBUG] 補完: Published {amazon_book.published_date}")
                        book.published_date = amazon_book.published_date
                    if not self.is_valid_image_url(book.cover_image_url) and self.is_valid_image_url(amazon_book.cover_image_url):
                        print(f"[DEBUG] 補完: Cover image from Amazon")
                        book.cover_image_url = amazon_book.cover_image_url
                    if not book.description and amazon_book.description:
                        book.description = amazon_book.description

            self._cache[isbn] = book
            return book

        return None
