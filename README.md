# ISBN Book Reader

画像からISBNバーコードを認識して書籍情報を取得するWebアプリケーションです。Notionに埋め込み可能です。

## 特徴

- 📸 画像からISBNバーコードを自動認識
- 📚 openBD API / Google Books APIから書籍情報を取得
- 🎨 シンプルで使いやすいUI
- 📱 カメラ撮影・ファイルアップロード両対応
- 📝 検出履歴の管理
- ☁️ Streamlit Cloudでデプロイ可能

## 技術スタック

- **フレームワーク**: Streamlit
- **ISBN認識**: pyzbar（ZBar）
- **画像処理**: OpenCV、Pillow
- **書籍情報API**: openBD API（優先）→ Google Books API（フォールバック）

## セットアップ

### 1. リポジトリをクローン

```bash
git clone https://github.com/YOUR_USERNAME/isbn-book-reader.git
cd isbn-book-reader
```

### 2. 仮想環境を作成してライブラリをインストール

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. ZBarライブラリをインストール（macOS）

```bash
brew install zbar
```

### 4. 環境変数を設定（オプション）

```bash
cp .env.example .env
# .envファイルを編集してGoogle Books APIキーを設定（オプション）
```

### 5. アプリを起動

```bash
DYLD_LIBRARY_PATH=/opt/homebrew/lib:$DYLD_LIBRARY_PATH streamlit run app.py
```

ブラウザで http://localhost:8501 にアクセスします。

## テスト

```bash
DYLD_LIBRARY_PATH=/opt/homebrew/lib:$DYLD_LIBRARY_PATH pytest tests/ -v --cov=src
```

## Streamlit Cloudへのデプロイ

1. GitHubリポジトリにプッシュ

```bash
git add .
git commit -m "Initial commit"
git push origin main
```

2. [Streamlit Cloud](https://share.streamlit.io)にログイン

3. "New app" → GitHubリポジトリを選択 → `app.py` を指定

4. デプロイ完了後、固定URLが発行されます

## Notionへの埋め込み

1. Notionページで `/埋め込み` と入力

2. Streamlit CloudのURLを貼り付け

3. 完了！

## 使い方

### ISBN認識タブ

1. 「カメラ撮影」または「ファイルアップロード」を選択
2. ISBNバーコードが写っている画像をアップロード
3. 自動的にバーコードを認識し、書籍情報を取得

### 履歴タブ

- 過去に検出した書籍の履歴を確認
- 履歴のクリアも可能

### 設定タブ

- Google Books APIキーの設定（オプション）
- デバッグ情報の表示

## 推奨事項

バーコード認識の精度を上げるために：

- 明るい環境で撮影
- バーコードを画像の中心に配置
- 解像度1280x720以上の画像を使用
- バーコード全体がはっきり写っていることを確認

## API制約

- **openBD API**: レート制限なし、日本の書籍に強い
- **Google Books API**: APIキーなしで1000 req/day、洋書・古い書籍に強い

## ライセンス

MIT License
