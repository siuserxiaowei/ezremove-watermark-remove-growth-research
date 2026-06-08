#!/usr/bin/env python3
"""Build the full legacy-content breakdown report and inline HTML page."""

from __future__ import annotations

import html
import json
import subprocess
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
DOCS = ROOT / "docs"
SITE = ROOT / "site"


ANALYSIS = {
    "1857705646172631354": {
        "theme": "赚钱认知：从“好学生规则”切换到“资源竞争、风险收益、利用规则”的创业视角。",
        "logic": [
            "用大学生关心荣誉是否影响就业的故事开场，把话题从校园评价体系转到真实赚钱体系。",
            "重新定义赚钱：不是把时间卖出去，而是利用认知差、信息差、规则差创造非线性收益。",
            "提出两个要摒弃的心智：道德洁癖和好学生思维；强调不是无底线，而是要理解资源有限、规则可被利用。",
            "用炒鞋和酒店协议价案例说明：机会往往伴随规则边界和账号/声誉风险，关键是计算风险收益比。",
        ],
        "principle": "做增长的人不能只按平台明面规则考试，要理解用户、平台和商业系统的激励结构；但每个越界动作都必须计算风险，不把风险外包给用户或品牌。",
        "ezremove": [
            "EzRemove 的 PR 可以借这个思路做“普通用户如何用 AI 工具降低素材处理成本”的认知差内容，而不是只讲功能。",
            "所有灰色使用场景必须加边界说明，例如版权、授权、个人素材、商用风险，避免把品牌做成侵权工具。",
            "把免费工具包装成效率杠杆：用更低时间成本完成图片/视频素材处理，而不是鼓励违规搬运。",
        ],
    },
    "1858800927282729363": {
        "theme": "SEO 第 0 篇：选词是流量分配的起点，核心词承接权重，非核心词负责铺量和传权。",
        "logic": [
            "先把 SEO 流程抽象成选词、内容、内链、外链、权重传递，再强调选词是最前置动作。",
            "回应“产品第一还是流量第一”：产品影响变现效率，但多数场景先要拿到可见流量。",
            "把关键词分成核心词与非核心词；核心词放首页/功能页，非核心词放博客/长尾页。",
            "最终目标不是文章本身，而是通过非核心页面把流量和权重导向核心产品页，形成品牌反哺。",
        ],
        "principle": "SEO 内容不是孤立文章，而是一套权重管道；每篇内容都要知道自己在给哪个核心页面输血。",
        "ezremove": [
            "`/watermark-remover/` 承接核心词组：watermark remover、watermark remove、remove watermark。",
            "博客集群承接长尾：remove watermark from image/video、remove logo、remove text、batch watermark remover。",
            "每篇长尾文都必须有明确内链回主工具页，形成“长尾入口 -> 工具体验 -> 注册/付费”的路径。",
        ],
    },
    "1859131744110481458": {
        "theme": "SEO 第 1 篇：新站选词要选易不选难，用相关词和长尾词完成冷启动。",
        "logic": [
            "用 Decopy 的 AI detector 例子说明：大词垂直但难度过高，新站直接打等于没有流量。",
            "提出选词原则：流量大不是价值，能进排名才有价值；难词可以长期做，但冷启动要先找易词。",
            "把核心词换成相关替代词，如 AI humanizer，再用具体问题型长尾词快速拿排名。",
            "强调 SEO 新手不要眼高手低，低流量长尾词能形成早期权重、数据和转化验证。",
        ],
        "principle": "冷启动阶段的关键词价值 = 可排名概率 × 需求相关度 × 转化路径，而不是单纯搜索量。",
        "ezremove": [
            "不要只盯 `watermark remove`，同时做低难度场景词：remove date stamp、remove logo from photo、remove text from image。",
            "做一批问题型页面：Can I remove watermark from a video? How to remove watermark without blur?",
            "用 GSC 看哪些长尾有 impression，再把有效词升级成独立页面或工具入口。",
        ],
    },
    "1861359494988759374": {
        "theme": "SEO 第 2 篇：竞品品牌词可以带流量，但必须满足竞品有品牌、自己产品不明显弱于对方。",
        "logic": [
            "观察到竞品写自家品牌词博客，于是反向写竞品品牌词抢一部分搜索用户。",
            "强调这个技巧不通用：竞品必须已有品牌搜索，否则没有需求；自己产品不能明显更差，否则跳出会伤害站点。",
            "用停留时间和跳出解释为什么博客权重可能下降，严重时会拖累落地页和全站质量信号。",
            "核心不是蹭词本身，而是用户搜竞品时是否存在替代、对比、迁移需求。",
        ],
        "principle": "竞品词页必须服务真实比较意图，不能伪装、误导或只蹭品牌流量。",
        "ezremove": [
            "做 `EzRemove vs Media.io`、`EzRemove vs Pixelbin`、`best watermark remover alternatives` 等对比页。",
            "每篇对比页要有清晰维度：免费额度、图片/视频支持、输出质量、速度、隐私、价格。",
            "不要把竞品页导到弱体验；页面首屏应直接给免费上传入口和替代理由。",
        ],
    },
    "1862088008939528665": {
        "theme": "SEO 第 2.5 篇：内链是站内权重管道，外链是冷启动加速器，优质外链取决于相关性与权重。",
        "logic": [
            "先把复杂链接概念收敛成内链和外链，降低理解成本。",
            "内链适合把长尾页面获得的流量和权重传给主页面，但需要铺量，冷启动较慢。",
            "外链尤其是高权重、强相关来源，可以快速提高站点信任和流量。",
            "用 ChatGPT 给 AI writer 页面外链的极端例子说明：垂直相关与权重同时存在时效果最大。",
        ],
        "principle": "内链负责分配已有资产，外链负责引入外部信任；冷启动不能只靠其中一个。",
        "ezremove": [
            "内部建立工具矩阵链接：watermark-remover、video-watermark-remover、magic-eraser、photo-enhancer 互相传权。",
            "外链目标优先图片编辑、视频剪辑、AI 工具目录、设计教程，而不是泛流量站。",
            "做可被引用资产：watermark remover benchmark、before/after 示例库、版权安全指南。",
        ],
    },
    "1863529073924030787": {
        "theme": "SEO 第 3 篇：外链最重要的是垂直相关；不相关流量带来短停留，可能反向降权。",
        "logic": [
            "用真实 case 说明：一个高曝光站给另一个不垂直站导流，反而造成流量和排名下滑。",
            "原因不是外链无效，而是用户画像错配，跳转后停留过短，质量信号变差。",
            "把外链方法分为付费和非付费，同时提醒付费、互链、ABC 互链都有规则风险。",
            "建议新手从垂直导航站、相关站点、断链修复、客座文章开始。",
        ],
        "principle": "外链不是越大越好，而是越准越好；能带来垂直用户的链接才是资产。",
        "ezremove": [
            "KOL/外链不要投泛娱乐流量，优先投设计、电商卖家、短视频剪辑、AI 图片工具用户。",
            "PR 文章要落在真实场景：去除自己素材水印、整理课程截图、处理商品图、视频剪辑提效。",
            "用 UTM + GA4/GSC 观察每个外链来源的停留、上传、注册和付费，不只看点击量。",
        ],
    },
    "1861705710545092642": {
        "theme": "选上涨潜力词：新站非核心词优先低难度、过千搜索、趋势向上的词。",
        "logic": [
            "给出新站非核心关键词阈值：难度 20% 或以下，搜索量过千就值得测试。",
            "提醒 Semrush 是第三方估算，要结合 Google Trends 观察流量起伏。",
            "重点不是当前最大词，而是有上涨潜力、竞争还没完全拥挤的词。",
        ],
        "principle": "趋势比静态搜索量更重要；早进上涨词，排名成本更低。",
        "ezremove": [
            "监控 `AI watermark remover`、`remove AI watermark`、`remove text from AI image` 等新兴词。",
            "每周拉 Google Trends + GSC impressions，把上升词快速扩成独立页面。",
            "用低难度词验证内容模板，再复制到更大词组。",
        ],
    },
    "1859514896049897754": {
        "theme": "产品第一还是流量第一：产品到行业平均后，运营和营销通常决定增长上限。",
        "logic": [
            "承认产品决定变现下限，但强调互联网产品如果没人看见，再好的体验也无法增长。",
            "指出产品优化有边际递减：从 90 到 95 的成本和收益不一定匹配。",
            "建议大多数情况下先有流量第一思维，但产品低于及格线时流量也没用。",
        ],
        "principle": "增长不是产品和流量二选一，而是先达到可转化产品底线，再把资源转向分发。",
        "ezremove": [
            "先确保上传、处理、下载、免费额度、注册流程不拖后腿，再加大 KOL/SEO。",
            "不要把所有资源花在模型小幅提升；要同步建设内容、PR、渠道、外链和转化漏斗。",
            "用“处理成功率、下载率、注册率、付费率”判断产品是否达到能承接流量的底线。",
        ],
    },
    "1859535615131517384": {
        "theme": "小红书冷启动 1：社媒推荐流不是搜索流，关键是首图、标题、停留与平台风格。",
        "logic": [
            "区分 Google 与小红书：Google 以搜索贯穿始终，小红书更多靠首页推荐分发。",
            "小红书内容不先问关键词难度，而先问首图和标题能否让垂直用户点进去并看完。",
            "被系统识别为优质笔记后才会持续推流，所以平台语感和内容包装比 SEO 选词更重要。",
        ],
        "principle": "不同平台对应不同分发机制；搜索承接需求，推荐制造需求。",
        "ezremove": [
            "KOL 内容不能只套 SEO 标题，要做前后对比、效率提升、真实素材处理过程。",
            "短视频/小红书脚本首屏展示“水印前后对比”，让用户先感知结果，再记住 EzRemove。",
            "把社媒内容的目标设为创造需求和品牌记忆，落地页再承接搜索与转化。",
        ],
    },
    "1859890665968251317": {
        "theme": "小红书冷启动 2：用信息差和内容场景创造需求，冷启动后再做 SEO 更容易。",
        "logic": [
            "Netflix 合租案例中，没有先写 SEO 博客，而是判断社媒冷启动更适合国内市场。",
            "硬营销受平台风控和用户反感影响，所以用剧评内容把 Netflix 需求先创造出来。",
            "核心动作是把用户不知道、没意识到的门槛信息展示出来，先产生兴趣，再承接产品。",
        ],
        "principle": "当用户还没有明确搜索需求时，先用内容创造需求；当需求被教育后，SEO 承接会更轻松。",
        "ezremove": [
            "做“素材处理前后对比”“电商图快速清理”“视频剪辑素材复用”这类需求创造内容。",
            "不要只说工具名；先展示具体痛点：水印遮挡、商品图不干净、视频素材无法复用。",
            "社媒冷启动稳定后，把热门评论问题沉淀为 SEO FAQ 和教程页。",
        ],
    },
    "1872582875465601044": {
        "theme": "小红书人设：利用稀缺身份和生活方式想象，提升内容点击和关注。",
        "logic": [
            "提出“中产人设”更容易涨粉，因为真实中产稀缺，用户对这种生活方式有想象。",
            "强调社媒内容不只是信息，也是在售卖身份、审美、生活方式和心理投射。",
            "计划用个人 IP 继续验证观点，说明这是可实验的运营假设。",
        ],
        "principle": "社媒增长常常来自身份投射；用户关注的不只是功能，还有自己想成为谁。",
        "ezremove": [
            "EzRemove 的 KOL 不只找工具测评号，也可找设计师、电商卖家、剪辑师这类身份型账号。",
            "内容角度从“去水印工具”升级成“高效素材工作流”“专业创作者工具箱”。",
            "品牌视觉和落地页案例要让用户觉得这是专业创作者使用的工具，而不是廉价小工具。",
        ],
    },
    "1862435142884901125": {
        "theme": "闲鱼选词/选品：没有直接数据时，用相邻平台关键词和头部卖家销量做代理判断。",
        "logic": [
            "承认没有直接查闲鱼关键词和流量的平台，于是用淘宝关键词做初筛。",
            "再回到闲鱼搜索结果，观察头部卖家的销量来判断真实需求和竞争格局。",
            "提出生意不可能三角：利润高、竞争小、门槛低不可能同时满足。",
            "把选品逻辑和 SEO 选词打通：尽量找利润高/需求强、竞争相对低的机会。",
        ],
        "principle": "没有完美数据时，用代理数据交叉验证；关键是判断需求、竞争和利润结构。",
        "ezremove": [
            "没有完整关键词数据时，用 Semrush、GSC、Google Suggest、竞品页面、社媒评论交叉判断。",
            "把关键词也当选品：搜索量是需求，KD/SERP 是竞争，CPC/转化是利润信号。",
            "优先做“需求明确、竞争可打、能转化”的页面，而不是只追最大词。",
        ],
    },
}


