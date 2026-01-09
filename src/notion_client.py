from typing import Optional, Dict, Any, Tuple
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
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        if not self.api_token:
            return None, "APIトークンが設定されていません"

        try:
            clean_db_id = self._clean_database_id(database_id)
            if not clean_db_id:
                return None, "データベースIDの形式が正しくありません"

            property_types = self.get_property_mapping(clean_db_id)
            properties = self._build_properties(book, property_types)

            data = {
                "parent": {"database_id": clean_db_id},
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

    def _clean_database_id(self, database_id: str) -> Optional[str]:
        import re

        db_id = database_id.strip()

        db_id = db_id.split('?')[0]

        db_id = db_id.replace('-', '')

        db_id = re.sub(r'[^a-zA-Z0-9]', '', db_id)

        if len(db_id) != 32:
            return None

        formatted_id = f"{db_id[0:8]}-{db_id[8:12]}-{db_id[12:16]}-{db_id[16:20]}-{db_id[20:32]}"

        return formatted_id

    def _build_properties(self, book: BookInfo, property_types: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
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
            isbn_type = property_types.get("ISBN") if property_types else "rich_text"

            if isbn_type == "number":
                try:
                    isbn_numeric = int(book.isbn.replace("-", "").replace(" ", ""))
                    properties["ISBN"] = {"number": isbn_numeric}
                except ValueError:
                    properties["ISBN"] = {
                        "rich_text": [{"text": {"content": book.isbn}}]
                    }
            else:
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
