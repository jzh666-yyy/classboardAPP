import streamlit as st


def render_global_styles():
    st.markdown(
        """
        <style>

        .main .block-container {
            padding-top: 1.5rem !important;
            padding-bottom: 1rem !important;
        }
        .stTabs [aria-selected="true"] {
            background-color: #2563eb !important;
            color: white !important;
        }

        /* 焦点页：当前任务绿色卡片（可点击） */
        div[class*="st-key-current_task_card_"] button {
            width: 100%;
            text-align: left;
            white-space: pre-line;
            background-color: #d1e7dd !important;
            color: #0f5132 !important;
            border-left: 8px solid #0f5132 !important;
            border-top: 1px solid #b8d9cb !important;
            border-right: 1px solid #b8d9cb !important;
            border-bottom: 1px solid #b8d9cb !important;
            border-radius: 12px !important;
            padding: 16px !important;
            min-height: 110px;
            box-shadow: none !important;
            font-size: 16px !important;
            line-height: 1.45 !important;
            font-weight: 700 !important;
        }
        div[class*="st-key-current_task_card_"] button:hover {
            background-color: #c4e1d2 !important;
            border-left-color: #0c3f28 !important;
        }

        /* 本周课表：自定义任务卡片可点击（点框即编辑） */
        div[class*="st-key-grid_task_card_"] button {
            width: 100%;
            min-height: 38px;
            text-align: left;
            white-space: pre-line;
            background-color: #fef3c7 !important;
            color: #92400e !important;
            border: 1px solid #f59e0b !important;
            border-radius: 6px !important;
            padding: 6px 6px !important;
            box-shadow: none !important;
            font-size: 11px !important;
            line-height: 1.25 !important;
        }
        div[class*="st-key-grid_task_card_"] button:hover {
            background-color: #fde68a !important;
            border-color: #d97706 !important;
        }

        div[class*="st-key-grid_task_done_"] button {
            width: 100%;
            min-height: 38px;
            text-align: left;
            white-space: pre-line;
            background-color: #f3f4f6 !important;
            color: #9ca3af !important;
            border: 1px solid #d1d5db !important;
            border-radius: 6px !important;
            padding: 6px 6px !important;
            box-shadow: none !important;
            font-size: 11px !important;
            line-height: 1.25 !important;
        }

        .grid-time-cell {
            min-height: 38px;
            display: flex;
            align-items: center;
            justify-content: flex-start;
        }

        .grid-occupied-cell {
            min-height: 38px;
            background-color: #f8fafc;
            border-left: 2px solid #bfdbfe;
            border-radius: 4px;
            margin-bottom: 2px;
        }

        .grid-empty-cell {
            min-height: 38px;
            border: 1px dashed #e5e7eb;
            border-radius: 4px;
            background: #ffffff;
            margin: 0;
        }

        /* 添加任务按钮：默认透明，悬浮时再提示，可避免界面过密 */
        div[class*="st-key-btn_add_"] button,
        div[class*="st-key-btn_add_occ_"] button,
        div[class*="st-key-btn_add_stack_"] button {
            min-height: 38px;
            width: 100%;
            border: 1px dashed transparent !important;
            border-radius: 6px !important;
            background: transparent !important;
            color: transparent !important;
            box-shadow: none !important;
            padding: 0 !important;
            font-size: 0 !important;
        }
        div[class*="st-key-btn_add_"] button:hover,
        div[class*="st-key-btn_add_occ_"] button:hover,
        div[class*="st-key-btn_add_stack_"] button:hover {
            border: 1px dashed #93c5fd !important;
            background: #eff6ff !important;
            color: #3b82f6 !important;
        }

        /* 空白格添加按钮悬浮效果 */
        .blank-slot-btn {
            width: 100%;
            height: 42px;
            border-radius: 6px;
            border: 1px dashed transparent;
            background-color: transparent;
            color: transparent;
            font-size: 11px;
            transition: all 0.2s ease-in-out;
            cursor: pointer;
        }
        .blank-slot-btn:hover {
            border: 1px dashed #93c5fd !important;
            background-color: #eff6ff !important;
            color: #3b82f6 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