def load_corpus() -> dict:
    path = PROCESSED / "public_legacy_content_corpus.json"
    if not path.exists():
        raise SystemExit("Run scripts/extract_x_legacy_corpus.py first.")
    return json.loads(path.read_text(encoding="utf-8"))


def type_name(kind: str) -> str:
    return {
        "root": "主贴",
        "thread": "作者补充楼层",
        "comment": "评论",
        "quote": "引用",
        "related": "关联内容",
    }.get(kind, kind)


def item_note(item: dict) -> str:
    text = item.get("text", "")
    kind = item.get("type")
    if kind == "root":
        return "主题入口，负责提出问题、定义讨论范围，并引出后续楼层的完整论证。"
    if kind == "quote":
        return "引用转发，通常代表该主题被作者或外部账号继续扩展为下一篇内容、工具篇或补充观点。"
    if kind == "comment":
        if "图" in text or "无边记" in text:
            return "读者询问内容生产工具，说明流程图、选词图、案例图本身有复用需求。"
        if "权重" in text or "外链" in text:
            return "读者追问权重/外链细节，说明抽象概念需要操作化。"
        if "盈利" in text or "付费" in text or "广告" in text:
            return "读者关心流量如何变现，说明 SEO 内容需要补商业模型。"
        if "硬启动" in text or "冷启动" in text:
            return "读者关心从 0 到 1 的启动动作，适合延展为执行清单。"
        if "学习" in text or "期待" in text or "意犹未尽" in text:
            return "正向反馈，说明系列化内容和专题沉淀有需求。"
        if "垃圾农场" in text:
            return "读者对低质 SEO 有反感，内容必须强调真实价值和合规增长。"
        return "外部互动，提供真实疑问、态度或后续选题线索。"
    if kind == "related":
        return "同一系列或上下游主题，用于补足上下文关系。"
    if "道德" in text or "规则" in text or "风险" in text:
        return "围绕规则边界、风险收益和赚钱认知展开补充。"
    if "核心" in text or "关键词" in text or "长尾" in text:
        return "围绕核心词、非核心词、长尾词和权重传递展开补充。"
    if "难度" in text or "Semrush" in text or "流量" in text:
        return "围绕关键词难度、流量判断和冷启动优先级展开补充。"
    if "竞品" in text or "品牌词" in text or "停留" in text:
        return "围绕竞品品牌词、用户停留和页面质量信号展开补充。"
    if "内链" in text or "外链" in text:
        return "围绕内链传权、外链冷启动和优质外链标准展开补充。"
    if "小红书" in text or "首页" in text or "笔记" in text:
        return "围绕推荐流、首图标题、平台风格和社媒冷启动展开补充。"
    if "Netflix" in text or "需求" in text:
        return "围绕信息差、需求创造和社媒先行的冷启动路径展开补充。"
    if "中产" in text or "人设" in text:
        return "围绕身份投射、人设和社媒关注动机展开补充。"
    if "闲鱼" in text or "淘宝" in text or "选品" in text:
        return "围绕代理数据、选品判断和竞争/利润/门槛三角展开补充。"
    return "作者补充楼层，负责把主贴观点展开成可执行判断。"


