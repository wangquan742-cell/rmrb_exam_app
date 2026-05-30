from typing import Dict
import pandas as pd


CHATGPT_COPY_INSTRUCTION = "请读取我上传的 Markdown 分析包，按文件内置的深度精读指令执行。不要简单总结，要讲清原文关键内容、深层含义、政策背景、文章结构、申论、面试、机关思维、工业视角、行测言语、中英表达和逻辑填空积累。完成解析后，请把不同文章分别生成 Word 文档，并把所有 Word 打包成一个 zip 文件返回给我下载。"


def build_task_code(date_str: str, task_name: str = "人民日报深度精读") -> str:
    safe_date = date_str.replace("-", "")
    return f"RMRB-DEEP-{safe_date}-{task_name}"


def build_deep_reading_prompt(row: Dict) -> str:
    """
    V6 统一深度精读提示词。
    不调用任何 API，专门用于导出 Markdown / Excel 后上传给 ChatGPT App。
    """
    title = row.get("标题", "")
    page = row.get("版面", "")
    tags = row.get("主题标签", "")
    thinking = row.get("机关思维", "")
    content = row.get("正文全文", "") or row.get("正文预览", "")
    link = row.get("链接", "")

    return f"""
你是我的“人民日报公考考编深度精读教练”。请注意：不要只做简单总结，不要泛泛而谈。我要的是像精读课一样，把文章讲透，让我即使不看原文，也能知道原文讲了什么、为什么这么讲、背后的政策逻辑是什么、如何迁移到申论/面试/行测言语/机关思维/产业工业视角中。

【文章信息】
标题：{title}
版面：{page}
主题标签：{tags}
机关思维初判：{thinking}
链接：{link}

【文章原文/正文预览】
{content}

【总要求】
请严格按照以下结构输出。每一部分都要尽量贴合原文，不要空泛套话。请把原文中的关键内容、关键逻辑、关键表达讲出来。重点不是“概括得短”，而是“讲得清楚、能积累、能迁移”。

一、原文关键内容精读：让我不看原文也知道文章讲了什么
1. 文章讲的核心事件/核心观点是什么？
2. 原文中有哪些关键事实、数据、主体、措施、案例？
3. 文章每一部分大概在讲什么？请按照原文顺序展开。
4. 哪些内容是必须记住的？哪些只是背景铺垫？
5. 用“考公学习语言”把原文内容重新讲一遍，但不要脱离原文。

二、深层含义与背后政策背景延伸
1. 这篇文章背后对应的国家战略、政策方向、治理要求是什么？
2. 可能关联哪些高频主题：高质量发展、新质生产力、基层治理、民生服务、数字治理、法治政府、营商环境、乡村振兴、生态文明、干部作风等？
3. 文章表面在讲什么，深层实际在强调什么？
4. 对公务员日常工作有什么启发：站位、群众观、问题导向、系统治理、依法行政、闭环落实、风险意识等。
5. 适合延伸积累的背景文件/政策精神请用通俗语言说明，不要编造具体文件名称；如果不确定，就说“可联系到某类政策方向”。

三、文章结构拆解：按公考文章阅读逻辑分析
请按照我做公考文章阅读的方法来拆：
1. 第一段/开头是否是背景？背景提供了什么语境？
2. 文中是否出现“本应/理应/原本应该”等理想状态与现实偏差？如果有，说明作者想提出什么问题。
3. “此外”类表达是在补充、并列，还是递进？
4. “对此/为此/因此”等后面是否提出对策？这些是不是重点？
5. “更为关键的是”等表达是并列还是递进？是否提示重点转移？
6. “当然”等表达是补充、让步，还是限定？为什么不能误判为主旨？
7. 结尾是否总结全文？如何帮助锁定主旨？
8. 如果这篇文章用于行测言语理解，主旨概括题、意图判断题、语句填空题可能怎么考？

四、申论积累
1. 可用于哪些申论主题？
2. 原文中可以积累的规范表达有哪些？请列出并解释适用场景。
3. 可以积累成哪些案例素材？
4. 可以写成哪些大作文分论点？
5. 可以迁移到哪些热点话题？
6. 如果写申论对策，可以从哪些角度展开：制度、机制、技术、人才、协同、监督、服务、落实等。

五、面试思维衍生与知识积累
1. 这篇文章可以转化成哪些面试题？至少给出：社会现象题、观点题、组织管理题、应急应变题或群众工作题。
2. 每类题目的核心作答角度是什么？
3. 如果考场上遇到类似题目，帽子怎么想、第一句话怎么开口？
4. 题干关键词怎么拆？
5. 可以从哪些意义、问题、原因、对策展开？
6. 如何自然升华，不要模板化？
7. 提炼这篇文章能补充的面试知识点，比如基层治理、公共服务、数字赋能、依法行政、协同治理、干部作风等。

六、公务员机关思维训练
请提炼这篇文章体现的机关工作思维：政治站位、群众思维、问题导向、系统思维、法治思维、底线思维、闭环思维、服务意识、落实意识。每一点都要结合文章内容说明，不能只列词。

七、工业/产业/工程机械/制造业视角积累
1. 这篇文章对制造业、高质量发展、新质生产力、数字化转型、产业升级有什么启发？
2. 如果联系工程机械、工业车辆、港口物流、起重机、解决方案业务，可以提炼哪些客户场景、产品话术或市场机会？
3. 如果文章不是工业主题，也请说明它能不能迁移到产业服务、政企客户、项目型销售、解决方案思维中。
4. 提炼3—5条“可用于工作中的表达/思路”。

八、行测言语理解积累
1. 文章主旨是什么？为什么？
2. 作者态度是什么？从哪些词句看出来？
3. 哪些逻辑词是“看门人”：例如本应、此外、对此、更为关键的是、当然、最后等？
4. 如果出主旨概括题，正确选项应该长什么样？
5. 如果出意图判断题，作者真正想强调什么？
6. 如果出语句填空/接语选择，应该关注什么逻辑？
7. 积累5个人民日报常用高频搭配，并说明适用场景。

九、中英表达积累
请提炼5—8组：中文机关表达、英文表达、使用场景、可用于申论/面试/工作汇报的例句。

十、金句与规范表达积累
1. 原文中值得摘抄的表达
2. 可以改写成申论/面试语言的表达
3. 今日必背金句3—5句
4. 每句适合用在哪类题目里

十一、逻辑填空积累
1. 从文章中提炼高频实词，并说明常见搭配和适用语境。
2. 提炼人民日报规范搭配，例如系统推进、协同发力、精准施策、久久为功、闭环管理、源头治理、提质增效等。
3. 提炼成语或四字格表达，说明含义、适用场景、易错点。
4. 做近义词辨析，例如推动/推进/促进，完善/健全/优化，提升/提高/增强，夯实/筑牢/巩固。
5. 分析文章中的语境关系，例如并列、递进、转折、因果、解释说明、让步补充。
6. 基于文章内容生成2—3道仿真逻辑填空题。
7. 给出正确答案。
8. 对每个错误选项说明为什么错：搭配不当、程度不符、感情色彩不符、对象不匹配、语义重复或逻辑不一致。
9. 输出今日必背词语和搭配。

十二、输出 Word 压缩包要求
如果当前 ChatGPT 环境支持生成文件，请在完成解析后：
1. 每一篇文章单独生成一个 Word 文档。
2. 每个 Word 文档内容包括：原文关键内容精读、深层含义、结构拆解、申论积累、面试思维、机关思维、工业视角、行测言语、逻辑填空积累、中英表达、金句积累。
3. 把所有 Word 文档放入一个 zip 压缩包。
4. 将 zip 文件返回给我下载。
如果当前环境不能生成文件，请先输出可复制到 Word 的完整内容。

十三、可回填表格
最后请用表格输出以下字段，方便我复制回Excel：
标题｜原文关键内容｜深层含义｜结构拆解｜申论主题｜申论规范表达｜面试题｜面试答题思路｜机关思维｜工业视角积累｜行测言语积累｜逻辑填空积累｜中英表达｜金句积累

【特别提醒】
- 不要说“文章强调了……”就结束，要具体说强调了什么、怎么强调、为什么重要。
- 不要只总结，要做精读、拆结构、做迁移、做积累。
- 如果原文信息不足，请基于原文预览谨慎分析，并明确说明“需要完整原文进一步确认”。
""".strip()


