import csv
import datetime
import io

import streamlit as st


def is_time_passed(time_str):
    try:
        now = datetime.datetime.now().time()
        end_str = time_str.split(" - ")[1].strip()
        end_time = datetime.datetime.strptime(end_str, "%H:%M").time()
        return now > end_time
    except Exception:
        return False


def duration_minutes(time_str):
    """解析形如 HH:MM - HH:MM 的时长，解析失败返回 0。"""
    try:
        parts = [p.strip() for p in time_str.split("-")]
        if len(parts) != 2:
            return 0
        start_t = datetime.datetime.strptime(parts[0], "%H:%M")
        end_t = datetime.datetime.strptime(parts[1], "%H:%M")
        return max(0, int((end_t - start_t).total_seconds() // 60))
    except Exception:
        return 0


def task_status_label(task, now_time):
    """生成任务状态标签：进行中 / 待开始 / 已结束 / 已完成。"""
    if task.get("is_custom") and task.get("completed"):
        return "已完成"

    try:
        start_str, end_str = [x.strip() for x in str(task.get("time", "")).split("-")]
        start_t = datetime.datetime.strptime(start_str, "%H:%M").time()
        end_t = datetime.datetime.strptime(end_str, "%H:%M").time()
    except Exception:
        return "未知"

    if start_t <= now_time <= end_t:
        return "进行中"
    if now_time < start_t:
        return "待开始"
    return "已结束"


def build_today_report_rows(tasks, now_time):
    """将今日任务转换为可展示/导出的表格行。"""
    rows = []
    for idx, task in enumerate(tasks, start=1):
        rows.append(
            {
                "序号": idx,
                "时间": task.get("time", ""),
                "任务": task.get("title", ""),
                "类型": "自定义" if task.get("is_custom") else "课程",
                "地点备注": task.get("notes", ""),
                "状态": task_status_label(task, now_time),
            }
        )
    return rows


def rows_to_csv_text(rows):
    """把表格行序列化为 CSV 文本（UTF-8 BOM 由下载按钮处理）。"""
    if not rows:
        return "序号,时间,任务,类型,地点备注,状态\n"

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


def calc_today_learning_summary(session_state, day_str, week_num):
    """统计当天四个模块的分钟数。"""
    summaries = {
        "cet4": 0,
        "uav": 0,
        "paper": 0,
        "sport": 0,
    }

    today_custom_tasks = [
        t for t in session_state.custom_tasks
        if t.get("day") == day_str and t.get("week") == week_num
    ]

    for task in today_custom_tasks:
        title = str(task.get("title", ""))
        mins = duration_minutes(str(task.get("time", "")))

        if "四级" in title:
            summaries["cet4"] += mins
        elif "无人机" in title:
            summaries["uav"] += mins
        elif "文献" in title:
            summaries["paper"] += mins
        elif "体育" in title or "锻炼" in title:
            summaries["sport"] += mins

    return summaries


def render_goal_card(label, mins, low_target, high_target=None):
    """渲染单个目标卡片并返回状态文本。"""
    if high_target is None:
        high_target = low_target

    if mins < low_target:
        status = "未达标"
        tone_bg = "#fff7ed"
        tone_border = "#fdba74"
        tone_text = "#9a3412"
    elif mins > high_target:
        status = "超出建议"
        tone_bg = "#f0fdf4"
        tone_border = "#86efac"
        tone_text = "#166534"
    else:
        status = "已达标"
        tone_bg = "#eff6ff"
        tone_border = "#93c5fd"
        tone_text = "#1e3a8a"

    target_text = (
        f"目标 {low_target}min"
        if low_target == high_target
        else f"目标 {low_target}-{high_target}min"
    )
    st.markdown(
        f"""
        <div style="background:{tone_bg}; border:1px solid {tone_border}; border-radius:10px; padding:10px; min-height:88px;">
            <div style="font-size:12px; color:{tone_text}; opacity:0.95;">{label}</div>
            <div style="font-size:22px; color:{tone_text}; font-weight:700; line-height:1.1; margin-top:4px;">{mins} min</div>
            <div style="font-size:12px; color:{tone_text}; margin-top:3px;">{target_text} | {status}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
