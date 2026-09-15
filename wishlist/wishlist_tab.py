import streamlit as st
from data_store import require_supabase


def get_connection():
    return require_supabase()


def initialize_database():
    get_connection()


def add_item(title, person):
    items = get_connection().table("wishlist").select("sort_order").eq("completed", False).order("sort_order", desc=True).limit(1).execute().data
    next_order = (items[0]["sort_order"] + 1) if items else 0
    get_connection().table("wishlist").insert({
        "title": title,
        "category": "",
        "person": person,
        "sort_order": next_order,
    }).execute()


def get_items():
    return get_connection().table("wishlist").select("*").order("completed").order("sort_order").order("id").execute().data


def update_item(item_id, completed):
    get_connection().table("wishlist").update({"completed": completed}).eq("id", item_id).execute()


def delete_item(item_id):
    get_connection().table("wishlist").delete().eq("id", item_id).execute()


def move_item(item_id, direction):
    client = get_connection()
    items = client.table("wishlist").select("id, sort_order").eq("completed", False).order("sort_order").execute().data
    current_index = next((index for index, item in enumerate(items) if item["id"] == item_id), None)
    if current_index is None:
        return
    target_index = current_index + direction
    if target_index < 0 or target_index >= len(items):
        return
    current_item = items[current_index]
    target_item = items[target_index]
    client.table("wishlist").update({"sort_order": target_item["sort_order"]}).eq("id", current_item["id"]).execute()
    client.table("wishlist").update({"sort_order": current_item["sort_order"]}).eq("id", target_item["id"]).execute()


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
        heading_column, edit_column = st.columns([4, 1])
        with heading_column:
            st.subheader("ふたりのしたいこと")
        with edit_column:
            edit_mode = st.toggle("編集", key="wishlist_edit_mode")

        items = get_items()
        if not items:
            st.info("まだ項目がありません。最初のやりたいことを追加しよう！")
            return

        active_items = [item for item in items if not item["completed"]]
        completed_items = [item for item in items if item["completed"]]

        for number, item in enumerate(active_items, start=1):
            item_column, done_column, action_column = st.columns([5, 1.2, 2.2], gap="small")
            with item_column:
                st.markdown(f"**{number}. {item['title']}**")
                st.caption(item["person"])
            with done_column:
                if st.button("できた！", key=f"wishlist_done_{item['id']}"):
                    update_item(item["id"], True)
                    st.rerun()
            with action_column:
                if edit_mode:
                    up_column, down_column, delete_column = st.columns(3)
                    with up_column:
                        if st.button("↑", key=f"wishlist_up_{item['id']}", help="上へ"):
                            move_item(item["id"], -1)
                            st.rerun()
                    with down_column:
                        if st.button("↓", key=f"wishlist_down_{item['id']}", help="下へ"):
                            move_item(item["id"], 1)
                            st.rerun()
                    with delete_column:
                        if st.button("消去", key=f"wishlist_delete_{item['id']}"):
                            delete_item(item["id"])
                            st.rerun()

        if completed_items:
            st.divider()
            st.subheader("叶えられたこと")
            for item in completed_items:
                item_column, restore_column, delete_column = st.columns([5, 1.2, 1.2], gap="small")
                with item_column:
                    st.markdown(f"~~{item['title']}~~")
                    st.caption(item["person"])
                with restore_column:
                    if edit_mode and st.button("戻す", key=f"wishlist_restore_{item['id']}"):
                        update_item(item["id"], False)
                        st.rerun()
                with delete_column:
                    if edit_mode and st.button("消去", key=f"wishlist_done_delete_{item['id']}"):
                        delete_item(item["id"])
                        st.rerun()
