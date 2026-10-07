import streamlit as st

import schedule as sch
import task_manager as tm
from ui_dialogs import (
    add_custom_task_dialog,
    change_tab1_week_dialog,
    edit_task_dialog,
    show_current_task_dialog,
)
from ui_focus_tab import render_focus_tab
from ui_grid_tab import render_grid_tab
from ui_styles import render_global_styles


st.set_page_config(page_title="研究生个人调度系统", page_icon="🎓", layout="wide")


# 初始化 Tab1 和 Tab2 独立的周次状态
if "tab1_week" not in st.session_state:
    st.session_state.tab1_week = getattr(st.session_state, "current_week", 3)
if "tab2_week" not in st.session_state:
    st.session_state.tab2_week = getattr(st.session_state, "current_week", 3)

sch.init_schedule(st.session_state)
# 从文件同步数据到 session_state
tm.sync_tasks(st.session_state)

# 全局样式
render_global_styles()

# Tab 布局
# 保留变量引用，确保 Streamlit 的 tab 容器上下文正确建立。
tab_focus, tab_grid = st.tabs(["此刻", "本周"])

with tab_focus:
    render_focus_tab(change_tab1_week_dialog, show_current_task_dialog)

with tab_grid:
    render_grid_tab(edit_task_dialog, add_custom_task_dialog)
