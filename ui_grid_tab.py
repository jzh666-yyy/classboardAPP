import datetime

import schedule as sch
import streamlit as st
from config import TIME_SLOTS, WEEK_DAYS
from ui_helpers import build_today_report_rows, rows_to_csv_text


def render_grid_tab(edit_task_dialog, add_custom_task_dialog):
    """Tab2 周视图：独立周次、轻量渲染、固定紧凑网格。"""
    now_time = datetime.datetime.now().time()
    today_idx = datetime.datetime.now().weekday()
    today_str = WEEK_DAYS[today_idx] if 0 <= today_idx < len(WEEK_DAYS) else WEEK_DAYS[0]

    def short_title(raw):
        text = str(raw or "").replace("📌", "").replace("📘", "").strip()
        return text if len(text) <= 9 else f"{text[:9]}…"

    # 预计算本周任务数据（避免网格内重复扫描）。
    day_tasks_map = {}
    day_slot_task_map = {}
    for day_name in WEEK_DAYS:
        day_courses = sch.get_day_schedule_by_week(st.session_state.tab2_week, day_name)
        day_customs = [
            t
            for t in st.session_state.custom_tasks
            if t.get("day") == day_name and t.get("week") == st.session_state.tab2_week
        ]
        all_tasks = sorted(day_courses + day_customs, key=lambda x: x.get("time", ""))
        day_tasks_map[day_name] = all_tasks

        slot_map = {}
        for task in all_tasks:
            for slot_num in task.get("slots", []):
                if slot_num not in slot_map:
                    slot_map[slot_num] = task
        day_slot_task_map[day_name] = slot_map

    # 导出数据（按 tab2_week 生成，与主界面周次逻辑分离）。
    day_rows = build_today_report_rows(day_tasks_map.get(today_str, []), now_time)
    for row in day_rows:
        row["周次"] = st.session_state.tab2_week
        row["星期"] = today_str

    week_rows = []
    for day_name in WEEK_DAYS:
        rows = build_today_report_rows(day_tasks_map.get(day_name, []), now_time)
        for row in rows:
            row["周次"] = st.session_state.tab2_week
            row["星期"] = day_name
            week_rows.append(row)

    day_csv = rows_to_csv_text(day_rows)
    week_csv = rows_to_csv_text(week_rows)

    custom_week_tasks = [
        t for t in st.session_state.custom_tasks if t.get("week") == st.session_state.tab2_week
    ]

    def render_task_segment(task, slot_num, show_text):
        slots = task.get("slots", [])
        if not slots:
            return

        is_start = slot_num == slots[0]
        is_end = slot_num == slots[-1]

        bg_color = "#fef3c7" if task.get("is_custom") else "#eff6ff"
        border_color = "#f59e0b" if task.get("is_custom") else "#bfdbfe"
        text_color = "#92400e" if task.get("is_custom") else "#1e40af"

        if task.get("completed"):
            bg_color = "#f3f4f6"
            border_color = "#d1d5db"
            text_color = "#9ca3af"

        if is_start and not is_end:
            border_style = f"border:1px solid {border_color};"
            border_radius = "6px 6px 0 0"
        elif (not is_start) and is_end:
            border_style = (
                f"border-left:1px solid {border_color};"
                f"border-right:1px solid {border_color};"
                f"border-bottom:1px solid {border_color};"
                "border-top:0;"
            )
            border_radius = "0 0 6px 6px"
        elif (not is_start) and (not is_end):
            border_style = (
                f"border-left:1px solid {border_color};"
                f"border-right:1px solid {border_color};"
                "border-top:0;border-bottom:0;"
            )
            border_radius = "0"
        else:
            border_style = f"border:1px solid {border_color};"
            border_radius = "6px"

        if show_text:
            strike = "text-decoration: line-through;" if task.get("completed") else ""
            content = (
                f"<strong style='color:{text_color}; font-size:11px; {strike}; "
                "display:block; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;'>"
                f"{short_title(task.get('title', ''))}</strong>"
            )
        else:
            content = "<span style='opacity:0;'>.</span>"

        st.markdown(
            f"""
            <div style="
                background-color:{bg_color};
                {border_style}
                border-radius:{border_radius};
                min-height:38px;
                padding:3px 6px;
                margin:0;
            ">
                {content}
            </div>
            """,
            unsafe_allow_html=True,
        )

    with st.sidebar:
        st.header("⚙️ 面板设置")
        selected_week = st.number_input(
            "当前周次 (第X周)", min_value=1, max_value=20, value=st.session_state.tab2_week
        )
        if selected_week != st.session_state.tab2_week:
            st.session_state.tab2_week = selected_week
            st.rerun()

        st.markdown("---")
        st.subheader("➕ 任务操作")
        quick_day = st.selectbox("星期", WEEK_DAYS, key="quick_add_day")
        quick_slot = st.selectbox(
            "起始节次",
            options=[s["slot"] for s in TIME_SLOTS],
            format_func=lambda x: f"第{x}节 ({TIME_SLOTS[x-1]['time']})",
            key="quick_add_slot",
        )
        if st.button("新增任务", use_container_width=True, key="btn_sidebar_add_task"):
            add_custom_task_dialog(quick_day, int(quick_slot))

        if custom_week_tasks:
            edit_map = {
                f"{t.get('day', '')} {t.get('time', '')} | {short_title(t.get('title', ''))}": t
                for t in custom_week_tasks
            }
            selected_label = st.selectbox("编辑已有任务", options=list(edit_map.keys()), key="quick_edit_task")
            if st.button("编辑选中任务", use_container_width=True, key="btn_sidebar_edit_task"):
                edit_task_dialog(edit_map[selected_label])

        st.markdown("---")
        st.subheader("📤 导出数据")
        st.download_button(
            "导出本周数据",
            data=week_csv.encode("utf-8-sig"),
            file_name=f"week_{st.session_state.tab2_week}_report.csv",
            mime="text/csv",
            use_container_width=True,
            key="download_week_csv",
        )
        st.download_button(
            "导出本日数据",
            data=day_csv.encode("utf-8-sig"),
            file_name=f"week_{st.session_state.tab2_week}_{today_str}_report.csv",
            mime="text/csv",
            use_container_width=True,
            key="download_day_csv",
        )

    st.markdown(f"### 🗓️ 第 {st.session_state.tab2_week} 周")

    grid_cols = st.columns([1.55, 1, 1, 1, 1, 1, 1, 1])
    with grid_cols[0]:
        st.markdown("**节次 (时间)**")
    for idx, day in enumerate(WEEK_DAYS):
        with grid_cols[idx + 1]:
            st.markdown(f"**{day}**")

    for slot_info in TIME_SLOTS:
        s_num = slot_info["slot"]
        s_time = slot_info["time"]
        slot_cols = st.columns([1.55, 1, 1, 1, 1, 1, 1, 1])

        with slot_cols[0]:
            st.markdown(
                f"<div class='grid-time-cell'><small><b>第{s_num}节</b><br>{s_time}</small></div>",
                unsafe_allow_html=True,
            )

        for idx, day in enumerate(WEEK_DAYS):
            with slot_cols[idx + 1]:
                task = day_slot_task_map.get(day, {}).get(s_num)
                if task:
                    show_text = s_num == task.get("slots", [s_num])[0]
                    render_task_segment(task, s_num, show_text=show_text)
                else:
                    st.markdown("<div class='grid-empty-cell'></div>", unsafe_allow_html=True)

    floating_tasks = [
        t
        for t in st.session_state.custom_tasks
        if t.get("week") == st.session_state.tab2_week and not t.get("slots")
    ]
    if floating_tasks:
        st.markdown("### 🧭 自由时间任务（不绑定节次）")
        for task in sorted(floating_tasks, key=lambda x: x.get("time", "")):
            st.markdown(
                f"""
                <div style="background:#fffbeb; border:1px solid #f59e0b; border-radius:8px; padding:8px 10px; margin-bottom:4px;">
                    <div style="font-weight:700; color:#92400e;">{task.get('title', '')}</div>
                    <div style="font-size:12px; color:#b45309;">{task.get('day', '')} | 🕒 {task.get('time', '')}</div>
                    <div style="font-size:12px; color:#78350f;">📍 {task.get('notes', '无备注')}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
