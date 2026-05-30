from datetime import date
import os

import pandas as pd
import streamlit as st

from ai_utils import (
    CHATGPT_COPY_INSTRUCTION,
    build_chatgpt_markdown_package,
    build_chatgpt_package,
    build_prompt_first_sheet,
    build_prompt_sheet,
    build_task_code,
)
from docx_utils import create_article_docx_zip, create_combined_docx
from excel_utils import export_beautified_excel
from rmrb_fetcher import articles_to_dataframe, fetch_multiple_pages, make_study_sheets


def get_app_password():
    """
    V7 可选访问密码：
    1. Streamlit Cloud：在 Secrets 里配置 APP_PASSWORD
    2. 本地运行：可设置环境变量 APP_PASSWORD
    3. 如果都没配置，则默认不启用密码
    """
    try:
        if "APP_PASSWORD" in st.secrets:
            return str(st.secrets["APP_PASSWORD"])
    except Exception:
        pass
    return os.environ.get("APP_PASSWORD", "")


def require_password():
    password = get_app_password()
    if not password:
        return True

    st.markdown("### 🔐 访问验证")
    st.caption("这是你的个人学习工具，公网部署后建议开启访问密码。")

    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        return True

    user_input = st.text_input("请输入访问密码", type="password")
    if st.button("进入学习助手"):
        if user_input == password:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("密码不正确，请重新输入。")

    st.stop()


def parse_custom_pages(text: str):
    pages = []
    for part in text.replace("，", ",").split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start, end = part.split("-", 1)
            for i in range(int(start), int(end) + 1):
                pages.append(str(i).zfill(2))
        else:
            pages.append(str(int(part)).zfill(2))
    return list(dict.fromkeys(pages))


def select_best_articles(df: pd.DataFrame, max_articles: int = 10, min_score: int = 0) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()

    max_articles = min(int(max_articles), 10)
    result = df.copy()

    if "考公价值分" in result.columns:
        result = result[result["考公价值分"] >= min_score]
        result = result.sort_values(by=["考公价值分", "版面号"], ascending=[False, True])
    else:
        result = result.head(max_articles)

    return result.head(max_articles).copy()


def ensure_content_column(df: pd.DataFrame, articles):
    if df is None or df.empty:
        return pd.DataFrame()

    if "正文全文" not in df.columns:
        content_map = {a.url: a.content for a in articles}
        if "链接" in df.columns:
            df["正文全文"] = df["链接"].map(content_map).fillna("")
        else:
            df["正文全文"] = ""

    return df


