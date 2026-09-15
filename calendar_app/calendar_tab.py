import html
from datetime import date

import streamlit as st
from data_store import require_supabase


def initialize_database():
    require_supabase()


def add_plan(plan_date, end_date, title, place, memo, person):
    require_supabase().table("plans").insert({
        "plan_date": plan_date.isoformat(), "end_date": end_date.isoformat(),
        "title": title, "place": place, "memo": memo, "person": person,
    }).execute()


def get_plans(year, month):
    first_day = date(year, month, 1).isoformat()
    if month == 12:
        next_month = date(year + 1, 1, 1)
    else:
        next_month = date(year, month + 1, 1)
    last_day = (next_month.fromordinal(next_month.toordinal() - 1)).isoformat()
    return require_supabase().table("plans").select("*").lte("plan_date", last_day).gte("end_date", first_day).order("plan_date").execute().data


def delete_plan(plan_id):
    require_supabase().table("plans").delete().eq("id", plan_id).execute()


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


def render_month(year, month, plans, person_colors):
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
                plan_html = []
                for plan in plans_by_date.get(date_key, []):
                    color = person_colors.get(plan["person"], "#9b8cff")
                    label = html.escape(plan["title"])
                    memo = html.escape(plan["memo"] or "")
                    plan_html.append(
                        f"<div class='plan-chip' style='border-left-color:{color}' title='{memo}'>{label}</div>"
                    )
                st.markdown("<div class='calendar-day'>", unsafe_allow_html=True)
                if st.button(
                    str(day_number),
                    key=f"select_date_{date_key}",
                    help=f"{current_date.year}年{current_date.month}月{day_number}日を開始日にする",
                    use_container_width=True,
                ):
                    st.session_state.selected_plan_date = current_date
                    st.rerun()
                st.markdown("".join(plan_html) + "</div>", unsafe_allow_html=True)


def render_calendar_tab(people):
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
        .calendar-day button { background: transparent; border: 0; color: #332b35 !important; font-weight: 700; justify-content: flex-start; min-height: 1.8rem; padding: 0.1rem 0.25rem; }
        .calendar-day button:hover { background: #ffe0ec; border-color: #ffb5cd; }
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
    if "selected_plan_date" not in st.session_state:
        st.session_state.selected_plan_date = date.today()

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
    person_colors = {
        people["self"]: "#ff7aa8",
        people["partner"]: "#68b7ff",
        people["together"]: "#a88be8",
    }
    st.markdown(
        f"<div class='legend'>🌸 {people['self']}　　⚽ {people['partner']}　　💜 {people['together']}</div>",
        unsafe_allow_html=True,
    )
    render_month(year, month, plans, person_colors)

    st.divider()
    form_column, list_column = st.columns([1, 1.2], gap="large")

    with form_column:
        st.subheader("予定を追加する")
        selected_plan_date = st.session_state.selected_plan_date
        st.caption(f"開始日: {selected_plan_date.year}年{selected_plan_date.month}月{selected_plan_date.day}日")
        with st.form("add_plan_form", clear_on_submit=True):
            person = st.selectbox(
                "誰の予定？",
                [people["self"], people["partner"], people["together"]],
            )
            plan_date = st.date_input(
                "開始日",
                value=selected_plan_date,
                key=f"plan_start_{selected_plan_date.isoformat()}",
            )
            end_date = st.date_input(
                "終了日（別の日にすると日またぎ）",
                value=selected_plan_date,
                key=f"plan_end_{selected_plan_date.isoformat()}",
            )
            title = st.text_input("予定", placeholder="映画・宿泊など")
            place = st.text_input("場所（任意）", placeholder="東京・仙台など")
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
