import requests

# テスト用のISBN（リーダブルコード）
test_isbn = "9784839974206"

print("=== openBD API テスト ===")
response = requests.get(f"https://api.openbd.jp/v1/get?isbn={test_isbn}")
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"Response: {data}")
    if data and data[0]:
        print("\n取得できたデータ:")
        summary = data[0].get('summary', {})
        print(f"  タイトル: {summary.get('title')}")
        print(f"  著者: {summary.get('author')}")
        print(f"  表紙URL: {summary.get('cover')}")

print("\n=== Google Books API テスト ===")
response = requests.get(f"https://www.googleapis.com/books/v1/volumes?q=isbn:{test_isbn}")
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"Total items: {data.get('totalItems')}")
    if data.get('totalItems', 0) > 0:
        volume_info = data['items'][0]['volumeInfo']
        print("\n取得できたデータ:")
        print(f"  タイトル: {volume_info.get('title')}")
        print(f"  著者: {volume_info.get('authors')}")
        print(f"  表紙URL: {volume_info.get('imageLinks', {}).get('thumbnail')}")