def build_prompt_first_sheet(df: pd.DataFrame, task_code: str, top_n: int = 5) -> pd.DataFrame:
    return pd.DataFrame([
        {
            "序号": 1,
            "用途": "最推荐：上传Markdown/Excel后复制这句话给ChatGPT",
            "复制给ChatGPT的内容": f"{CHATGPT_COPY_INSTRUCTION} 任务码：{task_code}。请优先分析精品文章前{top_n}篇。",
            "说明": "把Markdown分析包或Excel上传到当前ChatGPT窗口后，复制这一句话即可。",
        },
        {
            "序号": 2,
            "用途": "只分析最高分文章",
            "复制给ChatGPT的内容": f"请读取我上传的文件，任务码：{task_code}。只分析考公价值分最高的1篇文章。要求不是简单总结，而是做深度精读：原文关键内容、深层含义、政策背景、文章结构、申论积累、面试思维、机关思维、工业视角、行测言语、逻辑填空积累、中英表达、金句积累。完成后请生成一个Word文档返回。",
            "说明": "第一次测试或手机端快速使用时用这个。",
        },
        {
            "序号": 3,
            "用途": "让ChatGPT帮我回填表格",
            "复制给ChatGPT的内容": "请把你的解析结果整理成表格，字段包括：标题、原文关键内容、深层含义、结构拆解、申论主题、申论规范表达、面试题、面试答题思路、机关思维、工业视角积累、行测言语积累、逻辑填空积累、中英表达、金句积累。",
            "说明": "解析完之后追加这句话，让结果更方便复制回Excel。",
        },
        {
            "序号": 4,
            "用途": "V6.2模式说明",
            "复制给ChatGPT的内容": "V6.2不调用任何API，不需要任何API Key，只生成可上传给ChatGPT的Markdown、Excel和Word学习包。请直接根据我上传的文件做深度精读分析。",
            "说明": "防止混淆。",
        },
    ])


