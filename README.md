# 人民日报考公考编学习助手 V7 Top10候选 + 2—3篇超详细精读版

V7 保持纯 ChatGPT 半自动模式：不接 OpenAI API，不接 DeepSeek API，不需要任何 API Key。入口文件仍然是 `app.py`，保留 Streamlit Cloud 公网部署能力、`APP_PASSWORD` 访问密码逻辑、手机快速模式、电脑完整模式和逻辑填空积累模块。

## 一、这个版本新增什么

1. 保留每日抓取 Top10 候选文章，作为当天素材池。
2. 新增“深度精读篇数”选项，默认3篇，可在2—3篇之间选择。
3. Markdown 明确说明：Top10只是候选，不要平均分析全部文章。
4. 每篇深度文章单独生成任务块，要求像用户单独发送一个网址一样详细分析。
5. 强化提示词：原文内容精讲、段落结构精拆、政策背景和深层逻辑、申论可用素材、面试迁移和开口思路、行测篇章阅读结构、逻辑填空积累、金句和规范表达。
6. 页面新增“使用说明”折叠按钮，解释手机快速模式、电脑完整模式、Top10候选、深度精读篇数和 Markdown 使用方法。
7. ChatGPT 解析后按深度文章分别生成 Word，并把所有 Word 打包成 zip 返回。

## 二、本地启动

```bash
cd rmrb_exam_app
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## 三、设置访问密码

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

## 四、手机端使用流程

1. 手机浏览器打开公网网址。
2. 输入访问密码。
3. 选择日期和版面。
4. 设置深度精读篇数，默认3篇。
5. 点击“开始抓取”。
6. 下载 V7 Markdown 分析包。
7. 上传到 ChatGPT App。
8. 对 ChatGPT 说“按分析包执行”，或复制页面里的完整指令。
9. ChatGPT 只对前2—3篇深度文章做超详细精读，并按文章生成 Word 打包 zip 返回。

## 五、部署到公网

详见：

```text
DEPLOY_TO_PUBLIC_WEB.md
PUBLIC_DEPLOY_CHECKLIST.md
```
