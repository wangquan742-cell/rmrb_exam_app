import re
import time
from dataclasses import dataclass
from typing import List
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup


@dataclass
class Article:
    date: str
    page_no: str
    page_name: str
    title: str
    url: str
    source: str = "人民日报电子版"
    content: str = ""


def build_layout_url(date: str, page_no: str) -> str:
    year, month, day = date.split("-")
    return f"https://paper.people.com.cn/rmrb/pc/layout/{year}{month}/{day}/node_{page_no}.html"


def clean_text(text: str) -> str:
    if not text:
        return ""

    text = text.replace("\u3000", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n", text)
    return text.strip()


def fetch_article_content(url: str, sleep_seconds: float = 0.8) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X) AppleWebKit/537.36"
    }

    time.sleep(sleep_seconds)

    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    response.encoding = response.apparent_encoding

    soup = BeautifulSoup(response.text, "lxml")

    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    paragraphs = []
    for p in soup.find_all("p"):
        text = p.get_text(strip=True)
        if not text:
            continue

        if text in ["人民日报", "返回目录", "上一版", "下一版"]:
            continue
        if "版权声明" in text:
            continue
        if "人民日报社" in text and len(text) < 50:
            continue
        if "本报" not in text and len(text) < 8:
            continue

        paragraphs.append(text)

    content = "\n".join(paragraphs)
    return clean_text(content)


def fetch_layout_articles(
    date: str,
    page_no: str,
    sleep_seconds: float = 0.8,
    include_content: bool = False,
    max_content_articles: int = 10,
) -> List[Article]:
    url = build_layout_url(date, page_no)

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X) AppleWebKit/537.36"
    }

    time.sleep(sleep_seconds)

    response = requests.get(url, headers=headers, timeout=15)

    if response.status_code == 404:
        return []

    response.raise_for_status()
    response.encoding = response.apparent_encoding

    soup = BeautifulSoup(response.text, "lxml")

    page_name = ""
    for text in soup.stripped_strings:
        if text.startswith(f"第{page_no}版"):
            page_name = text
            break

    articles: List[Article] = []
    seen = set()

    for a in soup.find_all("a"):
        title = a.get_text(strip=True).replace("·", "").strip()
        href = a.get("href")

        if not title or not href:
            continue

        if "content_" not in href:
            continue

        full_url = urljoin(url, href)

        if full_url in seen:
            continue

        seen.add(full_url)

        articles.append(
            Article(
                date=date,
                page_no=page_no,
                page_name=page_name,
                title=title,
                url=full_url,
            )
        )

    if include_content:
        for index, article in enumerate(articles):
            if index >= max_content_articles:
                break
            try:
                article.content = fetch_article_content(article.url)
            except Exception as e:
                article.content = f"正文抓取失败：{e}"

    return articles


def fetch_multiple_pages(
    date: str,
    page_numbers: List[str],
    include_content: bool = False,
    max_content_articles: int = 20,
) -> List[Article]:
    all_articles: List[Article] = []
    remaining_content_count = max_content_articles

    for page_no in page_numbers:
        page_no = str(page_no).zfill(2)

        if include_content:
            page_content_limit = max(0, remaining_content_count)
            articles = fetch_layout_articles(
                date,
                page_no,
                include_content=True,
                max_content_articles=page_content_limit,
            )
            grabbed_count = sum(1 for item in articles if item.content)
            remaining_content_count -= grabbed_count
        else:
            articles = fetch_layout_articles(date, page_no)

        all_articles.extend(articles)

    return all_articles


def score_exam_value(title: str, page_name: str = "", content: str = "") -> int:
    text = f"{title} {page_name} {content[:800]}"

    keyword_weights = {
        "高质量发展": 5,
        "新质生产力": 5,
        "基层治理": 5,
        "中国式现代化": 5,
        "乡村振兴": 5,
        "科技创新": 5,
        "全过程人民民主": 5,
        "共同富裕": 5,
        "改革": 4,
        "营商环境": 4,
        "民生": 4,
        "就业": 4,
        "教育": 4,
        "医疗": 4,
        "养老": 4,
        "法治": 4,
        "依法": 4,
        "公共服务": 4,
        "社会治理": 4,
        "城市治理": 4,
        "数字政府": 4,
        "数字": 3,
        "智能": 3,
        "绿色": 3,
        "生态": 3,
        "安全": 3,
        "群众": 3,
        "干部": 3,
        "服务": 2,
        "发展": 2,
        "创新": 2,
        "治理": 2,
        "监督": 2,
        "落实": 2,
    }

    score = 0

    for keyword, weight in keyword_weights.items():
        if keyword in text:
            score += weight

    if "要闻" in page_name:
        score += 2
    if "评论" in page_name:
        score += 4
    if "理论" in page_name:
        score += 4
    if "经济" in page_name:
        score += 3
    if "社会" in page_name:
        score += 3
    if "法治" in page_name:
        score += 3

    return min(score, 10)