def build_prompt_sheet(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()

    top_df = df.sort_values(by="考公价值分", ascending=False).head(top_n)
    rows = []
    for _, row in top_df.iterrows():
        row_dict = row.to_dict()
        rows.append({
            "标题": row_dict.get("标题", ""),
            "考公价值分": row_dict.get("考公价值分", ""),
            "主题标签": row_dict.get("主题标签", ""),
            "机关思维": row_dict.get("机关思维", ""),
            "深度精读提示词": build_deep_reading_prompt(row_dict),
            "链接": row_dict.get("链接", ""),
        })
    return pd.DataFrame(rows)


def build_chatgpt_package(df: pd.DataFrame, task_code: str, top_n: int = 5) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()

    top_df = df.sort_values(by="考公价值分", ascending=False).head(top_n)
    rows = []
    for _, row in top_df.iterrows():
        row_dict = row.to_dict()
        rows.append({
            "任务码": task_code,
            "分析优先级": len(rows) + 1,
            "日期": row_dict.get("日期", ""),
            "版面": row_dict.get("版面", ""),
            "标题": row_dict.get("标题", ""),
            "考公价值分": row_dict.get("考公价值分", ""),
            "主题标签": row_dict.get("主题标签", ""),
            "机关思维": row_dict.get("机关思维", ""),
            "可转化面试题型": row_dict.get("可转化面试题型", ""),
            "一句话概括_规则版": row_dict.get("一句话概括", ""),
            "申论积累方向_规则版": row_dict.get("申论积累方向", ""),
            "面试题雏形_规则版": row_dict.get("面试题雏形", ""),
            "中英表达积累_规则版": row_dict.get("中英表达积累", ""),
            "逻辑填空积累_规则版": row_dict.get("逻辑填空积累", ""),
            "正文预览": row_dict.get("正文预览", ""),
            "链接": row_dict.get("链接", ""),
            "请ChatGPT输出": "原文关键内容精读、深层含义、政策背景、文章结构、公考阅读逻辑、申论积累、面试思维、机关思维、工业视角、行测言语、逻辑填空积累、中英表达、金句积累，并按文章分别生成Word后打包zip",
        })
    return pd.DataFrame(rows)


def build_chatgpt_markdown_package(df: pd.DataFrame, task_code: str, top_n: int = 5) -> str:
    if df.empty:
        return ""

    top_df = df.sort_values(by="考公价值分", ascending=False).head(top_n)
    lines = []
    lines.append("# 人民日报考公考编学习助手 V6.2 Markdown分析包")
    lines.append("")
    lines.append(f"任务码：{task_code}")
    lines.append("")
    lines.append("## 使用方式")
    lines.append("")
    lines.append("把这个 Markdown 文件上传到 ChatGPT App，然后复制下面这段话给 ChatGPT：")
    lines.append("")
    lines.append(f"> {CHATGPT_COPY_INSTRUCTION}")
    lines.append("")
    lines.append("## 全局深度精读要求")
    lines.append("")
    lines.append("1. 先讲清原文关键内容，让我不看原文也知道文章讲什么。")
    lines.append("2. 再讲深层含义和背后政策背景。")
    lines.append("3. 按公考文章阅读逻辑拆结构。")
    lines.append("4. 做申论、面试、机关思维、工业视角、行测言语、逻辑填空积累、中英表达和金句积累。")
    lines.append("5. 不同文章要分别生成Word，最后打包zip返回。")
    lines.append("6. 最后输出可回填Excel的表格。")
    lines.append("7. 逻辑填空积累必须包含：高频实词、规范搭配、成语/四字格、近义词辨析、语境关系、仿真逻辑填空题、正确答案、错项解析、今日必背搭配。")
    lines.append("")

    for idx, (_, row) in enumerate(top_df.iterrows(), start=1):
        row_dict = row.to_dict()
        lines.append(f"## 精品文章 {idx}：{row_dict.get('标题', '')}")
        lines.append("")
        lines.append(f"- 日期：{row_dict.get('日期', '')}")
        lines.append(f"- 版面：{row_dict.get('版面', '')}")
        lines.append(f"- 考公价值分：{row_dict.get('考公价值分', '')}")
        lines.append(f"- 主题标签：{row_dict.get('主题标签', '')}")
        lines.append(f"- 机关思维：{row_dict.get('机关思维', '')}")
        lines.append(f"- 链接：{row_dict.get('链接', '')}")
        lines.append("")
        lines.append("### 正文")
        lines.append("")
        lines.append(str(row_dict.get("正文全文", "") or row_dict.get("正文预览", ""))[:5000])
        lines.append("")
        lines.append("### 本文深度精读提示词")
        lines.append("")
        lines.append(build_deep_reading_prompt(row_dict))
        lines.append("")

    return "\n".join(lines)
