import streamlit as st
import streamlit.components.v1 as components
import datetime

import schedule as sch
import task_manager as tm
from config import TIME_SLOTS


def _render_live_clock_in_dialog():
    components.html(
        """
        <div style="display:flex; justify-content:center; margin: 2px 0 8px 0;">
            <div style="
                min-width: 200px;
                text-align:center;
                padding:8px 12px;
                border-radius:12px;
                border:2px solid #1d4ed8;
                background:linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
                box-shadow:0 4px 14px rgba(29, 78, 216, 0.2);
                font-family:'JetBrains Mono', 'Consolas', monospace;
                color:#0b3b8f;
                font-weight:800;
                letter-spacing:1px;
                line-height:1;
            ">
                <div style="font-size:12px; opacity:0.9; margin-bottom:5px;">当前时间</div>
                <div id="dialog-live-clock" style="font-size:30px;">--:--:--</div>
            </div>
        </div>
        <script>
            function pad(n) { return String(n).padStart(2, '0'); }
            function tick() {
                const d = new Date();
                const t = `${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
                const el = document.getElementById('dialog-live-clock');
                if (el) el.textContent = t;
            }
            tick();
            setInterval(tick, 1000);
        </script>
        """,
        height=90,
    )


@st.dialog("🟢 当前任务详情")
def show_current_task_dialog(task):
    _render_live_clock_in_dialog()
    st.markdown(
        f"""
        <div style="background-color:#d1e7dd; border-left:8px solid #0f5132; padding:16px; border-radius:10px; margin-top:4px;">
            <div style="color:#0f5132; font-size:20px; font-weight:800;">{task.get('title', '未命名任务')}</div>
            <div style="color:#0f5132; font-size:14px; margin-top:6px;">🕒 {task.get('time', '')}</div>
            <div style="color:#0f5132; font-size:14px; margin-top:2px;">📍 {task.get('notes', '无备注')}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if task.get("steps"):
        st.markdown("#### 📋 当前任务清单")
        for step in task.get("steps", []):
            marker = "✅" if step.get("done") else "⬜"
            st.write(f"{marker} {step.get('step', '')}")


@st.dialog("⚙️ 调整 Tab 1 当前周次")
def change_tab1_week_dialog():
    st.write("调整【此时此刻】焦点的查看周次：")
    new_w = st.number_input(
        "选择当前周次",
        min_value=1,
        max_value=20,
        value=st.session_state.tab1_week,
        step=1,
    )
    if st.button("💾 确认更改周次", use_container_width=True, type="primary"):
        st.session_state.tab1_week = new_w
        st.success(f"已成功切换至 第 {new_w} 周！")
        st.rerun()


@st.dialog("✏️ 编辑任务 / 课程")
def edit_task_dialog(task):
    with st.form(f"dialog_edit_{task['id']}"):
        new_title = st.text_input("名称", value=task["title"])
        new_notes = st.text_area("地点 / 备注", value=task["notes"])
        steps_text = "\n".join([s["step"] for s in task.get("steps", [])])
        new_steps_text = st.text_area(
            "Checklist 执行清单（一行一步）", value=steps_text, height=100
        )

        col_a, col_b = st.columns(2)
        with col_a:
            if st.form_submit_button("💾 保存修改", use_container_width=True):
                task["title"] = new_title
                task["notes"] = new_notes
                sch.update_task_steps(task, new_steps_text)

                if task.get("is_custom"):
                    tm.update_task(st.session_state, task)

                st.success("保存成功！")
                st.rerun()
        with col_b:
            if task.get("is_custom", False):
                if st.form_submit_button("🗑️ 删除任务", use_container_width=True, type="primary"):
                    tm.delete_task(st.session_state, task["id"])
                    st.success("任务已删除！")
                    st.rerun()


@st.dialog("➕ 在无课时段新增任务")
def add_custom_task_dialog(day, slot_num):
    slot_info = TIME_SLOTS[slot_num - 1]
    slot_start_str, slot_end_str = [x.strip() for x in slot_info["time"].split("-")]
    slot_start_time = datetime.datetime.strptime(slot_start_str, "%H:%M").time()
    slot_end_time = datetime.datetime.strptime(slot_end_str, "%H:%M").time()
    st.info(
        f"📅 安排时间：**{day} 第 {slot_num} 节 ({slot_info['time']})** | "
        f"**第 {st.session_state.tab2_week} 周**"
    )

    def infer_slots_by_time(start_t, end_t):
        matched = []
        for slot in TIME_SLOTS:
            s_start_str, s_end_str = [x.strip() for x in slot["time"].split("-")]
            s_start = datetime.datetime.strptime(s_start_str, "%H:%M").time()
            s_end = datetime.datetime.strptime(s_end_str, "%H:%M").time()
            if s_end > start_t and s_start < end_t:
                matched.append(slot["slot"])
        return matched

    with st.form(f"dialog_add_{day}_{slot_num}"):
        title = st.text_input("任务名称", placeholder="例如：写研究生论文 / 实验室做实验 / 自习")
        notes = st.text_input("地点 / 备注", placeholder="例如：图书馆3楼 / 501实验室")
        free_time_mode = st.toggle("自定义时间范围（不限节次）", value=True)

        if free_time_mode:
            t_start = st.time_input("开始时间", value=slot_start_time, step=300)
            t_end = st.time_input("结束时间", value=slot_end_time, step=300)
            duration_slots = None
        else:
            duration_slots = st.number_input(
                "持续节数", min_value=1, max_value=6, value=1, help="按节次连续占用"
            )
            t_start = None
            t_end = None
        steps_raw = st.text_area(
            "Checklist 清单 (可选，一行一项)", placeholder="读取文献\n整理数据"
        )

        if st.form_submit_button("确认添加", use_container_width=True):
            if not title.strip():
                st.error("请输入任务名称！")
            else:
                if free_time_mode:
                    if t_end <= t_start:
                        st.error("结束时间必须晚于开始时间")
                        return
                    start_str = t_start.strftime("%H:%M")
                    end_str = t_end.strftime("%H:%M")
                    slots_range = infer_slots_by_time(t_start, t_end)
                else:
                    end_slot = min(15, slot_num + int(duration_slots) - 1)
                    slots_range = list(range(slot_num, end_slot + 1))
                    start_str = TIME_SLOTS[slot_num - 1]["time"].split("-")[0].strip()
                    end_str = TIME_SLOTS[end_slot - 1]["time"].split("-")[1].strip()

                steps = [
                    {"step": line.strip(), "done": False}
                    for line in steps_raw.split("\n")
                    if line.strip()
                ]

                new_task = {
                    "id": f"custom_{day}_{st.session_state.tab2_week}_{slot_num}_{len(st.session_state.custom_tasks)}",
                    "day": day,
                    "week": st.session_state.tab2_week,
                    "slots": slots_range,
                    "time": f"{start_str} - {end_str}",
                    "title": f"📌 {title}",
                    "category": "📝 自定义任务",
                    "notes": notes if notes else "无备注",
                    "steps": steps,
                    "is_custom": True,
                    "completed": False,
                }

                tm.add_task(st.session_state, new_task)
                st.success("任务添加成功并已保存！")
                st.rerun()