def item_line(item: dict) -> str:
    metrics = item.get("metrics") or {}
    metric_bits = []
    if metrics.get("likes") is not None:
        metric_bits.append(f"likes {metrics.get('likes')}")
    if metrics.get("views") is not None:
        metric_bits.append(f"views {metrics.get('views')}")
    suffix = f" ({', '.join(metric_bits)})" if metric_bits else ""
    return f"- [{type_name(item['type'])}] [{item['id']}]({item['url']}) @{item.get('author') or 'unknown'}{suffix}：{item_note(item)}"


def summarize_comments(items: list[dict]) -> list[str]:
    comments = [item for item in items if item["type"] in {"comment", "quote"}]
    if not comments:
        return ["暂无明显外部评论/引用；这一篇更适合作为作者自有方法论沉淀。"]
    bullets = []
    for item in comments:
        text = item.get("text", "")
        author = item.get("author") or "unknown"
        if "图" in text or "无边记" in text:
            insight = "读者关心内容生产工具，说明方法论图/流程图本身有复用价值。"
        elif "权重" in text or "外链" in text:
            insight = "读者追问权重传递或外链细节，说明需要把抽象 SEO 概念落成操作手册。"
        elif "盈利" in text or "付费" in text or "广告" in text:
            insight = "读者关心商业模式，说明 SEO 内容需要同时解释流量如何变现。"
        elif "硬启动" in text or "冷启动" in text:
            insight = "读者关心从 0 到 1 的启动路径，适合补充执行清单。"
        elif "学习" in text or "期待" in text or "意犹未尽" in text:
            insight = "正向反馈证明系列化内容有追更需求，可以沉淀成专题页。"
        elif "垃圾农场" in text:
            insight = "存在对低质 SEO 的反感，后续内容要强调真实价值与合规增长。"
        else:
            insight = "评论提供了用户真实疑问或态度，可转成 FAQ、案例或后续选题。"
        bullets.append(f"- @{author} 在 [{item['id']}]({item['url']}) 的互动：{insight}")
    return bullets