def generate_topic_tags(title: str, page_name: str = "", content: str = "") -> str:
    text = f"{title} {page_name} {content[:800]}"

    tag_rules = {
        "基层治理": ["基层", "社区", "乡村治理", "治理"],
        "高质量发展": ["高质量发展", "发展", "经济"],
        "新质生产力": ["新质生产力", "科技", "智能", "数字", "创新", "人工智能"],
        "民生服务": ["民生", "就业", "教育", "医疗", "养老", "公共服务"],
        "法治政府": ["法治", "依法", "执法", "法院", "检察", "法律"],
        "乡村振兴": ["乡村", "农村", "农业", "农民"],
        "生态文明": ["生态", "绿色", "环保", "环境", "污染"],
        "干部作风": ["干部", "作风", "担当", "落实", "监督"],
        "营商环境": ["营商环境", "企业", "市场主体", "政务服务"],
        "安全治理": ["安全", "风险", "应急", "防范", "底线"],
        "数字治理": ["数字政府", "数字化", "智能化", "数据", "平台"],
    }

    tags = []

    for tag, keywords in tag_rules.items():
        for keyword in keywords:
            if keyword in text:
                tags.append(tag)
                break

    if not tags:
        tags.append("待人工判断")

    return "、".join(tags)


def suggest_interview_types(title: str, tags: str) -> str:
    result = []

    if any(key in tags for key in ["基层治理", "民生服务", "法治政府", "营商环境", "生态文明", "数字治理", "安全治理"]):
        result.append("社会现象题")

    if any(key in tags for key in ["干部作风", "基层治理", "民生服务", "高质量发展", "新质生产力"]):
        result.append("观点题")

    if any(key in tags for key in ["民生服务", "基层治理", "法治政府", "安全治理", "数字治理"]):
        result.append("应急应变题")

    if any(key in tags for key in ["乡村振兴", "生态文明", "营商环境", "民生服务"]):
        result.append("组织管理题")

    if not result:
        result.append("素材积累")

    return "、".join(result)


def generate_simple_summary(title: str, content: str) -> str:
    if not content:
        return f"围绕“{title}”进行素材积累，后续可进一步人工或AI解析。"

    first_sentence = re.split(r"[。！？]", content.strip())[0]
    if first_sentence:
        return first_sentence[:120] + "。"

    return f"围绕“{title}”进行素材积累。"


def generate_shenlun_direction(tags: str) -> str:
    directions = []

    if "基层治理" in tags:
        directions.append("基层治理：党建引领、群众参与、资源下沉、闭环落实")
    if "高质量发展" in tags:
        directions.append("高质量发展：问题导向、创新驱动、结构优化、提质增效")
    if "新质生产力" in tags:
        directions.append("新质生产力：科技创新、产业升级、数字赋能、人才支撑")
    if "民生服务" in tags:
        directions.append("民生服务：群众需求、公共服务、精准供给、兜底保障")
    if "法治政府" in tags:
        directions.append("法治政府：依法行政、规范执法、权责清晰、程序公正")
    if "乡村振兴" in tags:
        directions.append("乡村振兴：产业振兴、人才振兴、文化振兴、生态振兴、组织振兴")
    if "生态文明" in tags:
        directions.append("生态文明：绿色发展、污染防治、系统治理、长效保护")
    if "营商环境" in tags:
        directions.append("营商环境：简政放权、优化服务、公平监管、激发市场活力")
    if "安全治理" in tags:
        directions.append("安全治理：风险预判、隐患排查、应急处置、底线思维")
    if "数字治理" in tags:
        directions.append("数字治理：数据赋能、平台协同、流程再造、减负增效")

    if not directions:
        return "后续人工判断：可从背景、问题、原因、对策、金句五个角度积累。"

    return "；".join(directions)


