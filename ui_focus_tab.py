import datetime

import schedule as sch
import streamlit as st
import task_manager as tm

from ui_helpers import (
    is_time_passed,
)


def render_focus_tab(change_tab1_week_dialog, show_current_task_dialog):
    st.session_state.current_week = st.session_state.tab1_week
    today_str, curr_task, next_task = sch.get_current_focus_task(st.session_state)
    now_dt = datetime.datetime.now()
    now_time = now_dt.time()

    c_head, c_edit = st.columns([8, 2])
    with c_head:
        st.markdown(
            f"""
            <h3 style="margin-bottom:0;">
                                 今天：{today_str} |
                <span style="color:#2563eb; border-bottom: 2px dashed #2563eb; padding-bottom: 2px;">第 {st.session_state.tab1_week} 周 ✏️</span>
            </h3>
            """,
            unsafe_allow_html=True,
        )
    with c_edit:
        if st.button("⚙️ 修改周次", key="btn_quick_change_week", help="点击调整焦点视图的周次"):
            change_tab1_week_dialog()

    st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)

    main_task = curr_task if curr_task else next_task

    if curr_task:
        card_label = f"🔥 正在进行：{curr_task['title']}\n🕒 {curr_task['time']}\n📍 {curr_task['notes']}"
        if st.button(
            card_label,
            key=f"current_task_card_{curr_task['id']}",
            use_container_width=True,
            type="tertiary",
            help="点击查看当前时间和当前任务详情",
        ):
            show_current_task_dialog(curr_task)
        if curr_task.get("steps"):
            st.markdown("#### 📋 Checklist 执行清单：")
            all_done = True
            for s_idx, step_item in enumerate(curr_task["steps"]):
                step_item["done"] = st.checkbox(
                    step_item["step"], value=step_item["done"], key=f"f_chk_{curr_task['id']}_{s_idx}"
                )
                if not step_item["done"]:
                    all_done = False
            if all_done and len(curr_task["steps"]) > 0 and curr_task.get("is_custom"):
                curr_task["completed"] = True
                tm.save_tasks(st.session_state.custom_tasks)

    elif next_task:
        st.markdown(
            f"""
            <div style="background-color: #cff4fc; border-left: 8px solid #055160; padding: 22px; border-radius: 12px; margin-top: 10px;">
                <h2 style="color: #055160; margin:0;">☕ 下一项日程：{next_task['title']}</h2>
                <h4 style="color: #055160; margin-top:8px;">🕒 时间：{next_task['time']}</h4>
                <p style="color: #055160; font-size: 15px; margin-bottom:0;">{next_task['notes']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.success(f"🎉 今天（{today_str}）当前无正在进行或下一项日程！")

    day_courses = sch.get_day_schedule(st.session_state, today_str)
    day_customs = [
        t
        for t in st.session_state.custom_tasks
        if t["day"] == today_str and t.get("week") == st.session_state.tab1_week
    ]
    all_today = sorted(day_courses + day_customs, key=lambda x: x["time"].split(" - ")[0])

    remaining_tasks = [t for t in all_today if not main_task or t["id"] != main_task["id"]]

    active_yellow_tasks = []
    ended_gray_tasks = []

    for task in remaining_tasks:
        is_custom = task.get("is_custom", False)
        is_completed = task.get("completed", False)
        passed = is_time_passed(task["time"])

        if is_custom:
            if is_completed:
                ended_gray_tasks.append((task, "completed"))
            else:
                active_yellow_tasks.append(task)
        else:
            if passed:
                ended_gray_tasks.append((task, "time_passed"))
            else:
                active_yellow_tasks.append(task)

    if active_yellow_tasks:
        st.markdown(
            "<br><span style='font-size:15px; font-weight:bold; color:#d97706;'>📅 今日未完成 / 待进行日程：</span>",
            unsafe_allow_html=True,
        )
        for task in active_yellow_tasks:
            is_custom = task.get("is_custom", False)
            if is_custom:
                col_t, col_btn = st.columns([5, 1])
                with col_t:
                    st.markdown(
                        f"""
                        <div style="background-color: #fffbeb; border-left: 4px solid #f59e0b; padding: 8px 12px; border-radius: 6px; margin-bottom: 4px;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span style="color: #b45309; font-weight: bold; font-size: 14px;">{task['title']}</span>
                                <span style="color: #d97706; font-size: 12px;">🕒 {task['time']}</span>
                            </div>
                            <div style="color: #78350f; font-size: 12px;">📍 {task['notes']}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with col_btn:
                    if st.button("✅ 完成", key=f"btn_done_{task['id']}"):
                        task["completed"] = True
                        if task.get("steps"):
                            for s in task["steps"]:
                                s["done"] = True
                        tm.save_tasks(st.session_state.custom_tasks)
                        st.rerun()
            else:
                st.markdown(
                    f"""
                    <div style="background-color: #fffbeb; border-left: 4px solid #f59e0b; padding: 8px 12px; border-radius: 6px; margin-bottom: 4px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="color: #b45309; font-weight: bold; font-size: 14px;">{task['title']}</span>
                            <span style="color: #d97706; font-size: 12px;">🕒 {task['time']}</span>
                        </div>
                        <div style="color: #78350f; font-size: 12px;">📍 {task['notes']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    if ended_gray_tasks:
        st.markdown(
            "<br><span style='font-size:13px; font-weight:bold; color:#9ca3af;'>已结束 / 已完成日程：</span>",
            unsafe_allow_html=True,
        )
        for task, reason in ended_gray_tasks:
            is_custom = task.get("is_custom", False)
            if is_custom and reason == "completed":
                col_c, col_undo = st.columns([5, 1])
                with col_c:
                    st.markdown(
                        f"""
                        <div style="background-color: #ffffff; border: 1px solid #e5e7eb; border-left: 4px solid #9ca3af; padding: 5px 10px; border-radius: 6px; margin-bottom: 4px;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span style="color: #9ca3af; text-decoration: line-through; font-size: 13px;">{task['title']}</span>
                                <span style="color: #d1d5db; font-size: 11px;">🕒 {task['time']}</span>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with col_undo:
                    if st.button("↩️ 撤销", key=f"btn_undo_{task['id']}"):
                        task["completed"] = False
                        tm.save_tasks(st.session_state.custom_tasks)
                        st.rerun()
            else:
                st.markdown(
                    f"""
                    <div style="background-color: #ffffff; border: 1px solid #e5e7eb; border-left: 4px solid #d1d5db; padding: 5px 10px; border-radius: 6px; margin-bottom: 4px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="color: #9ca3af; text-decoration: line-through; font-size: 13px;">{task['title']}</span>
                            <span style="color: #d1d5db; font-size: 11px;">🕒 {task['time']} (已结束)</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
