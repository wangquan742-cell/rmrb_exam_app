# 人民日报考公考编学习助手 V7.1 三篇超详细精读 + 手机一键复制任务版

V7.1 保持纯 ChatGPT 半自动模式：不接 OpenAI API，不接 DeepSeek API，不需要任何 API Key。入口文件仍然是 `app.py`，保留 Streamlit Cloud 公网部署能力、`APP_PASSWORD` 访问密码逻辑、手机快速模式、电脑完整模式和逻辑填空积累模块。

## 一、核心逻辑

1. Top10 是候选池：每天最多筛选10篇文章，方便判断当天素材范围。
2. 默认只精读3篇：深度精读篇数可选2、3、5，默认3篇。
3. 不平均分析10篇：宁可只分析3篇，也不要浅分析10篇。
4. Word、Markdown、复制任务文本都围绕深度精读文章生成。
5. Excel 仍保留 Top10 候选池、申论素材、面试题库、逻辑填空等表格。

## 二、手机端推荐流程

1. 手机浏览器打开公网网址。
2. 输入访问密码。
3. 选择日期、版面和深度精读篇数。
4. 点击“开始抓取”。
5. 复制“完整精读任务”。
6. 点击“打开 ChatGPT”。
7. 在 ChatGPT 对话框中粘贴并发送。
8. ChatGPT 按深度文章分别生成 Word，并打包 zip 返回。

说明：由于浏览器安全限制，网站不能自动替用户上传文件到 ChatGPT，也不能自动替用户点击发送。当前最佳流程是：复制任务 → 打开 ChatGPT → 粘贴发送。

## 三、深度精读输出标准

每篇精读文章都要求像用户单独发送一个人民日报网址一样详细分析，必须包含：

1. 原文内容精讲：让我不看原文也知道文章讲什么。
2. 段落结构精拆：背景、问题、原因、对策、递进、让步、总结。
3. 政策背景和深层逻辑：讲清为什么人民日报要写这篇文章。
4. 申论素材转化：给出可直接写进申论的案例、分论点、规范表达。
5. 面试迁移：题型、关键词拆解、帽子怎么想、开口第一句、答题路线。
6. 行测篇章阅读训练：主旨句、意图判断、逻辑词、迷惑项设置。
7. 逻辑填空积累：高频实词、固定搭配、近义词辨析、语境关系、仿真题、错项解析。
8. 金句和规范表达。

## 四、本地启动

```bash
cd rmrb_exam_app
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## 五、设置访问密码

### 本地方式

```bash
export APP_PASSWORD="你自己的密码"
streamlit run app.py
```

### Streamlit Cloud 方式

部署后，在 Streamlit Cloud 的 App Settings / Secrets 中填写：

```toml
APP_PASSWORD = "你自己的密码"
```

如果不配置 `APP_PASSWORD`，App 默认不启用密码。

## 六、部署到公网

详见：

```text
DEPLOY_TO_PUBLIC_WEB.md
PUBLIC_DEPLOY_CHECKLIST.md
```
