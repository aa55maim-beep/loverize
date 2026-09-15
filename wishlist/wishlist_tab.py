import sqlite3
from pathlib import Path

import streamlit as st


DATABASE_PATH = Path(__file__).resolve().parent.parent / "plans.db"
def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS wishlist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                category TEXT NOT NULL,
                person TEXT NOT NULL,
                completed INTEGER NOT NULL DEFAULT 0
            )
            """
        )


def add_item(title, person):
    with get_connection() as connection:
        connection.execute(
            "INSERT INTO wishlist (title, category, person) VALUES (?, ?, ?)",
            (title, "", person),
        )


def get_items():
    with get_connection() as connection:
        return connection.execute(
            "SELECT * FROM wishlist ORDER BY completed, id DESC"
        ).fetchall()


def update_item(item_id, completed):
    with get_connection() as connection:
        connection.execute(
            "UPDATE wishlist SET completed = ? WHERE id = ?",
            (int(completed), item_id),
        )


def delete_item(item_id):
    with get_connection() as connection:
        connection.execute("DELETE FROM wishlist WHERE id = ?", (item_id,))


def render_wishlist_tab(people):
    initialize_database()

    st.markdown(
        """
        <style>
        .wishlist-intro { color: #332b35; margin-bottom: 1rem; }
        .wishlist-item { background: rgba(255, 255, 255, 0.78); border: 1px solid #f3d9e4; border-radius: 0.7rem; padding: 0.65rem 0.8rem; }
        .wishlist-category { color: #a35c7b; font-size: 0.78rem; font-weight: 700; }
        .wishlist-title { color: #332b35; font-size: 1rem; font-weight: 700; }
        .wishlist-owner { color: #756a73; font-size: 0.8rem; }
        </style>
        <p class="wishlist-intro">ふたりで叶えたいことを、思いついた順に残そう。</p>
        """,
        unsafe_allow_html=True,
    )

    form_column, list_column = st.columns([1, 1.35], gap="large")

    with form_column:
        st.subheader("したいことを追加")
        with st.form("wishlist_form", clear_on_submit=True):
            title = st.text_input("したいこと", placeholder="仙台に旅行する")
            person = st.selectbox(
                "誰のリスト？",
                [people["self"], people["partner"], people["together"]],
            )
            submitted = st.form_submit_button("✨ 追加する", use_container_width=True)

        if submitted:
            if not title.strip():
                st.error("したいことを入力してください。")
            else:
                add_item(title.strip(), person)
                st.success("リストに追加しました！")
                st.rerun()

    with list_column:
        st.subheader("ふたりのしたいこと")
        items = get_items()
        if not items:
            st.info("まだ項目がありません。最初のやりたいことを追加しよう！")
            return

        for number, item in enumerate(items, start=1):
            item_column, action_column = st.columns([5, 1], gap="small")
            with item_column:
                completed = st.checkbox(
                    f"{number}. {item['title']}",
                    value=bool(item["completed"]),
                    key=f"wishlist_completed_{item['id']}",
                )
                if completed != bool(item["completed"]):
                    update_item(item["id"], completed)
                    st.rerun()
                st.caption(item["person"])
            with action_column:
                if st.button("削除", key=f"wishlist_delete_{item['id']}"):
                    delete_item(item["id"])
                    st.rerun()
