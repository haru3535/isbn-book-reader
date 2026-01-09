import os
import streamlit as st
from PIL import Image
from datetime import datetime
from dotenv import load_dotenv

from src.isbn_detector import ISBNDetector
from src.book_api_client import BookAPIClient
from src.notion_client import NotionClient

load_dotenv()

if "detection_history" not in st.session_state:
    st.session_state.detection_history = []

if "notion_token" not in st.session_state:
    st.session_state.notion_token = os.getenv("NOTION_API_TOKEN", "")

if "notion_database_id" not in st.session_state:
    st.session_state.notion_database_id = os.getenv("NOTION_DATABASE_ID", "")

st.set_page_config(
    page_title="ISBN Book Reader",
    page_icon="📚",
    layout="wide"
)

st.markdown("""
<style>
  .block-container{padding-top:2rem; padding-bottom:2rem;}
  .book-card{border:1px solid #eee; border-radius:14px; padding:16px; margin:12px 0; background:#fff}
  .isbn-badge{background:#8bc34a; color:white; padding:4px 8px; border-radius:6px; font-size:0.85rem}
  .source-badge{background:#2196f3; color:white; padding:4px 8px; border-radius:6px; font-size:0.75rem; margin-left:8px}
</style>
""", unsafe_allow_html=True)

st.title("📚 ISBN Book Reader")
st.caption("画像からISBNバーコードを認識して書籍情報を取得")

tab1, tab2, tab3 = st.tabs(["📸 ISBN認識", "📚 履歴", "⚙️ 設定"])

with tab1:
    st.subheader("画像アップロード")

    input_method = st.radio(
        "入力方法",
        ["カメラ撮影", "ファイルアップロード"],
        horizontal=True
    )

    uploaded_file = None
    if input_method == "カメラ撮影":
        uploaded_file = st.camera_input("バーコードを撮影")
    else:
        uploaded_file = st.file_uploader(
            "画像をアップロード",
            type=["jpg", "jpeg", "png"],
            help="ISBNバーコードが写っている画像を選択"
        )

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="アップロード画像", use_container_width=True)

        with st.spinner("ISBNバーコードを検出中..."):
            detector = ISBNDetector()
            isbns = detector.detect_isbn(image)

        if not isbns:
            st.warning("⚠️ ISBNバーコードが検出できませんでした。")
            st.info("""
            **推奨事項:**
            - 明るい環境で撮影してください
            - バーコードが画像の中心に来るようにしてください
            - 解像度1280x720以上の画像を使用してください
            - バーコード全体がはっきり写っていることを確認してください
            """)
        else:
            st.success(f"✅ 検出されたISBN: {', '.join(isbns)}")

            api_client = BookAPIClient(
                google_api_key=os.getenv("GOOGLE_BOOKS_API_KEY")
            )

            for isbn in isbns:
                with st.spinner(f"書籍情報を取得中（ISBN: {isbn}）..."):
                    book = api_client.get_book_info(isbn)

                if book:
                    col1, col2 = st.columns([1, 3])

                    with col1:
                        if book.cover_image_url:
                            st.image(book.cover_image_url, width=150)
                        else:
                            st.info("📖 表紙画像なし")

                    with col2:
                        st.markdown(f"""
                        <div class="book-card">
                            <span class="isbn-badge">ISBN: {book.isbn}</span>
                            <span class="source-badge">{book.source}</span>
                            <h3 style="margin-top:12px;">{book.title or 'タイトル不明'}</h3>
                        </div>
                        """, unsafe_allow_html=True)

                        info_col1, info_col2 = st.columns(2)

                        with info_col1:
                            if book.authors:
                                st.write(f"**著者**: {', '.join(book.authors)}")
                            if book.publisher:
                                st.write(f"**出版社**: {book.publisher}")

                        with info_col2:
                            if book.published_date:
                                st.write(f"**発行日**: {book.published_date}")
                            if book.page_count:
                                st.write(f"**ページ数**: {book.page_count}")

                        if book.description:
                            with st.expander("📝 説明"):
                                st.write(book.description)

                        st.write("")
                        if st.session_state.notion_token and st.session_state.notion_database_id:
                            if st.button(f"📝 Notionに登録", key=f"notion_{isbn}"):
                                with st.spinner("Notionに登録中..."):
                                    notion_client = NotionClient(st.session_state.notion_token)
                                    result, error = notion_client.add_book_to_database(
                                        st.session_state.notion_database_id,
                                        book
                                    )
                                if result:
                                    st.success("✅ Notionデータベースに登録しました！")
                                else:
                                    st.error(f"❌ Notionへの登録に失敗しました。")
                                    if error:
                                        with st.expander("エラー詳細"):
                                            st.code(error)

                    st.session_state.detection_history.insert(0, {
                        "isbn": isbn,
                        "book": book,
                        "timestamp": datetime.now().isoformat()
                    })
                else:
                    st.error(f"❌ ISBN {isbn} の書籍情報が見つかりませんでした。")
                    st.info("openBD APIとGoogle Books APIの両方でデータが見つかりませんでした。")

