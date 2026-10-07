import os
import json

DATA_FILE = "custom_tasks.json"
SETTINGS_FILE = "user_settings.json"

DEFAULT_SETTINGS = {
    "work_start_hour": 9,
    "work_end_hour": 21,
}

def load_tasks():
    """从本地文件读取任务列表（保障刷新和重启后数据不丢失）"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_tasks(tasks):
    """保存任务列表到本地文件"""
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(tasks, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"保存任务失败: {e}")

def add_task(st_session, task_data):
    """添加新任务并同步到 session_state 与本地文件"""
    tasks = load_tasks()
    tasks.append(task_data)
    save_tasks(tasks)
    st_session.custom_tasks = tasks

def update_task(st_session, updated_task):
    """更新已存在的任务并同步到 session_state 与本地文件"""
    tasks = load_tasks()
    for idx, t in enumerate(tasks):
        if t.get("id") == updated_task.get("id"):
            tasks[idx] = updated_task
            break
    save_tasks(tasks)
    st_session.custom_tasks = tasks

def delete_task(st_session, task_id):
    """删除任务并同步到 session_state 与本地文件"""
    tasks = load_tasks()
    tasks = [t for t in tasks if t.get("id") != task_id]
    save_tasks(tasks)
    st_session.custom_tasks = tasks

def sync_tasks(st_session):
    """强制重新从文件装载数据到 session_state（用于页面顶层同步）"""
    st_session.custom_tasks = load_tasks()


def load_user_settings():
    """读取用户设置，缺失字段自动补默认值。"""
    settings = dict(DEFAULT_SETTINGS)
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                loaded = json.load(f)
            if isinstance(loaded, dict):
                settings.update(loaded)
        except Exception:
            pass
    return settings


def save_user_settings(settings):
    """保存用户设置到本地文件。"""
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存用户设置失败: {e}")


def sync_user_settings(st_session):
    """同步用户设置到 session_state。"""
    st_session.user_settings = load_user_settings()


def update_work_time(st_session, start_hour, end_hour):
    """更新并持久化工作时间设置。"""
    settings = dict(getattr(st_session, "user_settings", load_user_settings()))
    settings["work_start_hour"] = int(start_hour)
    settings["work_end_hour"] = int(end_hour)
    save_user_settings(settings)
    st_session.user_settings = settings
