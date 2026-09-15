import streamlit as st
from data_store import require_supabase


def get_connection():
    return require_supabase()


def initialize_database():
    get_connection()


def add_item(title, person):
    get_connection().table("wishlist").insert({"title": title, "category": "", "person": person}).execute()


def get_items():
    return get_connection().table("wishlist").select("*").order("completed").order("id", desc=True).execute().data


def update_item(item_id, completed):
    get_connection().table("wishlist").update({"completed": completed}).eq("id", item_id).execute()


def delete_item(item_id):
    get_connection().table("wishlist").delete().eq("id", item_id).execute()


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