def source_section(source: dict) -> str:
    root_id = source["root_id"]
    analysis = ANALYSIS[root_id]
    items = source["items"]
    counts = Counter(item["type"] for item in items)
    root = next((item for item in items if item["type"] == "root"), None)
    thread_items = [item for item in items if item["type"] == "thread"]
    comment_items = [item for item in items if item["type"] == "comment"]
    quote_items = [item for item in items if item["type"] == "quote"]
    related_items = [item for item in items if item["type"] == "related"]

    parts = [
        f"## {source['label']}",
        "",
        f"- 来源：[{source['source_url']}]({source['source_url']})",
        f"- 抓取结构：主贴 {counts.get('root', 0)}，作者补充楼层 {counts.get('thread', 0)}，评论 {counts.get('comment', 0)}，引用 {counts.get('quote', 0)}，关联内容 {counts.get('related', 0)}",
        f"- 主题：{analysis['theme']}",
        "",
        "### 内容结构拆解",
        "",
    ]
    for idx, bullet in enumerate(analysis["logic"], 1):
        parts.append(f"{idx}. {bullet}")
    parts.extend(["", "### 主贴与楼层脉络", ""])
    if root:
        parts.append(item_line(root))
    for item in thread_items:
        parts.append(item_line(item))

    parts.extend(["", "### 评论与引用洞察", ""])
    parts.extend(summarize_comments(comment_items + quote_items))
    if related_items:
        parts.extend(["", "### 关联内容", ""])
        for item in related_items:
            parts.append(item_line(item))

    parts.extend(["", "### 可复用原则", "", analysis["principle"], "", "### 映射到 EzRemove", ""])
    for action in analysis["ezremove"]:
        parts.append(f"- {action}")
    parts.append("")
    return "\n".join(parts)


