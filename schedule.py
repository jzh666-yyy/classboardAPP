import json
import os
import datetime
from config import BASE_SCHEDULE, TIME_SLOTS, WEEK_DAYS

TASKS_FILE = "custom_tasks.json"

# -----------------------------------------------------------------------------
# 自定义任务的持久化保存/读取
# -----------------------------------------------------------------------------
def load_custom_tasks():
    if os.path.exists(TASKS_FILE):
        try:
            with open(TASKS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_custom_tasks(custom_tasks):
    try:
        with open(TASKS_FILE, "w", encoding="utf-8") as f:
            json.dump(custom_tasks, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存自定义任务失败: {e}")

# -----------------------------------------------------------------------------
# 初始化 Session State
# -----------------------------------------------------------------------------
def init_schedule(session_state):
    if "current_week" not in session_state:
        session_state.current_week = 1
    if "custom_tasks" not in session_state:
        session_state.custom_tasks = load_custom_tasks()

def switch_week(session_state, new_week):
    session_state.current_week = new_week

# -----------------------------------------------------------------------------
# 课表与任务查询
# -----------------------------------------------------------------------------
def get_day_schedule_by_week(week_num, day_str):
    day_courses = []
    
    for course in BASE_SCHEDULE:
        if course["day"] == day_str and week_num in course["weeks"]:
            t_start = TIME_SLOTS[course["slots"][0] - 1]["time"].split("-")[0]
            t_end = TIME_SLOTS[course["slots"][-1] - 1]["time"].split("-")[1]
            
            day_courses.append({
                "id": f"course_{course['title']}_{day_str}_{course['slots'][0]}",
                "title": f"📘 {course['title']}",
                "category": "📚 基础课程",
                "time": f"{t_start} - {t_end}",
                "slots": course["slots"],
                "notes": course["location"],
                "is_custom": False,
                "steps": []
            })
    return day_courses


def get_day_schedule(session_state, day_str):
    curr_w = session_state.current_week
    return get_day_schedule_by_week(curr_w, day_str)

def get_current_focus_task(session_state):
    weekday_idx = datetime.datetime.now().weekday()
    if weekday_idx >= len(WEEK_DAYS):
        today_str = WEEK_DAYS[0]
    else:
        today_str = WEEK_DAYS[weekday_idx]
        
    day_courses = get_day_schedule(session_state, today_str)
    day_customs = [
        t for t in session_state.custom_tasks 
        if t["day"] == today_str and t.get("week") == session_state.current_week and not t.get("completed", False)
    ]
    
    all_tasks = sorted(day_courses + day_customs, key=lambda x: x["time"].split(" - ")[0])
    now_time = datetime.datetime.now().time()
    
    curr_task = None
    next_task = None
    
    for task in all_tasks:
        try:
            start_str, end_str = task["time"].split(" - ")
            start_t = datetime.datetime.strptime(start_str.strip(), "%H:%M").time()
            end_t = datetime.datetime.strptime(end_str.strip(), "%H:%M").time()
            
            if start_t <= now_time <= end_t:
                curr_task = task
                break
            elif now_time < start_t:
                if next_task is None:
                    next_task = task
        except Exception:
            continue
            
    return today_str, curr_task, next_task

def update_task_steps(task, steps_text):
    lines = [line.strip() for line in steps_text.split("\n") if line.strip()]
    task["steps"] = [{"step": line, "done": False} for line in lines]
