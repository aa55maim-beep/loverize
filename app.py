import streamlit as st

from calendar_app.calendar_tab import render_calendar_tab
from memory import render_memory_tab
from wishlist.wishlist_tab import render_wishlist_tab


st.set_page_config(page_title="Calendar", page_icon="💗", layout="wide")


def require_allowed_user():
    if not st.user.is_logged_in:
        st.title("🔐 ログイン")
        st.write("登録されたGoogleアカウントでログインしてください。")
        if st.button("Googleでログイン"):
            st.login()
        st.stop()

    allowed_emails = {
        email.strip().lower()
        for email in st.secrets.get("allowed_emails", [])
        if email.strip()
    }
    user_email = st.user.email.strip().lower()

    if user_email not in allowed_emails:
        st.error("このアプリを利用できるアカウントではありません。")
        st.button("ログアウト", on_click=st.logout)
        st.stop()

    with st.sidebar:
        st.caption(f"ログイン中: {user_email}")
        st.button("ログアウト", on_click=st.logout)


require_allowed_user()

with st.sidebar:
    st.header("ふたりの設定")
    self_name = st.text_input("自分の名前", value="自分", key="self_name").strip() or "自分"
    partner_name = st.text_input("相手の名前", value="相手", key="partner_name").strip() or "相手"

people = {"self": self_name, "partner": partner_name, "together": "2人"}

st.markdown(
    """
    <style>
    .stApp { background-color: #fff1f6; }
    .stApp, .stApp p, .stApp label, .stApp [data-testid="stMarkdownContainer"], .stApp [data-testid="stWidgetLabel"] { color: #332b35 !important; }
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 { color: #332b35 !important; }
    .stApp [data-baseweb="tab"], .stApp [data-baseweb="tab"] p, .stApp [data-baseweb="tab"] span { color: #332b35 !important; }
    .stApp [data-testid="stFormSubmitButton"] button p, .stApp [data-testid="stFormSubmitButton"] button span { color: #332b35 !important; }
    [data-testid="stHeader"] { background: rgba(255, 241, 246, 0.8); }
    .hero { padding: 1.2rem 0 0.6rem; }
    .eyebrow { color: #e15b8d; font-size: 0.85rem; font-weight: 700; letter-spacing: 0.08em; }
    .hero h1 { color: #3d3040; margin: 0.2rem 0 0.4rem; font-size: 2.3rem; }
    .hero p { color: #796b78; margin: 0; }
    </style>
    <div class="hero">
      <div class="eyebrow">OUR LITTLE PLANS</div>
      <h1>💗 Calendar</h1>
    <p>ふたりの予定共有機能</p>
    </div>
    """,
    unsafe_allow_html=True,
)

calendar_page, wishlist_page, memories_page = st.tabs(
    ["📅 カレンダー", "⭐したいことリスト", "📸 思い出"]
)

with calendar_page:
    render_calendar_tab(people)

with wishlist_page:
    render_wishlist_tab(people)

with memories_page:
    render_memory_tab()