def comment_insights_section() -> str:
    return """## 评论/引用总洞察

本次原始数据里可明确拆出的非作者互动包括 13 条评论/回复和 1 条非作者引用；页面级统计中的其他引用对象更多用于系列上下文和关联内容。评论区传递出的重点不是“大家觉得有用”这种泛反馈，而是很具体的执行缺口：

| 评论信号 | 说明 | 对 EzRemove 的落地动作 |
|---|---|---|
| 问流程图和工具 | 用户不只要观点，还想复用图、表、流程 | 把 SEO/PR/GEO 方法做成可下载模板、检查表、工作流图 |
| 问权重传递和外链 | 抽象 SEO 概念需要翻译成操作步骤 | 做内链/外链/长尾页的执行手册，配真实页面结构示例 |
| 问商业模式 | 用户关心流量如何变现，不满足于排名解释 | 每个流量打法都补上转化路径：访问、上传、下载、注册、付费 |
| 问冷启动后怎么做 | 选词只是起点，读者需要从 0 到 1 的硬启动清单 | 为 `watermark remove` 做 30/60/90 天页面、KOL、外链、GSC 迭代计划 |
| 质疑低质 SEO | 有人把关键词打法等同内容农场 | EzRemove 页面必须有真实工具入口、前后对比、限制说明和版权边界 |
| 问无流量外链是否有用 | 用户能识别“链接数”和“有效用户”的区别 | 外链验收从 DA/数量转向垂直相关、停留、上传、导出和辅助转化 |
| 请求长文展开 | X 线程有学习价值，但不适合作为最终知识库 | 把线程整理成飞书文档、GitHub 研究页、FAQ 和执行清单 |

结论：这批评论本质上在要求“把打法产品化”。对 EzRemove 来说，不能只发布一堆围绕 `watermark remove` 的文章；要把文章、工具入口、案例图、模板、FAQ、KOL 内容和转化数据连成一个系统。
"""


