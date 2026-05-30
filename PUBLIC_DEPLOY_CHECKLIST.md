# V6.2 公网部署一站式清单

## 目标

把人民日报考公考编学习助手部署成一个手机可以打开的网址，例如：

```text
https://rmrb-exam-app-xxx.streamlit.app
```

## 第 1 步：准备 GitHub 仓库

1. 打开 GitHub
2. New repository
3. 仓库名建议：

```text
rmrb_exam_app
```

4. 选择 Private 或 Public 都可以。个人学习建议 Private。
5. 创建仓库。

## 第 2 步：上传 V6.2 文件

把 V6.2 文件夹里的内容全部上传。

必须包含：

```text
app.py
requirements.txt
ai_utils.py
rmrb_fetcher.py
excel_utils.py
docx_utils.py
README.md
DEPLOY_TO_PUBLIC_WEB.md
PUBLIC_DEPLOY_CHECKLIST.md
.streamlit/config.toml
```

注意：

```text
不要上传 .venv 文件夹
不要上传真实 secrets.toml
不要上传带有个人密码的文件
```

## 第 3 步：Streamlit Cloud 创建 App

1. 打开 Streamlit Community Cloud
2. New app / Create app
3. 选择 GitHub 仓库
4. Branch 选择 main
5. Main file path 填：

```text
app.py
```

6. 点击 Deploy

## 第 4 步：设置访问密码

进入 App Settings / Secrets，填写：

```toml
APP_PASSWORD = "你自己的密码"
```

保存后重启 App。

## 第 5 步：手机打开

部署成功后获得网址，例如：

```text
https://rmrb-exam-app-xxxx.streamlit.app
```

iPhone Safari 打开这个网址，输入访问密码即可使用。

## 第 6 步：每日使用流程

1. 选择日期
2. 选择 01—05 或 01—10 版
3. 开始抓取
4. 下载精品 Markdown 分析包
5. 分享到 ChatGPT App
6. 对 ChatGPT 说：按分析包执行
7. 等待 ChatGPT 返回 Word 压缩包

## 常见问题

### 1. 页面打不开

可能原因：
- Streamlit Cloud 还在部署
- 依赖安装失败
- GitHub 文件没上传完整

检查：
- 查看 Streamlit Cloud 日志
- 确认 requirements.txt 在根目录
- 确认 app.py 在根目录

### 2. 抓不到当天文章

可能原因：
- 当天人民日报电子版还没有更新
- 日期不对
- 版面还没生成

处理：
- 先用昨天日期测试
- 版面选择 01—05
- 最低考公价值分设为 0

### 3. 手机上下载 Markdown 不方便

处理：
- 用 Safari 打开网页
- 点击下载 Markdown
- 选择分享
- 分享到 ChatGPT App 或保存到文件

### 4. 不想别人访问

一定要设置 APP_PASSWORD。
不要把网址公开发到群里。
