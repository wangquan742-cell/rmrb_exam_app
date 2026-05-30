# 人民日报考公考编学习助手 V6.2 手机体验 + 逻辑填空积累版

V6.2 保持纯 ChatGPT 半自动模式：不接 OpenAI API，不接 DeepSeek API，不需要任何 API Key。入口文件仍然是 `app.py`，保留 Streamlit Cloud 公网部署能力和 `APP_PASSWORD` 访问密码逻辑。

## 一、这个版本新增什么

1. 手机快速模式：手机端优先下载 Markdown 分析包，减少表格和 Word 干扰。
2. 电脑完整模式：保留 Excel、Word、Markdown 全部下载按钮和完整表格预览。
3. 一键复制 ChatGPT 指令：上传 Markdown 后直接复制页面指令给 ChatGPT。
4. 抓取失败中文提示：优先提示日期未更新、版面不存在、网络异常、页面结构变化等原因。
5. Markdown 内置逻辑填空积累要求：高频实词、规范搭配、成语/四字格、近义词辨析、语境关系、仿真题、答案、错项解析、今日必背搭配。
6. ChatGPT 解析后按文章生成 Word，并把所有 Word 打包成 zip 返回。
7. 保留每日精品 Top10 筛选逻辑。

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
4. 点击“开始抓取”。
5. 下载 V6.2 精品 Markdown 分析包。
6. 上传到 ChatGPT App。
7. 对 ChatGPT 说“按分析包执行”，或复制页面里的完整指令。
8. ChatGPT 解析后，每篇文章单独生成 Word，并打包 zip 返回。

## 五、部署到公网

详见：

```text
DEPLOY_TO_PUBLIC_WEB.md
PUBLIC_DEPLOY_CHECKLIST.md
```