def build_markdown(corpus: dict) -> str:
    total_items = sum(len(source["items"]) for source in corpus["sources"])
    total_counts = Counter()
    for source in corpus["sources"]:
        total_counts.update(source["counts"])

    sections = "\n".join(source_section(source) for source in corpus["sources"])

    return f"""# EzRemove `watermark remove` 增长研究：ZaneWynn_SEO 遗产内容完整拆解

> 目标站点：[https://ezremove.ai/](https://ezremove.ai/)
> 目标词：`watermark remove`
> 输出日期：2026-06-08
> 本版目标：不是指标表，而是把 12 篇 X/Twitter 内容、作者补充楼层、评论和引用拆解成可学习、可复刻、可落地到 EzRemove 的增长方法论。
> 公开版说明：完整原始文本保存在本地忽略文件 `data/processed/public_legacy_content_corpus.json` 与 `data/raw` 中；公开页保留链接、结构化拆解、评论/引用洞察和执行映射，不大段搬运原文。

## 总览

本次解析出 {len(corpus["sources"])} 个来源主题、{total_items} 条有效 tweet 对象：主贴 {total_counts.get("root", 0)} 条，作者补充楼层 {total_counts.get("thread", 0)} 条，评论 {total_counts.get("comment", 0)} 条，引用 {total_counts.get("quote", 0)} 条，关联内容 {total_counts.get("related", 0)} 条。

这批内容真正有价值的不是“某个 SEO 技巧”，而是一套从认知、选词、内容、外链、社媒冷启动、代理数据判断到商业化承接的增长系统：

- 认知层：赚钱/创业不是考试，要理解规则、激励和风险收益。
- SEO 层：选词决定入口，长尾负责铺量，内链负责传权，外链负责外部信任。
- 社媒层：推荐流不是搜索流，首图、标题、人设和需求创造更重要。
- 商业层：产品到及格线后，流量和营销决定上限；但产品不能低于承接流量的底线。
- 数据层：没有完美数据时，用 Semrush、GSC、Google Trends、竞品、社媒评论、平台销量做代理验证。

## 术法道器势总拆解

| 层级 | 拆解 | 对 EzRemove 的含义 |
|---|---|---|
| 术 | 选词、长尾页、竞品词、内链、外链、KOL、首图标题、FAQ | 具体执行动作，必须绑定页面和指标 |
| 法 | 先低难度冷启动，再核心词承接；先创造需求，再搜索承接 | 建立内容集群和 PR/KOL 流程，不做一次性活动 |
| 道 | 真实用户价值、风险收益、平台分发机制、产品承接底线 | 不做虚假搜索/点击，用真实需求推品牌搜索 |
| 器 | Semrush、GSC、Trends、GA4、UTM、X 评论、页面模板 | 每周复盘词、页、渠道、转化 |
| 势 | AI 图片/视频编辑需求、电商素材处理、短视频素材复用 | `watermark remove` 不是单词，而是素材处理工作流入口 |

{comment_insights_section()}

{sections}

## 对 EzRemove 的总执行方案

### 1. 页面结构

- 核心页：`/watermark-remover/` 承接 `watermark remover / watermark remove / remove watermark`。
- 视频页：`/video-watermark-remover/` 承接视频场景与短视频剪辑 KOL 流量。
- 长尾页：`remove watermark from image`、`remove watermark from video`、`remove logo from photo`、`remove text from image`、`remove date stamp`、`remove TikTok watermark`。
- 对比页：`EzRemove vs Media.io`、`EzRemove vs Pixelbin`、`best watermark remover alternatives`。
- GEO 页：`What is EzRemove?`、`How EzRemove works`、`EzRemove FAQ`、`Is it legal to remove watermarks?`。

### 2. 内容生产

- 每篇文章必须服务一个明确页面角色：拉新、比较、解释、转化或传权。
- 长尾文章首屏放上传入口或前后对比，不要让用户看完长文才知道工具在哪。
- 评论区出现的问题直接转 FAQ：工具怎么做图、权重怎么传、怎么冷启动、外链有没有流量也有效吗、商业模式是什么。

### 3. KOL/PR

- 用真实 KOL 曝光和免费工具体验制造品牌搜索，不做机器人搜索、虚假点击、账号矩阵规避。
- KOL 垂类优先：电商卖家、设计师、短视频剪辑、AI 工具测评、学生/职场效率。
- 内容角度优先前后对比、工作流节省时间、素材处理成本下降，而不是只喊“去水印”。

### 4. 外链

- 优先垂直站：AI 图片工具目录、视频剪辑教程、设计资源站、电商卖家资源、创作者工具合集。
- 每条外链都用 UTM 看停留、上传、注册，不只看点击。
- 不买泛站群链接；不相关大流量可能带来短停留，反而伤害站点质量信号。

### 5. 30/60/90 天

- 30 天：完成核心页和 10 篇长尾/FAQ；投 20 个小 KOL；建立 GSC/GA4/UTM 周报。
- 60 天：扩展 40-60 篇内容；做 5 个竞品对比页；拿 20 条垂直外链；沉淀评论问题库。
- 90 天：做多语言页面和 GEO 页面；筛出稳定 KOL 渠道；把有效长尾升级成功能落地页。

## 验收标准

- 页面打开后直接看到完整拆解，不再只是 Markdown 链接。
- 每篇来源都包含主贴结构、作者楼层、评论/引用洞察、可复用原则和 EzRemove 映射。
- GitHub Pages、GitHub 仓库、飞书文档三处一致。
- 公开版不大段复制原文，但足够让团队复盘这批内容的增长方法论。
"""