with tab2:
    st.subheader("検出履歴")

    if not st.session_state.detection_history:
        st.info("まだ履歴がありません。「ISBN認識」タブで書籍を検索してください。")
    else:
        if st.button("履歴をクリア"):
            st.session_state.detection_history = []
            st.rerun()

        st.write(f"**合計: {len(st.session_state.detection_history)}件**")

        for idx, entry in enumerate(st.session_state.detection_history):
            book = entry["book"]
            timestamp = datetime.fromisoformat(entry["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")

            with st.expander(f"#{idx + 1} - {book.title or 'タイトル不明'} ({timestamp})"):
                col1, col2 = st.columns([1, 3])

                with col1:
                    if book.cover_image_url:
                        st.image(book.cover_image_url, width=120)

                with col2:
                    st.markdown(f"""
                    <span class="isbn-badge">ISBN: {book.isbn}</span>
                    <span class="source-badge">{book.source}</span>
                    """, unsafe_allow_html=True)

                    if book.authors:
                        st.write(f"**著者**: {', '.join(book.authors)}")
                    if book.publisher:
                        st.write(f"**出版社**: {book.publisher}")
                    if book.page_count:
                        st.write(f"**ページ数**: {book.page_count}")

with tab3:
    st.subheader("設定")

    st.write("**Notion連携設定**")

    notion_token_input = st.text_input(
        "Notion API トークン",
        value=st.session_state.notion_token,
        type="password",
        help="Notion Integration のシークレットトークンを入力"
    )

    notion_db_input = st.text_input(
        "Notion データベースID",
        value=st.session_state.notion_database_id,
        help="書籍を登録するNotionデータベースのID（32桁の英数字）。URLの?以降は含めないでください。",
        placeholder="例: 1e1d8e68479381d78152c6def101615c"
    )

    if st.button("Notion設定を保存"):
        st.session_state.notion_token = notion_token_input
        st.session_state.notion_database_id = notion_db_input
        st.success("✅ Notion設定を保存しました！")

    if st.session_state.notion_token and st.session_state.notion_database_id:
        st.info("✅ Notion連携が有効です")

        with st.expander("📚 Notionデータベースの必要プロパティ"):
            st.markdown("""
            以下のプロパティを持つデータベースを作成してください：

            | プロパティ名 | タイプ |
            |------------|--------|
            | Name | タイトル |
            | ISBN | テキスト（推奨）または数値 |
            | Author | テキスト |
            | Publisher | テキスト |
            | Published | 日付 |
            | Pages | 数値 |

            **重要**: プロパティ名は英語で、完全に一致させてください。

            **注意**: ISBNは「テキスト」タイプを推奨します。「数値」でも動作しますが先頭のゼロが削除されます。

            表紙画像は自動的にページカバーとして設定されます。

            詳しいセットアップ方法は NOTION_SETUP.md を参照してください。
            """)
    else:
        st.warning("⚠️ Notion連携を使用するには、上記の設定が必要です")

    st.write("---")

    st.write("**Google Books API キー**")
    api_key = st.text_input(
        "APIキーを入力（オプション）",
        type="password",
        help="APIキーなしでも動作しますが、レート制限があります（1000 req/day）"
    )

    if api_key:
        st.info("💡 APIキーは現在のセッションでのみ有効です。永続的に設定する場合は .env ファイルに保存してください。")

    st.write("---")
    st.write("**About**")
    st.markdown("""
    このアプリは画像からISBNバーコードを認識し、書籍情報を取得します。

    **機能:**
    - バーコード認識による ISBN 検出
    - openBD API / Google Books API から書籍情報を取得
    - 履歴管理

    **データソース:**
    - openBD API（優先）: 日本の書籍データベース
    - Google Books API（フォールバック）: 洋書・古い書籍に強い
    """)

    st.write("---")
    st.write("**デバッグ情報**")
    if st.checkbox("デバッグモードを有効化"):
        st.json({
            "detection_history_count": len(st.session_state.detection_history),
            "google_api_key_set": bool(os.getenv("GOOGLE_BOOKS_API_KEY")),
            "zbar_available": True
        })