def generate_governance_thinking(tags: str) -> str:
    thinking = []

    if "基层治理" in tags or "民生服务" in tags:
        thinking.append("群众思维")
        thinking.append("闭环思维")
    if "法治政府" in tags:
        thinking.append("法治思维")
    if "安全治理" in tags:
        thinking.append("底线思维")
        thinking.append("应急思维")
    if "数字治理" in tags or "新质生产力" in tags:
        thinking.append("创新思维")
        thinking.append("系统思维")
    if "高质量发展" in tags or "营商环境" in tags:
        thinking.append("发展思维")
        thinking.append("服务思维")
    if "生态文明" in tags:
        thinking.append("系统治理思维")
    if "干部作风" in tags:
        thinking.append("责任意识")
        thinking.append("落实意识")

    if not thinking:
        thinking.append("问题导向")
        thinking.append("系统思维")

    return "、".join(dict.fromkeys(thinking))


def generate_interview_question(title: str, tags: str, interview_types: str) -> str:
    if "社会现象题" in interview_types:
        return f"人民日报文章《{title}》反映了相关社会治理/公共服务现象。对此，你怎么看？"

    if "观点题" in interview_types:
        return f"有人说，推进相关工作既要重视效率，也要重视群众感受。结合《{title}》，谈谈你的理解。"

    if "应急应变题" in interview_types:
        return f"如果你是基层工作人员，在推进《{title}》相关工作中遇到群众质疑或突发情况，你会怎么办？"

    if "组织管理题" in interview_types:
        return f"单位准备围绕《{title}》相关主题开展一次调研或宣传活动，领导交给你负责，你怎么组织？"

    return f"请结合《{title}》，谈谈这篇文章对公务员日常工作的启发。"


def generate_bilingual_terms(tags: str) -> str:
    terms = []

    mapping = {
        "基层治理": "基层治理：grassroots governance / community-level governance",
        "高质量发展": "高质量发展：high-quality development",
        "新质生产力": "新质生产力：new quality productive forces",
        "民生服务": "民生保障：ensuring and improving people's wellbeing；公共服务：public services",
        "法治政府": "法治政府：law-based government；依法行政：law-based administration",
        "乡村振兴": "乡村振兴：rural revitalization",
        "生态文明": "生态文明：ecological civilization；绿色发展：green development",
        "营商环境": "优化营商环境：improve the business environment",
        "干部作风": "干部作风：work style of officials；担当作为：take responsibility and act proactively",
        "安全治理": "风险防控：risk prevention and control；应急处置：emergency response",
        "数字治理": "数字治理：digital governance；数据赋能：data empowerment",
    }

    for tag, expression in mapping.items():
        if tag in tags:
            terms.append(expression)

    if not terms:
        terms.append("后续人工补充：中文机关表达 + 英文表达 + 使用场景")

    return "；".join(terms)


def generate_cloze_accumulation(tags: str, title: str = "") -> str:
    base = [
        "高频实词：推进、完善、优化、提升、夯实、统筹、赋能、落实",
        "规范搭配：系统推进、协同发力、精准施策、久久为功、闭环管理、源头治理、提质增效",
        "成语/四字格：因地制宜、久久为功、标本兼治、同向发力",
        "近义词辨析：推动偏宏观启动，推进偏过程落实，促进偏形成积极变化；完善偏补短板，健全偏建机制，优化偏提质量",
        "语境关系：重点关注并列、递进、转折、因果、解释说明、让步补充",
        "仿真逻辑填空题：请ChatGPT结合原文生成2—3道题，并给出正确答案与错项解析",
        "今日必背搭配：精准施策、协同治理、提质增效、闭环落实",
    ]

    if "基层治理" in tags:
        base.append("主题搭配：党建引领基层治理、资源下沉、群众参与、闭环落实")
    if "高质量发展" in tags or "新质生产力" in tags:
        base.append("主题搭配：创新驱动、数字赋能、产业升级、提质增效")
    if "民生服务" in tags:
        base.append("主题搭配：精准供给、兜底保障、回应关切、优化服务")
    if "法治政府" in tags:
        base.append("主题搭配：依法行政、规范执法、权责清晰、源头治理")
    if "营商环境" in tags:
        base.append("主题搭配：简政放权、公平监管、优化服务、激发活力")

    return "；".join(base)


