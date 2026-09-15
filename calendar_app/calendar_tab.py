import html
import sqlite3
from datetime import date
from pathlib import Path

import streamlit as st


DATABASE_PATH = Path(__file__).resolve().parent.parent / "plans.db"
PERSON_COLORS = {"まい": "#ff7aa8", "かず": "#68b7ff", "2人": "#a88be8"}
PEOPLE = ["まい", "かず", "2人"]


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plan_date TEXT NOT NULL,
                end_date TEXT,
                title TEXT NOT NULL,
                place TEXT,
                memo TEXT,
                person TEXT NOT NULL
            )
            """
        )
        columns = {row["name"] for row in connection.execute("PRAGMA table_info(plans)")}
        if "end_date" not in columns:
            connection.execute("ALTER TABLE plans ADD COLUMN end_date TEXT")
            connection.execute("UPDATE plans SET end_date = plan_date WHERE end_date IS NULL")
        connection.execute("UPDATE plans SET person = 'まい' WHERE person = 'わたし'")
        connection.execute("UPDATE plans SET person = 'かず' WHERE person = 'パートナー'")


def add_plan(plan_date, end_date, title, place, memo, person):
    with get_connection() as connection:
        connection.execute(
            "INSERT INTO plans (plan_date, end_date, title, place, memo, person) VALUES (?, ?, ?, ?, ?, ?)",
            (plan_date.isoformat(), end_date.isoformat(), title, place, memo, person),
        )


def get_plans(year, month):
    first_day = date(year, month, 1).isoformat()
    if month == 12:
        next_month = date(year + 1, 1, 1)
    else:
        next_month = date(year, month + 1, 1)
    last_day = (next_month.fromordinal(next_month.toordinal() - 1)).isoformat()
    with get_connection() as connection:
        return connection.execute(
            """
            SELECT * FROM plans
            WHERE plan_date <= ? AND COALESCE(end_date, plan_date) >= ?
            ORDER BY plan_date, id
            """,
            (last_day, first_day),
        ).fetchall()


def delete_plan(plan_id):
    with get_connection() as connection:
        connection.execute("DELETE FROM plans WHERE id = ?", (plan_id,))


def month_cells(year, month):
    first_day = date(year, month, 1)
    if month == 12:
        next_month = date(year + 1, 1, 1)
    else:
        next_month = date(year, month + 1, 1)
    days_in_month = (next_month - first_day).days
    cells = [None] * first_day.weekday() + list(range(1, days_in_month + 1))
    cells.extend([None] * ((7 - len(cells) % 7) % 7))
    return cells


def render_month(year, month, plans):
    plans_by_date = {}
    for plan in plans:
        start_date = date.fromisoformat(plan["plan_date"])
        end_date = date.fromisoformat(plan["end_date"] or plan["plan_date"])
        current_date = start_date
        while current_date <= end_date:
            plans_by_date.setdefault(current_date.isoformat(), []).append(plan)
            current_date = date.fromordinal(current_date.toordinal() + 1)

    weekdays = ["月", "火", "水", "木", "金", "土", "日"]
    st.markdown(
        "<div class='weekday-row'>"
        + "".join(f"<div>{day}</div>" for day in weekdays)
        + "</div>",
        unsafe_allow_html=True,
    )

    cells = month_cells(year, month)
    for start in range(0, len(cells), 7):
        columns = st.columns(7)
        for index, day_number in enumerate(cells[start : start + 7]):
            with columns[index]:
                if day_number is None:
                    st.markdown("<div class='calendar-day empty-day'></div>", unsafe_allow_html=True)
                    continue

                current_date = date(year, month, day_number)
                date_key = current_date.isoformat()
                today_class = " today" if current_date == date.today() else ""
                plan_html = []
                for plan in plans_by_date.get(date_key, []):
                    color = PERSON_COLORS.get(plan["person"], "#9b8cff")
                    label = html.escape(plan["title"])
                    memo = html.escape(plan["memo"] or "")
                    plan_html.append(
                        f"<div class='plan-chip' style='border-left-color:{color}' title='{memo}'>{label}</div>"
                    )
                st.markdown(
                    f"<div class='calendar-day'><div class='day-number{today_class}'>{day_number}</div>{''.join(plan_html)}</div>",
                    unsafe_allow_html=True,
                )


def render_calendar_tab():
    st.markdown(
        """
        <style>
        .stApp, .stApp p, .stApp label, .stApp [data-testid="stMarkdownContainer"], .stApp [data-testid="stText"], .stApp [data-testid="stWidgetLabel"] { color: #332b35 !important; }
        .stApp input, .stApp textarea, .stApp select, .stApp [data-baseweb="input"] input { color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; }
        .stApp input::placeholder, .stApp textarea::placeholder { color: #ffffff !important; opacity: 0.85; }
        .stApp button p, .stApp button span { color: #ffffff !important; }
        .stApp [data-baseweb="tab"], .stApp [data-baseweb="tab"] p, .stApp [data-baseweb="tab"] span { color: #332b35 !important; }
        .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 { color: #332b35 !important; }
        .stApp [data-testid="stFormSubmitButton"] button p, .stApp [data-testid="stFormSubmitButton"] button span { color: #332b35 !important; }
        .weekday-row { display: grid; grid-template-columns: repeat(7, 1fr); gap: 0.5rem; margin: 1rem 0 0.35rem; color: #9b8c98; font-size: 0.85rem; text-align: center; }
        .day-number { color: #4b3d4c; font-weight: 700; padding: 0.35rem 0.45rem; }
        .day-number.today { background: #ffe0ec; border-radius: 999px; color: #c83f73; width: 2rem; text-align: center; }
        .calendar-day { background: rgba(255, 255, 255, 0.7); border: 1px solid #f3d9e4; border-radius: 0.55rem; box-sizing: border-box; height: 7rem; overflow: hidden; padding: 0.25rem; }
        .empty-day { background: rgba(255, 255, 255, 0.25); }
        .plan-chip { background: white; border-left: 4px solid #ff7aa8; border-radius: 0.45rem; color: #332b35; font-size: 0.72rem; margin: 0.18rem 0; overflow: hidden; padding: 0.28rem 0.35rem; text-overflow: ellipsis; white-space: nowrap; }
        .legend { color: #332b35; font-size: 0.85rem; margin: 0.5rem 0 1rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )
    initialize_database()

    if "calendar_year" not in st.session_state:
        st.session_state.calendar_year = date.today().year
        st.session_state.calendar_month = date.today().month

    year = st.session_state.calendar_year
    month = st.session_state.calendar_month
    month_label = f"{year}年{month}月"

    navigation_left, month_title, navigation_right = st.columns([1, 4, 1])
    with navigation_left:
        if st.button("‹ 前の月", use_container_width=True, key="previous_month"):
            if month == 1:
                st.session_state.calendar_year -= 1
                st.session_state.calendar_month = 12
            else:
                st.session_state.calendar_month -= 1
            st.rerun()
    with month_title:
        st.markdown(
            f"<h2 style='text-align:center;color:#4b3d4c;margin:0.3rem 0'>{month_label}</h2>",
            unsafe_allow_html=True,
        )
    with navigation_right:
        if st.button("次の月 ›", use_container_width=True, key="next_month"):
            if month == 12:
                st.session_state.calendar_year += 1
                st.session_state.calendar_month = 1
            else:
                st.session_state.calendar_month += 1
            st.rerun()

    plans = get_plans(year, month)
    st.markdown("<div class='legend'>🌸 まい　　⚽ かず　　💜 2人</div>", unsafe_allow_html=True)
    render_month(year, month, plans)

    st.divider()
    form_column, list_column = st.columns([1, 1.2], gap="large")

    with form_column:
        st.subheader("予定を追加する")
        with st.form("add_plan_form", clear_on_submit=True):
            person = st.selectbox("誰の予定？", PEOPLE)
            plan_date = st.date_input("開始日", value=date.today())
            end_date = st.date_input("終了日（泊まりなどは別の日に設定）", value=date.today())
            title = st.text_input("予定", placeholder="映画・かずの家にお泊りなど")
            place = st.text_input("場所（任意）", placeholder="府中・宮城など")
            memo = st.text_area("メモ（任意）", placeholder="チケットを予約する")
            submitted = st.form_submit_button("💗 予定を追加", use_container_width=True)

        if submitted:
            if not title.strip():
                st.error("予定名を入力してください。")
            elif end_date < plan_date:
                st.error("終了日は開始日以降の日付にしてください。")
            else:
                add_plan(plan_date, end_date, title.strip(), place.strip(), memo.strip(), person)
                st.success("予定を追加しました！")
                st.rerun()

    with list_column:
        st.subheader(f"{month_label}の予定")
        if not plans:
            st.info("まだ予定がありません。最初の予定を追加してみよう！")
        else:
            for plan in plans:
                plan_date = date.fromisoformat(plan["plan_date"])
                end_date = date.fromisoformat(plan["end_date"] or plan["plan_date"])
                date_label = f"{plan_date.month}/{plan_date.day}"
                if end_date != plan_date:
                    date_label += f"〜{end_date.month}/{end_date.day}"
                detail = f"{date_label} · {plan['person']} · {plan['title']}"
                if plan["place"]:
                    detail += f" · {plan['place']}"
                delete_column, detail_column = st.columns([1, 8])
                with delete_column:
                    if st.button("削除", key=f"delete_{plan['id']}"):
                        delete_plan(plan["id"])
                        st.rerun()
                with detail_column:
                    st.markdown(f"**{detail}**")
                    if plan["memo"]:
                        st.caption(plan["memo"])
