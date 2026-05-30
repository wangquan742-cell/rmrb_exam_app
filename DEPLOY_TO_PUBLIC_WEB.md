# V7.1 部署成公网网址完整说明

## 一、推荐方案：Streamlit Community Cloud

它适合这个项目，因为：
- 不需要自己买服务器
- 适合 Python + Streamlit 项目
- 可以生成公网网址
- iPhone 可以直接访问

## 二、部署前文件结构

你的 GitHub 仓库根目录应该类似：

```text
rmrb_exam_app/
├── app.py
├── ai_utils.py
├── rmrb_fetcher.py
├── excel_utils.py
├── docx_utils.py
├── requirements.txt
├── README.md
├── DEPLOY_TO_PUBLIC_WEB.md
├── PUBLIC_DEPLOY_CHECKLIST.md
└── .streamlit/
    ├── config.toml
    └── secrets.toml.example
```

不要上传：

```text
.venv/
__pycache__/
真实 secrets.toml
```

## 三、部署步骤

1. 上传代码到 GitHub
2. 打开 Streamlit Community Cloud
3. Create app
4. 选择仓库
5. Main file path 填 `app.py`
6. Deploy

## 四、设置密码

在 Streamlit Cloud 的 Secrets 里填：

```toml
APP_PASSWORD = "你自己的密码"
```

保存后重启。

## 五、手机使用

iPhone Safari 打开：

```text
https://你的项目名.streamlit.app
```

输入密码后即可使用。

## 六、后续可以升级的功能

V7.1 可继续做：
1. 登录页更美观
2. 每日历史记录
3. 自动保存 Markdown 到云端
4. 一键复制提示词
5. 管理员后台
6. 自动生成每日学习包索引