def generate_daily_review(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()

    top = df.sort_values(by="考公价值分", ascending=False).head(5)

    rows = []
    for index, row in top.iterrows():
        rows.append({
            "复盘类型": "今日重点文章",
            "内容": row.get("标题", ""),
            "建议动作": f"重点看：{row.get('申论积累方向', '')}",
            "对应链接": row.get("链接", ""),
        })
        rows.append({
            "复盘类型": "今日面试练习",
            "内容": row.get("面试题雏形", ""),
            "建议动作": "按照社会现象/观点/应急/组织管理模板，口头作答一遍",
            "对应链接": row.get("链接", ""),
        })

    rows.append({
        "复盘类型": "今日必背表达",
        "内容": "坚持问题导向，聚焦群众急难愁盼，推动工作从“有没有”向“好不好”转变。",
        "建议动作": "背诵并尝试改写到申论开头或面试结尾",
        "对应链接": "",
    })
    rows.append({
        "复盘类型": "今日必背表达",
        "内容": "以系统观念统筹推进，以闭环机制压实责任，以群众满意检验成效。",
        "建议动作": "用于组织管理、基层治理、应急应变类题目总结升华",
        "对应链接": "",
    })

    return pd.DataFrame(rows)


def articles_to_dataframe(articles: List[Article]) -> pd.DataFrame:
    rows = []

    for item in articles:
        score = score_exam_value(item.title, item.page_name, item.content)
        tags = generate_topic_tags(item.title, item.page_name, item.content)
        interview_types = suggest_interview_types(item.title, tags)

        content = item.content or ""
        content_preview = content[:300] + ("..." if len(content) > 300 else "")

        rows.append({
            "日期": item.date,
            "版面号": item.page_no,
            "版面": item.page_name,
            "标题": item.title,
            "链接": item.url,
            "来源": item.source,
            "考公价值分": score,
            "主题标签": tags,
            "机关思维": generate_governance_thinking(tags),
            "可转化面试题型": interview_types,
            "正文字数": len(content),
            "正文预览": content_preview,
            "一句话概括": generate_simple_summary(item.title, content),
            "申论积累方向": generate_shenlun_direction(tags),
            "面试题雏形": generate_interview_question(item.title, tags, interview_types),
            "中英表达积累": generate_bilingual_terms(tags),
            "逻辑填空积累": generate_cloze_accumulation(tags, item.title),
            "复习状态": "未复习",
            "个人笔记": "",
            "备注": "V7.1：三篇超详细精读 + 手机一键复制任务版"
        })

    df = pd.DataFrame(rows)

    if not df.empty:
        df = df.sort_values(by=["考公价值分", "版面号"], ascending=[False, True])

    return df


def make_study_sheets(df: pd.DataFrame):
    if df.empty:
        empty = pd.DataFrame()
        return empty, empty, empty, empty, empty, empty

    top_df = df.sort_values(by="考公价值分", ascending=False).head(10)

    shenlun_cols = [
        "日期", "版面", "标题", "考公价值分", "主题标签", "机关思维",
        "一句话概括", "申论积累方向", "正文预览", "链接"
    ]
    shenlun_df = df[[col for col in shenlun_cols if col in df.columns]].copy()

    interview_cols = [
        "日期", "版面", "标题", "可转化面试题型", "面试题雏形",
        "主题标签", "机关思维", "链接"
    ]
    interview_df = df[[col for col in interview_cols if col in df.columns]].copy()

    bilingual_cols = [
        "日期", "标题", "主题标签", "中英表达积累", "链接"
    ]
    bilingual_df = df[[col for col in bilingual_cols if col in df.columns]].copy()

    cloze_cols = [
        "日期", "标题", "主题标签", "逻辑填空积累", "正文预览", "链接"
    ]
    cloze_df = df[[col for col in cloze_cols if col in df.columns]].copy()

    review_df = generate_daily_review(df)

    return top_df, shenlun_df, interview_df, bilingual_df, cloze_df, review_df
