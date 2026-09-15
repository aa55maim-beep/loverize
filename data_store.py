import streamlit as st
from supabase import Client, create_client


@st.cache_resource
def get_supabase() -> Client:
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_SERVICE_ROLE_KEY"],
    )


def require_supabase():
    if "SUPABASE_URL" not in st.secrets or "SUPABASE_SERVICE_ROLE_KEY" not in st.secrets:
        st.error("保存機能の設定が未完了です。管理者がSupabaseのSecretsを設定してください。")
        st.stop()
    return get_supabase()
