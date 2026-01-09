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
    ) -> tuple[Optional[Dict[str, Any]], Optional[str]]:
        if not self.api_token:
            return None, "APIトークンが設定されていません"

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
                return response.json(), None
            else:
                error_msg = f"Status {response.status_code}: {response.text}"
                return None, error_msg

        except Exception as e:
            return None, f"エラー: {str(e)}"

    def _build_properties(self, book: BookInfo) -> Dict[str, Any]:
        properties = {}

        if book.title:
            properties["Name"] = {
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
            properties["Author"] = {
                "rich_text": [
                    {
                        "text": {"content": ", ".join(book.authors)}
                    }
                ]
            }

        if book.publisher:
            properties["Publisher"] = {
                "rich_text": [
                    {
                        "text": {"content": book.publisher}
                    }
                ]
            }

        if book.published_date:
            try:
                properties["Published"] = {
                    "date": {
                        "start": book.published_date
                    }
                }
            except:
                pass

        if book.page_count:
            properties["Pages"] = {
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