def markdown_to_html(markdown: str) -> str:
    result = subprocess.run(
        ["pandoc", "-f", "gfm", "-t", "html"],
        input=markdown,
        text=True,
        capture_output=True,
        check=True,
    )
    return result.stdout


def build_html(markdown: str) -> str:
    body = markdown_to_html(markdown)
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>EzRemove 增长研究：遗产内容完整拆解</title>
  <style>
    :root {{
      --ink: #111827;
      --muted: #4b5563;
      --line: #d8dee9;
      --accent: #0f766e;
      --bg: #f8fafc;
      --panel: #ffffff;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.72;
    }}
    header {{
      background: #0f172a;
      color: white;
      padding: 44px 24px 34px;
      border-bottom: 4px solid var(--accent);
    }}
    .wrap {{ width: min(1180px, calc(100% - 42px)); margin: 0 auto; }}
    header h1 {{ margin: 0 0 12px; font-size: clamp(32px, 5vw, 56px); line-height: 1.1; letter-spacing: 0; }}
    header p {{ margin: 0; color: #dbeafe; font-size: 18px; max-width: 880px; }}
    main {{ padding: 28px 0 72px; }}
    article {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 34px;
      overflow-wrap: anywhere;
    }}
    h1 {{ font-size: 36px; line-height: 1.18; letter-spacing: 0; }}
    h2 {{ margin-top: 42px; padding-top: 16px; border-top: 1px solid var(--line); font-size: 28px; letter-spacing: 0; }}
    h3 {{ margin-top: 26px; font-size: 21px; }}
    p, li {{ font-size: 16px; }}
    a {{ color: var(--accent); }}
    blockquote {{
      margin: 18px 0;
      padding: 14px 18px;
      border-left: 4px solid var(--accent);
      background: #f0fdfa;
      color: #334155;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      display: block;
      overflow-x: auto;
      margin: 18px 0 26px;
      font-size: 14px;
    }}
    th, td {{
      border: 1px solid var(--line);
      padding: 9px 10px;
      vertical-align: top;
      white-space: nowrap;
      text-align: left;
    }}
    th {{ background: #f1f5f9; }}
    code {{
      background: #eef2f7;
      padding: 2px 5px;
      border-radius: 4px;
      font-size: .92em;
    }}
    @media (max-width: 760px) {{
      article {{ padding: 22px; }}
      h1 {{ font-size: 28px; }}
      h2 {{ font-size: 23px; }}
      th, td {{ white-space: normal; min-width: 120px; }}
    }}
  </style>
</head>
<body>
  <header>
    <div class="wrap">
      <h1>遗产内容完整拆解</h1>
      <p>12 篇 X/Twitter 内容、作者楼层、评论与引用，拆成 EzRemove 可执行的 SEO / PR / GEO 增长系统。</p>
    </div>
  </header>
  <main class="wrap">
    <article>
{body}
    </article>
  </main>
</body>
</html>
"""


def build_readme(corpus: dict, total_items: int, total_counts: Counter) -> str:
    return f"""# EzRemove `watermark remove` 增长研究

本仓库保存对 ZaneWynn_SEO 12 篇 X/Twitter 遗产内容的结构化拆解，并映射到 EzRemove 的 `watermark remove` 增长执行方案。

- 完整 Markdown 文档：[docs/ezremove-watermark-remove-growth-research.md](docs/ezremove-watermark-remove-growth-research.md)
- GitHub Pages 入口：[docs/index.html](docs/index.html)
- 目标站点：[https://ezremove.ai/](https://ezremove.ai/)

## 本版内容

- 来源主题：{len(corpus["sources"])} 个
- 有效 tweet 对象：{total_items} 条
- 主贴：{total_counts.get("root", 0)} 条
- 作者补充楼层：{total_counts.get("thread", 0)} 条
- 评论：{total_counts.get("comment", 0)} 条
- 引用：{total_counts.get("quote", 0)} 条
- 关联内容：{total_counts.get("related", 0)} 条

公开版保留链接、结构化拆解、评论/引用洞察和 EzRemove 执行映射；完整原始文本只保存在本地忽略目录 `data/raw` 与 `data/processed/public_legacy_content_corpus.json`。
"""


def main() -> int:
    DOCS.mkdir(parents=True, exist_ok=True)
    SITE.mkdir(parents=True, exist_ok=True)
    corpus = load_corpus()
    total_items = sum(len(source["items"]) for source in corpus["sources"])
    total_counts = Counter()
    for source in corpus["sources"]:
        total_counts.update(source["counts"])
    markdown = build_markdown(corpus)
    metrics = {
        "generated_at": "2026-06-08",
        "source_count": len(corpus["sources"]),
        "stats": corpus["stats"],
    }
    (DOCS / "ezremove-watermark-remove-growth-research.md").write_text(markdown, encoding="utf-8")
    (ROOT / "README.md").write_text(build_readme(corpus, total_items, total_counts), encoding="utf-8")
    html_doc = build_html(markdown)
    (DOCS / "index.html").write_text(html_doc, encoding="utf-8")
    (SITE / "index.html").write_text(html_doc, encoding="utf-8")
    (PROCESSED / "public_breakdown_metrics.json").write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(DOCS / "ezremove-watermark-remove-growth-research.md")
    print(DOCS / "index.html")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
