# 人民日报考公考编学习助手 V6.1 公网部署增强版

V6.1 是“一步到位”公网部署版本。

## 一、这个版本解决什么问题

1. 取消 OpenAI API
2. 取消 DeepSeek API
3. 不需要任何 API Key
4. 只保留 ChatGPT 半自动路线
5. 每天最多筛选 10 篇精品文章
6. 自动生成带完整指令的 Markdown 分析包
7. Markdown 内置要求：ChatGPT 解析后，每篇文章单独生成 Word，最后打包 zip 返回
8. 支持部署到公网，iPhone Safari 可以直接打开
9. 增加访问密码能力，避免公网网址被别人随便使用
10. 页面做了手机端适配

## 二、本地启动

```bash
cd ~/Downloads/个人学习项目/rmrb_exam_app
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

然后保存并重启 App。

如果不配置 `APP_PASSWORD`，App 默认不启用密码。

## 四、手机端使用流程

1. iPhone Safari 打开公网网址
2. 输入访问密码
3. 选择日期和版面
4. 点击“开始抓取”
5. 下载 Markdown 分析包
6. 分享到 ChatGPT App
7. 对 ChatGPT 说：按分析包执行
8. ChatGPT 解析后，每篇文章单独生成 Word，并打包 zip 返回

## 五、部署到公网

详见：

```text
DEPLOY_TO_PUBLIC_WEB.md
PUBLIC_DEPLOY_CHECKLIST.md
```
