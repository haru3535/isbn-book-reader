from typing import Optional, Dict, Any
import requests
from src.openbd_client import BookInfo


class NotionClient:
    def __init__(self, api_token: Optional[str] = None):
        self.api_token = api_token
        self.base_url = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }

    def add_book_to_database(
        self,
        database_id: str,
        book: BookInfo
    ) -> Optional[Dict[str, Any]]:
        if not self.api_token:
            return None

        try:
            properties = self._build_properties(book)

            data = {
                "parent": {"database_id": database_id},
                "properties": properties
            }

            if book.cover_image_url:
                data["cover"] = {
                    "type": "external",
                    "external": {"url": book.cover_image_url}
                }

            response = requests.post(
                f"{self.base_url}/pages",
                headers=self.headers,
                json=data,
                timeout=10
            )

            if response.status_code in [200, 201]:
                return response.json()
            else:
                return None

        except Exception:
            return None

    def _build_properties(self, book: BookInfo) -> Dict[str, Any]:
        properties = {}

        if book.title:
            properties["名前"] = {
                "title": [
                    {
                        "text": {"content": book.title}
                    }
                ]
            }

        if book.isbn:
            properties["ISBN"] = {
                "rich_text": [
                    {
                        "text": {"content": book.isbn}
                    }
                ]
            }

        if book.authors:
            properties["著者"] = {
                "rich_text": [
                    {
                        "text": {"content": ", ".join(book.authors)}
                    }
                ]
            }

        if book.publisher:
            properties["出版社"] = {
                "rich_text": [
                    {
                        "text": {"content": book.publisher}
                    }
                ]
            }

        if book.published_date:
            properties["発行日"] = {
                "date": {
                    "start": book.published_date
                }
            }

        if book.page_count:
            properties["ページ数"] = {
                "number": book.page_count
            }

        return properties

    def get_property_mapping(self, database_id: str) -> Optional[Dict[str, str]]:
        if not self.api_token:
            return None

        try:
            response = requests.get(
                f"{self.base_url}/databases/{database_id}",
                headers=self.headers,
                timeout=10
            )

            if response.status_code == 200:
                db_data = response.json()
                properties = db_data.get("properties", {})
                return {name: prop["type"] for name, prop in properties.items()}

        except Exception:
            pass

        return None
