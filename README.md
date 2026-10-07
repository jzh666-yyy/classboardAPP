# my_dashboard

一个基于 Streamlit 的个人任务/课表面板。

## 本地运行

1. 安装依赖

```bash
pip install -r requirements.txt
```

2. 启动

```bash
streamlit run app.py
```

## 公网部署（推荐：Streamlit Community Cloud）

1. 将项目上传到 GitHub 仓库。
2. 打开 Streamlit Community Cloud：
   - https://share.streamlit.io/
3. 点击 `New app`，选择你的 GitHub 仓库。
4. `Main file path` 填 `app.py`。
5. 点击 `Deploy`。
6. 部署成功后得到公网链接，直接发给朋友即可。

## 注意

- `custom_tasks.json`、`user_settings.json`、`current_week.json` 已在 `.gitignore` 中，默认不会上传你的本地私人数据。
- 如果你希望朋友访问时看到初始示例数据，可以手动准备一个示例 `custom_tasks.example.json` 并在应用启动时复制为运行数据文件。
