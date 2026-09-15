import sqlite3
from datetime import date
from pathlib import Path

import streamlit as st


DATABASE_PATH = Path(__file__).resolve().parent / "plans.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memory_date TEXT NOT NULL,
                title TEXT NOT NULL,
                place TEXT,
                memo TEXT,
                image BLOB,
                image_type TEXT
            )
            """
        )


def add_memory(memory_date, title, place, memo, image, image_type):
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO memories
                (memory_date, title, place, memo, image, image_type)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                memory_date.isoformat(),
                title,
                place,
                memo,
                image,
                image_type,
            ),
        )


def get_memories():
    with get_connection() as connection:
        return connection.execute(
            "SELECT * FROM memories ORDER BY memory_date DESC, id DESC"
        ).fetchall()


def delete_memory(memory_id):
    with get_connection() as connection:
        connection.execute("DELETE FROM memories WHERE id = ?", (memory_id,))


def render_memory_tab():
    initialize_database()

    st.markdown(
        """
        <style>
        .memory-intro { color: #332b35; margin-bottom: 1rem; }
        .memory-card { background: rgba(255, 255, 255, 0.78); border: 1px solid #f3d9e4; border-radius: 0.7rem; padding: 0.8rem; }
        .memory-date { color: #a35c7b; font-size: 0.8rem; }
        .memory-title { color: #332b35; font-size: 1.05rem; font-weight: 700; }
        </style>
        <p class="memory-intro">ふたりで過ごした時間を、写真と一緒に残そう。</p>
        """,
        unsafe_allow_html=True,
    )

    form_column, list_column = st.columns([1, 1.35], gap="large")

    with form_column:
        st.subheader("思い出を追加")
        with st.form("memory_form", clear_on_submit=True):
            memory_date = st.date_input("日にち", value=date.today())
            title = st.text_input("タイトル", placeholder="旅行・記念日ディナーなど")
            place = st.text_input("場所（任意）", placeholder="東京・仙台など")
            memo = st.text_area("思い出メモ（任意）", placeholder="楽しかったことを書こう")
            image_file = st.file_uploader("写真（任意）", type=["jpg", "jpeg", "png", "webp"])
            submitted = st.form_submit_button("📸 思い出を追加", use_container_width=True)

        if submitted:
            if not title.strip():
                st.error("タイトルを入力してください。")
            else:
                image = image_file.getvalue() if image_file else None
                image_type = image_file.type if image_file else None
                add_memory(
                    memory_date,
                    title.strip(),
                    place.strip(),
                    memo.strip(),
                    image,
                    image_type,
                )
                st.success("思い出を追加しました！")
                st.rerun()

    with list_column:
        st.subheader("ふたりの思い出")
        memories = get_memories()
        if not memories:
            st.info("まだ思い出がありません。最初の思い出を追加しよう！")
            return

        for memory in memories:
            memory_date = date.fromisoformat(memory["memory_date"])
            st.markdown(
                f"<div class='memory-date'>{memory_date.year}/{memory_date.month}/{memory_date.day}</div>",
                unsafe_allow_html=True,
            )
            st.markdown(f"<div class='memory-title'>{memory['title']}</div>", unsafe_allow_html=True)
            if memory["place"]:
                st.caption(f"📍 {memory['place']}")
            if memory["image"]:
                st.image(memory["image"], use_container_width=True)
            if memory["memo"]:
                st.write(memory["memo"])
            if st.button("削除", key=f"memory_delete_{memory['id']}"):
                delete_memory(memory["id"])
                st.rerun()
            st.divider()
