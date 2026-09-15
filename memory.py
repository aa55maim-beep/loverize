from datetime import date
from uuid import uuid4

import streamlit as st
from data_store import require_supabase


def initialize_database():
    require_supabase()


def add_memory(memory_date, title, place, memo, image_file):
    client = require_supabase()
    image_path = None
    if image_file:
        image_path = f"memories/{uuid4().hex}_{image_file.name}"
        client.storage.from_("memory-photos").upload(
            image_path, image_file.getvalue(), {"content-type": image_file.type}
        )
    client.table("memories").insert({
        "memory_date": memory_date.isoformat(), "title": title,
        "place": place, "memo": memo, "image_path": image_path,
    }).execute()


def get_memories():
    return require_supabase().table("memories").select("*").order("memory_date", desc=True).order("id", desc=True).execute().data


def delete_memory(memory_id):
    client = require_supabase()
    memory = client.table("memories").select("image_path").eq("id", memory_id).single().execute().data
    if memory and memory.get("image_path"):
        client.storage.from_("memory-photos").remove([memory["image_path"]])
    client.table("memories").delete().eq("id", memory_id).execute()


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
                add_memory(
                    memory_date,
                    title.strip(),
                    place.strip(),
                    memo.strip(),
                    image_file,
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
            if memory.get("image_path"):
                image_url = require_supabase().storage.from_("memory-photos").create_signed_url(memory["image_path"], 3600)["signedURL"]
                st.image(image_url, use_container_width=True)
            if memory["memo"]:
                st.write(memory["memo"])
            if st.button("削除", key=f"memory_delete_{memory['id']}"):
                delete_memory(memory["id"])
                st.rerun()
            st.divider()