st.set_page_config(
    page_title="人民日报考公学习助手 V7",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 1.2rem;
    }
    @media (max-width: 768px) {
        .block-container {
            padding-left: 0.8rem;
            padding-right: 0.8rem;
        }
        h1 {
            font-size: 1.45rem !important;
        }
        h2, h3 {
            font-size: 1.15rem !important;
        }
        .stButton button {
            width: 100%;
        }
        .stDownloadButton button {
            width: 100%;
            min-height: 3rem;
            font-size: 1rem;
            font-weight: 650;
        }
        div[data-testid="stMetricValue"] {
            font-size: 1.1rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

require_password()

st.title("📰 人民日报考公考编学习助手 V7")
st.caption("Top10候选 + 2—3篇超详细精读版：纯 ChatGPT 半自动、不接任何 AI API、不需要 API Key。")

st.markdown("### 今日使用流程")
flow_cols = st.columns(3)
flow_cols[0].markdown("**1. 选择日期和版面**  \n在侧边栏设置日期、版面范围和正文抓取。")
flow_cols[1].markdown("**2. 点击开始抓取**  \n系统自动筛选 Top10 候选文章。")
flow_cols[2].markdown("**3. 设置深度精读篇数**  \n默认只精读前3篇，不平均分析10篇。")
flow_cols = st.columns(3)
flow_cols[0].markdown("**4. 下载 Markdown 分析包**  \n手机端优先下载 Markdown。")
flow_cols[1].markdown("**5. 上传到 ChatGPT App**  \n对 ChatGPT 说“按分析包执行”。")
flow_cols[2].markdown("**6. 生成 Word 并打包 zip**  \nChatGPT 按深度文章分别返回 Word。")

st.info("手机端提示：推荐手机端优先下载 Markdown 分析包；Excel 和 Word 更适合电脑端使用。如果今天抓不到，可能当天还未更新，建议选择昨天日期。")

st.markdown("### 复制给 ChatGPT 的指令")
st.text_area("上传 Markdown 分析包后，复制这段话给 ChatGPT", value=CHATGPT_COPY_INSTRUCTION, height=150)
st.code(CHATGPT_COPY_INSTRUCTION, language="text")

with st.expander("使用说明"):
    st.markdown(
        """
        - 手机快速模式：突出 Markdown 下载按钮，表格预览更轻，适合手机端把分析包上传到 ChatGPT App。
        - 电脑完整模式：显示 Excel、Word、Markdown 全部下载按钮，并保留完整表格预览。
        - Top10候选：系统每天最多筛选10篇候选文章，作为今日素材池。
        - 深度精读篇数：默认3篇，只对候选池前2—3篇做超详细精读，避免把10篇文章平均分析得很浅。
        - Markdown使用方法：下载 V7 Markdown 分析包，上传到 ChatGPT App，然后复制页面里的指令；ChatGPT 会按深度任务块逐篇生成 Word，并打包 zip 返回。
        """
    )

if "df" not in st.session_state:
    st.session_state.df = None
if "best_df" not in st.session_state:
    st.session_state.best_df = None
if "current_task" not in st.session_state:
    st.session_state.current_task = ""
if "task_code" not in st.session_state:
    st.session_state.task_code = ""

with st.sidebar:
    st.header("抓取设置")

    usage_mode = st.radio(
        "使用模式",
        ["手机快速模式", "电脑完整模式"],
        help="手机快速模式突出 Markdown 下载；电脑完整模式显示完整表格和 Excel/Word/Markdown 下载。"
    )

    selected_date = st.date_input("选择日期", value=date.today())

    page_mode = st.radio(
        "选择版面范围",
        ["01—05 版", "01—10 版", "单版抓取", "自定义版面"],
    )

    page_no = st.text_input("单版版面号", value="05", help="单版抓取时使用，例如：01、02、03、04、05")
    custom_pages = st.text_input("自定义版面", value="01-05", help="例如：01-05 或 01,03,05,09")

    include_content = st.checkbox(
        "抓取文章正文",
        value=True,
        help="勾选后会逐篇打开文章链接抓取正文。建议用于个人学习，不要公开分发全文。"
    )

    max_content_articles = st.slider(
        "最多抓取正文篇数",
        min_value=1,
        max_value=60,
        value=20,
        help="这是候选文章正文抓取上限；最终输出仍然最多10篇精品。"
    )

    st.divider()
    st.header("精品筛选")

    max_best_articles = st.slider("每日Top10候选文章上限", min_value=1, max_value=10, value=10)
    min_score = st.slider("最低考公价值分", min_value=0, max_value=10, value=0)
    tag_keyword = st.text_input("按主题标签筛选", value="")
    interview_keyword = st.text_input("按面试题型筛选", value="")

    st.divider()
    st.header("输出设置")

    top_n_word = st.slider("生成Word文章篇数", min_value=1, max_value=10, value=8)
    deep_reading_count = st.slider(
        "深度精读篇数",
        min_value=2,
        max_value=3,
        value=3,
        help="V7建议只精读前2—3篇。Top10只是候选池，不要让ChatGPT平均分析10篇。"
    )

    st.divider()
    st.header("手机/公网")
    st.caption("V7 可部署到 Streamlit Community Cloud，生成公网网址后 iPhone Safari 可以直接打开。")
    st.caption("本地同 Wi‑Fi 也可用 Mac 局域网 IP 访问。部署步骤见压缩包内 DEPLOY_TO_PUBLIC_WEB.md。")

date_str = selected_date.strftime("%Y-%m-%d")
page_no = page_no.zfill(2)

if page_mode == "01—05 版":
    pages = [str(i).zfill(2) for i in range(1, 6)]
elif page_mode == "01—10 版":
    pages = [str(i).zfill(2) for i in range(1, 11)]
elif page_mode == "单版抓取":
    pages = [page_no]
else:
    try:
        pages = parse_custom_pages(custom_pages)
    except Exception:
        pages = ["01", "02", "03", "04", "05"]

st.subheader("当前任务")
st.write(f"准备抓取：**{date_str} 第 {', '.join(pages)} 版**")
st.info(f"本版本每天最多输出 **{max_best_articles} 篇Top候选文章**，Markdown 默认只对前 **{deep_reading_count} 篇**做超详细精读。")

if include_content:
    st.warning(f"本次会继续抓取候选文章正文，最多抓取 {max_content_articles} 篇；最终只保留Top {max_best_articles}候选，并精读前{deep_reading_count}篇。")
else:
    st.info("当前只抓取文章标题和链接，不抓取正文。")

st.caption("提示：如果今天抓不到，可能人民日报电子版当天尚未更新，建议先选择昨天日期或已成功抓取过的日期测试。")

if st.button("开始抓取", type="primary"):
    try:
        with st.spinner("正在抓取候选文章，请稍等..."):
            articles = fetch_multiple_pages(
                date_str,
                pages,
                include_content=include_content,
                max_content_articles=max_content_articles,
            )

            if not articles:
                st.session_state.df = pd.DataFrame()
                st.session_state.best_df = pd.DataFrame()
                st.warning("没有抓到文章。可能是当天人民日报电子版还没有更新，或者该日期/版面不存在。请换一个已发布日期，或稍后再试。")
                st.stop()

            st.session_state.current_task = f"{date_str}_第{'-'.join(pages)}版"
            raw_df = articles_to_dataframe(articles)

            if raw_df.empty:
                st.session_state.df = pd.DataFrame()
                st.session_state.best_df = pd.DataFrame()
                st.warning("抓取到了页面，但没有解析到文章列表。可能页面结构变化，或该日期/版面暂无文章。")
                st.stop()

            raw_df = ensure_content_column(raw_df, articles)

            best_df = select_best_articles(
                raw_df,
                max_articles=max_best_articles,
                min_score=min_score,
            )

            if best_df.empty:
                st.session_state.df = raw_df
                st.session_state.best_df = pd.DataFrame()
                st.warning("有候选文章，但按当前最低分筛选后没有精品文章。建议降低“最低考公价值分”。")
                st.stop()

            st.session_state.df = raw_df
            st.session_state.best_df = best_df
            st.session_state.task_code = build_task_code(date_str)

        st.success(f"抓取成功：候选文章 {len(raw_df)} 篇，最终保留Top候选 {len(best_df)} 篇。")
        st.info(f"本次 ChatGPT 半自动分析任务码：{st.session_state.task_code}")

    except Exception as e:
        st.error("抓取失败，请先按下面原因排查：")
        st.markdown(
            """
            1. 当天人民日报电子版可能尚未更新。
            2. 所选日期或版面不存在。
            3. 网络暂时异常。
            4. 人民日报页面结构可能变化。
            5. 建议先切换到昨天日期或已成功抓取过的日期测试。
            """
        )
        with st.expander("查看技术错误"):
            st.exception(e)

if st.session_state.best_df is not None and not st.session_state.best_df.empty:
    raw_df = st.session_state.df.copy()
    df = st.session_state.best_df.copy()

    filtered_df = df.copy()
    if tag_keyword.strip():
        filtered_df = filtered_df[filtered_df["主题标签"].fillna("").str.contains(tag_keyword.strip())]
    if interview_keyword.strip():
        filtered_df = filtered_df[filtered_df["可转化面试题型"].fillna("").str.contains(interview_keyword.strip())]

    candidate_count = min(10, len(df))
    deep_count = min(deep_reading_count, len(df))

    top_df, shenlun_df, interview_df, bilingual_df, cloze_df, review_df = make_study_sheets(df)
    prompt_first_df = build_prompt_first_sheet(
        df,
        task_code=st.session_state.task_code,
        candidate_top_n=candidate_count,
        deep_n=deep_count,
    )
    prompt_df = build_prompt_sheet(df, top_n=deep_count)
    chatgpt_package_df = build_chatgpt_package(
        df,
        task_code=st.session_state.task_code,
        candidate_top_n=candidate_count,
        deep_n=deep_count,
    )
    markdown_package = build_chatgpt_markdown_package(
        df,
        task_code=st.session_state.task_code,
        candidate_top_n=candidate_count,
        deep_n=deep_count,
    )

    mobile_quick = usage_mode == "手机快速模式"

    st.markdown("### 数据概览")
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("候选文章", len(raw_df))
    col2.metric("Top候选", len(df))
    col3.metric("当前筛选后", len(filtered_df))
    col4.metric("最高考公价值分", int(df["考公价值分"].max()))
    col5.metric("深度精读篇数", deep_count)

    st.markdown("### 今日Top10候选文章")
    st.success(f"本表显示今日候选文章，最多10篇；Markdown只要求ChatGPT对前{deep_count}篇做超详细精读。")
    if mobile_quick:
        st.info("手机快速模式已简化表格预览，优先使用下方 Markdown 下载按钮。")
        st.dataframe(filtered_df[["日期", "版面", "标题", "考公价值分", "主题标签", "链接"]], width="stretch", height=260)
    else:
        st.dataframe(filtered_df, width="stretch")

    st.markdown("### ChatGPT 半自动使用说明")
    st.success(f"任务码：{st.session_state.task_code}")
    st.info(f"推荐下载 Markdown 分析包，上传到 ChatGPT App。Top10只是候选，不要平均分析全部文章；V7会要求只对前{deep_count}篇做超详细精读。")
    st.text_area("复制给 ChatGPT 的完整指令", value=CHATGPT_COPY_INSTRUCTION, height=150)
    if not mobile_quick:
        st.dataframe(prompt_first_df, width="stretch")

    if not mobile_quick:
        tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
            "先看这里",
        "Top10候选",
            "候选文章池",
            "申论素材卡",
            "面试题库",
            "逻辑填空",
            "今日复盘",
            "ChatGPT待分析包",
            "AI提示词",
        ])

        with tab1:
            st.dataframe(prompt_first_df, width="stretch")
        with tab2:
            st.dataframe(top_df, width="stretch")
        with tab3:
            st.dataframe(raw_df, width="stretch")
        with tab4:
            st.dataframe(shenlun_df, width="stretch")
        with tab5:
            st.dataframe(interview_df, width="stretch")
        with tab6:
            st.dataframe(cloze_df, width="stretch")
        with tab7:
            st.dataframe(review_df, width="stretch")
        with tab8:
            st.dataframe(chatgpt_package_df, width="stretch")
        with tab9:
            st.dataframe(prompt_df, width="stretch")

    sheets = {
        "先看这里_ChatGPT提示词": prompt_first_df,
        "今日精品文章Top10": df,
        "候选文章池": raw_df,
        "申论素材卡": shenlun_df,
        "面试题库": interview_df,
        "中英表达": bilingual_df,
        "逻辑填空积累": cloze_df,
        "今日复盘": review_df,
        "ChatGPT待分析包": chatgpt_package_df,
        "AI提示词": prompt_df,
    }

    st.markdown("### 下载区")
    st.download_button(
        label="下载 V7 Markdown分析包（手机推荐）",
        data=markdown_package.encode("utf-8"),
        file_name=f"人民日报_{st.session_state.current_task}_V7_Top10候选_深度精读{deep_count}篇.md",
        mime="text/markdown",
        type="primary",
    )

    excel_bytes = export_beautified_excel(sheets)
    if mobile_quick:
        with st.expander("电脑端下载：Excel 和 Word"):
            st.download_button(
                label="下载 V7 Excel学习包",
                data=excel_bytes,
                file_name=f"人民日报_{st.session_state.current_task}_V7学习包.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

            article_zip_bytes = create_article_docx_zip(
                df,
                task_code=st.session_state.task_code,
                top_n=min(top_n_word, len(df)),
            )
            st.download_button(
                label="下载原始精品文章单独Word压缩包",
                data=article_zip_bytes,
                file_name=f"人民日报_{st.session_state.current_task}_原始精品文章单独Word.zip",
                mime="application/zip",
            )
    else:
        st.download_button(
            label="下载 V7 Excel学习包",
            data=excel_bytes,
            file_name=f"人民日报_{st.session_state.current_task}_V7学习包.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

        article_zip_bytes = create_article_docx_zip(
            df,
            task_code=st.session_state.task_code,
            top_n=min(top_n_word, len(df)),
        )
        st.download_button(
            label="下载原始精品文章单独Word压缩包",
            data=article_zip_bytes,
            file_name=f"人民日报_{st.session_state.current_task}_原始精品文章单独Word.zip",
            mime="application/zip",
        )

        combined_docx = create_combined_docx(df, task_code=st.session_state.task_code, top_n=min(top_n_word, len(df)))
        st.download_button(
            label="下载原始精品总学习笔记Word",
            data=combined_docx,
            file_name=f"人民日报_{st.session_state.current_task}_原始精品总学习笔记.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )

st.divider()
st.caption("说明：V7不调用任何AI API，不需要API Key。Top10只是候选，Markdown默认只要求前2—3篇超详细精读，并保留逻辑填空积累模块。")
