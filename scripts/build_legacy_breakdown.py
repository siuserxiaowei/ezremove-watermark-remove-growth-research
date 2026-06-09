#!/usr/bin/env python3
"""Build the full legacy-content breakdown report and inline HTML page."""

from __future__ import annotations

import html
import json
import sys
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


ITEM_BREAKDOWNS = {
    "1857705646172631354": {"point": "用“优秀宿舍是否帮助就业”的提问切入，指出学生评价体系和真实赚钱体系不是一回事。", "role": "开场冲突，把读者从校园规则拉到商业规则。", "action": "内容开头用一个具体误区引出认知差，比直接讲大道理更容易被读下去。"},
    "1857705649452326975": {"point": "重新定义赚钱：不是大量时间换钱，而是靠认知差、信息差和资源配置获得非线性收益。", "role": "先定义核心概念，避免后文把打工、赚钱、创业混在一起。", "action": "EzRemove 内容也要先定义用户收益：省时间、降低素材处理成本，而不是只说功能。"},
    "1857705652426363227": {"point": "承认普通人很难绕开打工，但打工阶段要积累认知和能力，为后续真正赚钱做准备。", "role": "缓和观点，避免把“打工不是赚钱”理解成否定工作。", "action": "教程内容要给过渡路径：先用免费工具提升效率，再逐步进入付费/专业工作流。"},
    "1857705655324270740": {"point": "提出第一种要丢掉的思维是道德洁癖，并用大学期间多账号抢鞋卖鞋说明资源竞争。", "role": "用争议案例把“规则内竞争”和“资源有限”讲具体。", "action": "增长策略要识别规则边界，但不能把侵权、虚假流量这类风险包装成技巧。"},
    "1857705658596078054": {"point": "补充炒鞋案例的收益和舆论争议，再转入第二个要丢掉的心智：好学生思维。", "role": "从道德压力过渡到规则服从，形成两类心智障碍。", "action": "复盘打法时同时写收益和争议，团队才知道哪些动作可复制、哪些动作要避开。"},
    "1857705661280497864": {"point": "指出中式教育训练的是遵守既定规则；赚钱更需要理解、利用、试探甚至突破规则。", "role": "把好学生思维和商业增长思维正式区分。", "action": "做 SEO/GEO 不只按教程填表，要理解 Google、社媒和用户决策机制。"},
    "1857705663847415889": {"point": "用酒店协议价案例说明：规则套利能带来实际优惠，但一定违反平台或商家规则。", "role": "给“利用规则”一个生活化样本，让抽象观点落地。", "action": "任何增长动作都要标注规则性质：白帽、灰区、违规、不可做。"},
    "1857705709930209404": {"point": "强调协议价套利会带来账号审计和封号风险，关键不是技巧，而是风险收益比判断。", "role": "把案例从“怎么占便宜”拉回“如何计算风险”。", "action": "KOL、外链、竞品词、版权边界都要做风险收益表，不只看短期流量。"},
    "1857705712790679782": {"point": "总结道德洁癖和好学生思维本质相近，放下这两点才开始进入赚钱状态。", "role": "收束整篇价值观，给出明确结论。", "action": "把价值观内容沉淀成团队增长原则：理解规则、计算风险、承担后果。"},

    "1858800927282729363": {"point": "SEO 系列第 0 篇，从流程图切入，强调选词是 SEO 最早也最重要的动作。", "role": "建立系列入口和基础框架。", "action": "EzRemove 先定核心词、长尾词和页面分工，再写内容。"},
    "1858800931665797596": {"point": "回应产品第一还是流量第一：产品影响变现，但多数场景先要把流量入口选对。", "role": "解释为什么把选词放在产品判断前。", "action": "把 `watermark remove` 页面当流量入口设计，同时保留产品转化指标。"},
    "1858800934530543679": {"point": "把关键词分为核心和非核心；核心词给首页/功能页，非核心词给博客或辅助落地页。", "role": "给出页面架构规则。", "action": "核心页承接 `watermark remover`，博客承接图片、视频、平台、场景长尾。"},
    "1858800936933806287": {"point": "说明非核心页面最终要把权重和流量传给产品，达到规模后再形成品牌反哺。", "role": "把内容生产和品牌增长连接起来。", "action": "每篇教程都要有内链和 CTA，不做孤立流量页。"},
    "1859079567266509022": {"point": "作者补充流程图制作工具是 Apple 无边记。", "role": "回应读者对内容资产制作方法的需求。", "action": "把流程图、选词表、内链图做成可下载模板，作为 lead magnet。"},
    "1859483186100912378": {"point": "读者质疑做词容易变成低质内容农场。", "role": "提供反面约束，提醒关键词策略不能只堆页面。", "action": "EzRemove 的 SEO 页必须有真实工具、示例、限制说明和版权边界。"},
    "1858911845232636291": {"point": "读者给出正向学习反馈。", "role": "证明基础向 SEO 内容有受众。", "action": "把系列整理成知识库，而不是只留在 X 线程里。"},
    "1858918866036158537": {"point": "读者追问流程图用什么工具做。", "role": "说明图表和流程资产本身能引发互动。", "action": "提供可复用图表模板，带动收藏、分享和品牌搜索。"},
    "1859114539897549227": {"point": "读者想学习权重传递的参考资料。", "role": "暴露执行层缺口：概念知道了，但不知道怎么系统学。", "action": "新增内链、外链、权重传递的教程页和检查清单。"},
    "1858912156869423157": {"point": "外部引用表达希望继续看更多 SEO 分享。", "role": "验证系列化内容有延展空间。", "action": "按专题连续发，而不是一次性发布单篇。"},
    "1859131744110481458": {"point": "引用承接到第 1 篇：用 AI detector 案例讲选易不选难。", "role": "把第 0 篇的选词框架推进到实际案例。", "action": "先打低难度长尾，再回攻 `watermark remove` 核心词。"},
    "1861708834051670418": {"point": "引用扩展到工具篇：Semrush、Google Trends、MozBar 分别看量、趋势、难度。", "role": "补齐选词工具层。", "action": "建立每周关键词看板，用搜索量、KD、趋势和 GSC impression 共同决策。"},

    "1859131744110481458": {"point": "用 AI 内容检测/优化产品举例，指出新站直接打 ai detector 这类大词难度过高。", "role": "用真实产品场景解释为什么不能只看搜索量。", "action": "EzRemove 不只打 `watermark remove`，先找能排得动的场景词。"},
    "1859131747944071495": {"point": "给出原则：选易不选难；难词不是不能做，但要看投入、团队能力和收益评估。", "role": "提出冷启动阶段的选词判断标准。", "action": "把关键词按 KD、转化意图、页面成本分层排期。"},
    "1859131752733962646": {"point": "把 AI detector 换成 AI humanizer，并用更具体的长尾问题快速切入排名。", "role": "演示如何从难词切到相关词和问题型长尾。", "action": "围绕 `remove watermark from image/video`、`remove logo/text` 建长尾集群。"},
    "1859131756009714068": {"point": "提醒不要眼高手低：低流量词只要能排名就有价值，难词打不上等于没有流量。", "role": "修正新手只追大词的错误预期。", "action": "用小词跑模板、拿 impression，再复制到大词。"},
    "1859131758715040041": {"point": "预告后续会分享选词工具和综合判断流量、难度的方法。", "role": "给系列内容留钩子。", "action": "把研究文档拆成工具篇、方法篇、案例篇连续发布。"},
    "1859394615025205390": {"point": "读者追问案例站如何盈利。", "role": "暴露 SEO 文章缺少商业闭环解释。", "action": "每个流量案例都补上变现路径：免费、付费、广告、订阅或转化。"},
    "1922163716071559216": {"point": "读者请求把长线程展开成可读长文。", "role": "说明 X 线程需要二次整理成知识库。", "action": "飞书/GitHub 页面要承担长期归档，而不是只放链接。"},
    "1861413425517322640": {"point": "读者反馈自己的站点很难优化。", "role": "体现诊断/审计类内容有需求。", "action": "做“为什么你的网站排不上去”的 teardown 模板。"},
    "1861359494988759374": {"point": "引用承接到第 2 篇：用竞品品牌词起量，但强调不通用。", "role": "把选词从长尾扩展到竞品需求。", "action": "做对比页时必须服务真实替代和比较意图。"},
    "1858800927282729363": {"point": "关联回第 0 篇，补足选词框架的上游背景。", "role": "建立系列上下文。", "action": "专题页互相内链，让读者按顺序学习。"},

    "1861359494988759374": {"point": "提出轻量起量技巧：写竞品品牌词博客，抢一部分已有品牌搜索需求。", "role": "把 SEO 选词从通用词扩展到竞品词。", "action": "做 `EzRemove vs X`、`best watermark remover alternatives`，但必须诚实比较。"},
    "1861359500109947332": {"point": "强调两个条件：竞品要已有品牌搜索；自己产品不能明显弱，否则流量上来后权重会掉。", "role": "给竞品词打法设置可用边界。", "action": "只做能承接的竞品词，对比页首屏放真实产品能力和限制。"},
    "1861359503821955113": {"point": "解释停留时间过短会让博客降权；如果落地页体验差，还可能拖累全站。", "role": "把用户行为信号和网站权重风险讲清楚。", "action": "对比页必须提高停留和转化：表格、样例、上传入口、FAQ。"},
    "1861408692022792562": {"point": "读者希望继续讲选词后如何硬启动。", "role": "说明选词之后的页面、外链、索引、转化步骤仍是缺口。", "action": "新增 `after keyword research` 执行清单。"},
    "1866068405645914545": {"point": "引用把品牌词打法迁移到 AI Video / Sora 场景，说明可找主核心词和品牌词突破口。", "role": "展示打法跨品类迁移。", "action": "EzRemove 可关注平台/工具相关新词，但避免冒充或误导。"},
    "1862088008939528665": {"point": "引用承接到第 2.5 篇，进入内链/外链和权重传递。", "role": "把竞品词之后的权重问题展开。", "action": "对比页和长尾页必须接入内链系统。"},
    "1859131744110481458": {"point": "关联回第 1 篇，说明竞品品牌词仍属于选词体系的一部分。", "role": "维持系列知识结构。", "action": "在文档中把所有战术归回关键词分层。"},

    "1862088008939528665": {"point": "把复杂链接概念收敛到内链和外链：内链连站内，外链连外站，本质都是传流量和权重。", "role": "降低链接建设的理解门槛。", "action": "先让团队统一语言：哪些链接用于传权，哪些用于获客。"},
    "1862088013825855634": {"point": "用 AI writer 说明内链：长尾页先进首页，再把流量和权重传给主落地页。", "role": "解释内链为什么依赖长尾铺量。", "action": "所有长尾教程链接回 `/watermark-remover/` 和相关工具页。"},
    "1862088017248387312": {"point": "指出内链冷启动慢，优质外链能更快带来高权重和流量；用 ChatGPT 外链做极端例子。", "role": "说明外链是冷启动加速器。", "action": "优先争取 AI 工具目录、编辑教程、垂直资源页的上下文链接。"},
    "1862088020104806404": {"point": "定义优质外链的两个关键维度：垂直和权重，并预告后续会讲 case。", "role": "为下一篇垂直外链埋伏笔。", "action": "外链候选必须同时看相关性、页面权重和真实用户质量。"},
    "1863529073924030787": {"point": "引用承接到第 3 篇：用真实 case 说明不垂直外链会伤站。", "role": "从概念进入反面案例。", "action": "不要把泛流量站当高质量外链。"},
    "1861359494988759374": {"point": "关联回竞品词篇，说明链接和竞品页都是权重/流量系统的一部分。", "role": "连接选词和链接建设。", "action": "竞品页、长尾页、核心页要统一内链结构。"},

    "1863529073924030787": {"point": "用两个自有网站的 case 说明：高曝光网站给不垂直站导流，反而导致目标站排名和流量下降。", "role": "以反例证明外链不只看流量大小。", "action": "PR/KOL 只找真正会使用图片/视频处理工具的人群。"},
    "1863529078550384804": {"point": "复盘失败原因：两个网站功能和用户画像不垂直，跳转用户停留太短，被判断为低质量站。", "role": "定位问题在用户匹配，不是外链动作本身。", "action": "外链验收看 engaged session、上传、导出，不只看点击。"},
    "1863529082799182173": {"point": "外链建设优先看垂直；方法分付费和非付费，付费见效快但违反 Google 规则。", "role": "给出外链路径和风险分类。", "action": "建立白帽外链清单：相关站联系、断链修复、客座文章、垂直目录。"},
    "1863529085731057924": {"point": "提醒互链、付费、ABC 互链都有惩罚风险，新手可先提交垂直导航站。", "role": "给新手一个低风险起步动作。", "action": "先做 AI/image/video 目录站，再逐步做资源页和教程合作。"},
    "1864588978009329972": {"point": "作者回复：无点击外链可能有一点效果，但不算优质；没有点击也不会因停留短而降权。", "role": "细化“有链接但无流量”的判断。", "action": "无流量链接可作为补充，不应作为主要外链资产。"},
    "1864489960562413651": {"point": "读者追问评论区或低点击位置加外链是否有效。", "role": "把外链质量问题推到更细的执行层。", "action": "外链评估增加位置可见度、点击意图和页面上下文。"},
    "1862088008939528665": {"point": "关联回第 2.5 篇，补足内链/外链基础概念。", "role": "连接基础概念与真实 case。", "action": "在文档里先讲概念，再讲失败案例和检查表。"},

    "1861705710545092642": {"point": "给新站非核心词阈值：KD 20% 以下、搜索量过千可测试；还要用 Google Trends 看趋势。", "role": "把选词标准量化。", "action": "EzRemove 每周筛低 KD、上升趋势、强场景相关词。"},

    "1859514896049897754": {"point": "提出产品第一还是流量第一的问题，并给出倾向：多数情况下流量第一，产品决定下限，流量决定上限。", "role": "建立资源分配原则。", "action": "产品到及格线后，不要只磨功能，要同步拉 SEO/KOL/PR。"},
    "1859514899334131861": {"point": "互联网打破地缘限制，能不能被用户看到往往比产品是否从 90 分到 95 分更重要。", "role": "解释为什么产品优化有边际递减。", "action": "把研发资源留给关键转化阻塞点，其余投入分发。"},
    "1859514901800349807": {"point": "建议建立流量第一思维：产品达到行业平均后，更多精力放运营和营销；ChatGPT 这类变革产品是例外。", "role": "给出一般规则和例外。", "action": "用上传成功率、下载率、复用率判断是否已到可放量状态。"},
    "1859514905587827107": {"point": "补充不是二极管：如果产品低于 60 分或有严重缺陷，再高流量也没用。", "role": "给流量第一设底线。", "action": "上线前先修阻断流程，再投 KOL 和外链。"},
    "1858800931665797596": {"point": "关联回 SEO 第 0 篇中对产品/流量优先级的讨论。", "role": "把战略判断和选词动作连接起来。", "action": "页面优先级按流量机会和产品承接能力共同决定。"},

    "1859535615131517384": {"point": "小红书第 1 篇：提醒不要直接用 SEO 逻辑运营小红书，根因是算法类型不同。", "role": "先纠正跨平台方法误用。", "action": "社媒内容不要套 Google 标题，要适配推荐流。"},
    "1860684169615171613": {"point": "作者回复 SEO 应算运营岗。", "role": "回应角色定位问题。", "action": "团队分工上把 SEO 放进增长/运营闭环，而不是孤立内容岗。"},
    "1859535620290314679": {"point": "解释 Google 依赖搜索动作，小红书更多靠首页推荐；关键是首图、标题和停留。", "role": "建立平台分发差异。", "action": "小红书/KOL 内容首屏必须展示前后对比和结果。"},
    "1859535624069587275": {"point": "被判定为优质笔记后会持续推流；首图信息量和小红书体标题决定点击。", "role": "解释推荐流起量机制。", "action": "给每个 KOL brief 配封面、标题、前 3 秒脚本。"},
    "1859535626422583787": {"point": "目标不是让用户搜索到笔记，而是进入首页后让垂直用户点击并读完。", "role": "明确小红书冷启动目标。", "action": "社媒 KPI 看完读、互动、品牌记忆和后续搜索，不只看排名。"},
    "1859758143770853816": {"point": "读者验证：自己的小红书流量多数来自发现页，高流量内容都有平台风格文案图片。", "role": "外部案例支持作者判断。", "action": "把平台原生感作为 KOL 质量检查项。"},
    "1860678864630092146": {"point": "读者询问 SEO 是否属于运营岗位。", "role": "暴露新人对职能边界的困惑。", "action": "教程里补 SEO、内容、增长、运营的岗位关系。"},
    "1859890665968251317": {"point": "引用承接到小红书第 2 篇：从算法差异进入信息差和创造需求。", "role": "把平台机制推进到营销策略。", "action": "社媒先教育需求，再让 SEO 承接搜索。"},

    "1859890665968251317": {"point": "小红书第 2 篇：Netflix 合租项目冷启动，不先写 SEO，而是判断社媒更适合。", "role": "用项目 case 说明渠道选择要看市场和用户认知。", "action": "EzRemove 可先用社媒展示素材处理场景，再承接搜索。"},
    "1859890670464573705": {"point": "国内市场有小红书优先级，但硬广受风控和反感影响，因此要创造需求。", "role": "解释为什么不用直接营销。", "action": "KOL 内容先讲痛点和结果，不要一上来硬推工具。"},
    "1859890673643815118": {"point": "Netflix 老用户会自己找合租，但国内更多人不知道 Netflix；要通过剧评展示门槛信息来创造需求。", "role": "把“创造需求”具体化。", "action": "展示水印遮挡、商品图不干净、视频素材难复用，让用户意识到需求。"},
    "1859890676043001964": {"point": "只要需求判断正确，社媒中短期营销能完成冷启动；之后再做 SEO 会更容易。", "role": "给出社媒先行、SEO 后承接的路径。", "action": "KOL 评论和搜索增长稳定后，把问题沉淀为 SEO FAQ。"},
    "1866780845656473877": {"point": "引用分析竞品 GamsGo：高流量但主要靠品牌词，服务问题会放大用户负反馈。", "role": "补充品牌词和服务承接风险。", "action": "品牌搜索拉起来后，客服、交付、退款和体验不能掉链子。"},
    "1859535615131517384": {"point": "关联回小红书第 1 篇的平台算法差异。", "role": "保持小红书系列上下文。", "action": "先学平台机制，再设计需求创造内容。"},

    "1872582875465601044": {"point": "建议做小红书副业可立“中产”人设，通过生活方式、消费观和适度优越感吸粉。", "role": "从内容机制扩展到人设和身份投射。", "action": "EzRemove KOL 可选创作者、设计师、卖家等身份型账号。"},
    "1872582878531649674": {"point": "解释中产稀缺带来的想象和渴望，所以中产人设在小红书讨喜，但真实性常不足。", "role": "给出人设有效的社会心理原因。", "action": "人设营销要用真实工作流支撑，避免虚假包装。"},
    "1872582880964321424": {"point": "作者计划做个人 IP 账号验证观点。", "role": "把判断变成可实验假设。", "action": "KOL/账号策略要小样本测试，而不是一次押注。"},
    "1874259808653820166": {"point": "读者反驳：这种人设可能让用户误判社会现实。", "role": "提示人设营销的副作用。", "action": "品牌内容要做身份吸引，但不要制造过度焦虑或虚假优越。"},

    "1862435142884901125": {"point": "闲鱼选词/选品没有直接工具，可用淘宝关键词做需求代理，再看长尾衍生。", "role": "提出没有完美数据时的替代验证法。", "action": "EzRemove 关键词也用 Semrush、GSC、Suggest、社媒评论交叉验证。"},
    "1862435149746774053": {"point": "提出生意不可能三角：利润高、竞争小、门槛低不可能同时满足。", "role": "把选品约束抽象成决策框架。", "action": "选关键词同样看需求、竞争、转化价值三者取舍。"},
    "1862435155992060201": {"point": "淘宝关键词只能初筛，还要回闲鱼看头部卖家销量；AJ 例子说明需求大但竞争也大。", "role": "展示代理数据如何回到真实平台验证。", "action": "内容机会必须用 SERP、竞品页、GSC 数据二次确认。"},
    "1862435160882651276": {"point": "AJ 这类生意门槛低、利润中等、竞争大；最好找利润高和竞争低的组合，逻辑类似 SEO 选词。", "role": "把电商选品和 SEO 选词统一。", "action": "优先做高意图、低竞争、可转化的场景页。"},
    "1862518796604612720": {"point": "作者回复会持续分享相关想法。", "role": "维护系列预期。", "action": "把评论反馈转成后续内容 backlog。"},
    "1862498562543952342": {"point": "读者表示意犹未尽，希望更详细。", "role": "验证闲鱼/代理数据方法有进一步拆解需求。", "action": "补一篇“没有关键词工具时如何做代理调研”的教程。"},
    "1856971285794099659": {"point": "关联到闲鱼运营旧帖：用基础 SEO/产品运营思维做闲鱼有降维优势。", "role": "补足作者在闲鱼场景的长期经验。", "action": "把 SEO 方法迁移到站外平台：标题、需求、转化、复购。"},
}

ITEM_BREAKDOWNS.update(
    {
        "1862088008939528665": {
            "point": "把复杂链接概念收敛到内链和外链：内链连站内，外链连外站，本质都是传流量和权重。",
            "role": "降低链接建设的理解门槛。",
            "action": "先让团队统一语言：哪些链接用于传权，哪些用于获客。",
        },
        "1859535615131517384": {
            "point": "小红书第 1 篇：提醒不要直接用 SEO 逻辑运营小红书，根因是算法类型不同。",
            "role": "先纠正跨平台方法误用。",
            "action": "社媒内容不要套 Google 标题，要适配推荐流。",
        },
        "1861359494988759374": {
            "point": "提出轻量起量技巧：写竞品品牌词博客，抢一部分已有品牌搜索需求。",
            "role": "把 SEO 选词从通用词扩展到竞品词。",
            "action": "做 `EzRemove vs X`、`best watermark remover alternatives`，但必须诚实比较。",
        },
    }
)


def load_corpus() -> dict:
    path = PROCESSED / "public_legacy_content_corpus.json"
    if not path.exists():
        raise SystemExit("Run scripts/extract_x_legacy_corpus.py first.")
    return json.loads(path.read_text(encoding="utf-8"))


def archived_media_files() -> set[str]:
    media_dir = DOCS / "assets" / "x-media"
    if not media_dir.exists():
        return set()
    return {path.name for path in media_dir.glob("*.jpg")}


def corpus_media_files(corpus: dict) -> set[str]:
    return {
        media.get("file_name")
        for source in corpus["sources"]
        for item in source["items"]
        for media in (item.get("media") or [])
        if media.get("file_name")
    }


def type_name(kind: str) -> str:
    return {
        "root": "主贴",
        "thread": "作者补充楼层",
        "comment": "评论",
        "quote": "引用",
        "related": "关联内容",
    }.get(kind, kind)


def item_note(item: dict) -> str:
    if item.get("id") in ITEM_BREAKDOWNS:
        return ITEM_BREAKDOWNS[item["id"]]["point"]
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


def item_role(item: dict) -> str:
    if item.get("id") in ITEM_BREAKDOWNS:
        return ITEM_BREAKDOWNS[item["id"]]["role"]
    kind = item.get("type")
    if kind == "root":
        return "提出主题和问题框架。"
    if kind == "thread":
        return "补充主贴论证。"
    if kind == "comment":
        return "提供读者疑问、反驳或需求信号。"
    if kind == "quote":
        return "把原主题扩展到后续话题或外部传播。"
    return "补足上下游背景。"


def item_action(item: dict) -> str:
    if item.get("id") in ITEM_BREAKDOWNS:
        return ITEM_BREAKDOWNS[item["id"]]["action"]
    kind = item.get("type")
    if kind == "comment":
        return "转成 FAQ、选题或检查清单。"
    if kind == "quote":
        return "作为系列内容的延伸入口。"
    return "沉淀为可执行判断。"


def md_cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", "<br>")


def item_original_text(item: dict) -> str:
    if item.get("type") in {"root", "thread", "related"}:
        return "公开页不复制长原文；见链接、逐条拆解和本地 raw 归档。"
    text = item.get("text") or ""
    if len(text) <= 48:
        return text
    return text[:48].rstrip() + "..."


def visible_public_excerpt(record: dict) -> str:
    matched_type = record.get("matched_type")
    if matched_type in {"root", "thread", "related"}:
        return f"已看到{type_name(matched_type)}内容；公开页不复制长原文，见链接和拆解。"
    excerpt = record.get("excerpt") or ""
    if matched_type in {"comment", "quote"}:
        return excerpt if len(excerpt) <= 48 else excerpt[:48].rstrip() + "..."
    if len(excerpt) <= 36:
        return excerpt or "-"
    return "可见正文/页面块已归档；公开页只保留结构化线索。"


def media_markdown(source: dict) -> list[str]:
    rows = []
    for item in source["items"]:
        for idx, media in enumerate(item.get("media") or [], 1):
            local = f"assets/x-media/{media['file_name']}"
            caption = f"{type_name(item['type'])} [{item['id']}]({item['url']}) 配图 {idx}"
            if media.get("width") and media.get("height"):
                caption += f"（{media['width']}x{media['height']}）"
            rows.extend(
                [
                    f"![{caption}]({local})",
                    "",
                    f"- {caption}；原图来源：[{media.get('id')}]({media.get('url')})",
                    "",
                ]
            )
    if not rows:
        return ["暂无抓取到配图或视频媒体。"]
    return rows


def orphan_media_markdown(corpus: dict) -> list[str]:
    orphan_files = sorted(archived_media_files() - corpus_media_files(corpus))
    if not orphan_files:
        return []
    rows = [
        "## 历史已归档图片补充",
        "",
        "以下图片是历史抓取时已经归档到仓库的 X 媒体文件；本轮 X payload 没有重新返回对应媒体对象，但文件仍保留并展示，避免遗漏已保存素材。",
        "",
    ]
    for file_name in orphan_files:
        tweet_id = file_name.split("_", 1)[0]
        rows.extend(
            [
                f"![历史归档图片 {file_name}](assets/x-media/{file_name})",
                "",
                f"- 关联 tweet id：[{tweet_id}](https://x.com/i/web/status/{tweet_id})；本地文件：`assets/x-media/{file_name}`",
                "",
            ]
        )
    return rows


def visible_archive_markdown(source: dict) -> list[str]:
    archive = source.get("visible_archive") or {}
    records = archive.get("records") or []
    header = [
        f"逐屏滚动快照 {archive.get('snapshot_count', 0)} 份；可见文章块 {archive.get('article_block_count', 0)} 个；去重后可见内容块 {archive.get('unique_block_count', 0)} 个。",
        "",
    ]
    if not records:
        return header + ["暂无逐屏可见内容快照；需要重新运行浏览器抓取脚本。"]
    rows = [
        "| 页面 | 屏次/位置 | 匹配对象 | 公开短线索 | 读完后的拆解 |",
        "|---|---|---|---|---|",
    ]
    for record in records:
        matched = "-"
        if record.get("matched_id"):
            matched = f"[{type_name(record.get('matched_type'))} {record['matched_id']}]({record.get('matched_url')})"
        rows.append(
            "| "
            + " | ".join(
                [
                    md_cell(record.get("page") or "-"),
                    md_cell(f"第 {record.get('step')} 屏 / y={record.get('scroll_y')}"),
                    md_cell(matched),
                    md_cell(visible_public_excerpt(record)),
                    md_cell(record.get("insight") or "-"),
                ]
            )
            + " |"
        )
    return header + rows


def item_line(item: dict) -> str:
    metrics = item.get("metrics") or {}
    metric_bits = []
    if metrics.get("likes") is not None:
        metric_bits.append(f"likes {metrics.get('likes')}")
    if metrics.get("views") is not None:
        metric_bits.append(f"views {metrics.get('views')}")
    suffix = f" ({', '.join(metric_bits)})" if metric_bits else ""
    return f"- [{type_name(item['type'])}] [{item['id']}]({item['url']}) @{item.get('author') or 'unknown'}{suffix}：{item_note(item)}"


def item_table(items: list[dict]) -> list[str]:
    if not items:
        return ["暂无。"]
    rows = [
        "| 类型 | 链接 | 互动 | 公开短线索/评论线索 | 内容要点 | 这一层的作用 | 可复用动作 |",
        "|---|---|---:|---|---|---|---|",
    ]
    for item in items:
        metrics = item.get("metrics") or {}
        likes = metrics.get("likes")
        views = metrics.get("views")
        metric = []
        if likes is not None:
            metric.append(f"likes {likes}")
        if views is not None:
            metric.append(f"views {views}")
        rows.append(
            "| "
            + " | ".join(
                [
                    md_cell(type_name(item["type"])),
                    md_cell(f"[{item['id']}]({item['url']})"),
                    md_cell("<br>".join(metric) if metric else "-"),
                    md_cell(item_original_text(item)),
                    md_cell(item_note(item)),
                    md_cell(item_role(item)),
                    md_cell(item_action(item)),
                ]
            )
            + " |"
        )
    return rows


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
        f"- 媒体：已归档 {source.get('media_count', 0)} 个图片/媒体文件",
        f"- 逐屏可见归档：快照 {source.get('visible_archive', {}).get('snapshot_count', 0)} 份，去重内容块 {source.get('visible_archive', {}).get('unique_block_count', 0)} 个",
        f"- 主题：{analysis['theme']}",
        "",
        "### 配图/媒体归档",
        "",
    ]
    parts.extend(media_markdown(source))
    parts.extend([
        "",
        "### 浏览器逐屏可见内容归档",
        "",
    ])
    parts.extend(visible_archive_markdown(source))
    parts.extend([
        "",
        "### 全文结构拆解",
        "",
    ])
    for idx, bullet in enumerate(analysis["logic"], 1):
        parts.append(f"{idx}. {bullet}")
    parts.extend(["", "### 主贴与楼层逐条拆解", ""])
    if root:
        parts.extend(item_table([root] + thread_items))
    else:
        parts.extend(item_table(thread_items))

    parts.extend(["", "### 评论与引用洞察", ""])
    parts.extend(item_table(comment_items + quote_items))
    if related_items:
        parts.extend(["", "### 关联内容", ""])
        parts.extend(item_table(related_items))

    parts.extend(["", "### 可复用原则", "", analysis["principle"], "", "### 映射到 EzRemove", ""])
    for action in analysis["ezremove"]:
        parts.append(f"- {action}")
    parts.append("")
    return "\n".join(parts)


def comment_insights_section(total_counts: Counter) -> str:
    return f"""## 评论/引用总洞察

本次原始数据里可明确拆出的互动包括评论/回复 {total_counts.get("comment", 0)} 条、引用 {total_counts.get("quote", 0)} 条；页面级引用对象里既有非作者引用，也有作者用来承接下一篇的系列引用。评论区传递出的重点不是“大家觉得有用”这种泛反馈，而是很具体的执行缺口：

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
    total_media = sum(source.get("media_count", 0) for source in corpus["sources"])
    unique_media = corpus_media_files(corpus)
    archived_media = archived_media_files()
    total_unique_media = len(unique_media | archived_media)
    orphan_media_count = len(archived_media - unique_media)
    total_counts = Counter()
    total_snapshots = 0
    total_visible_blocks = 0
    total_unique_visible_blocks = 0
    for source in corpus["sources"]:
        total_counts.update(source["counts"])
        archive = source.get("visible_archive") or {}
        total_snapshots += archive.get("snapshot_count", 0)
        total_visible_blocks += archive.get("article_block_count", 0)
        total_unique_visible_blocks += archive.get("unique_block_count", 0)

    sections = "\n".join(source_section(source) for source in corpus["sources"])

    return f"""# EzRemove `watermark remove` 增长研究：ZaneWynn_SEO 遗产内容完整拆解

> 目标站点：[https://ezremove.ai/](https://ezremove.ai/)
> 目标词：`watermark remove`
> 输出日期：2026-06-08
> 本版目标：不是指标表，而是把 12 篇 X/Twitter 内容、作者补充楼层、评论、引用和浏览器逐屏可见内容拆解成可学习、可复刻、可落地到 EzRemove 的增长方法论。
> 公开版说明：完整原始响应和逐屏 DOM 快照保存在本地忽略文件 `data/processed/public_legacy_content_corpus.json` 与 `data/raw` 中；公开页保留链接、配图、公开短线索、评论/引用线索、结构化拆解和执行映射。

## 总览

本次解析出 {len(corpus["sources"])} 个来源主题、{total_items} 条有效 tweet 对象：主贴 {total_counts.get("root", 0)} 条，作者补充楼层 {total_counts.get("thread", 0)} 条，评论 {total_counts.get("comment", 0)} 条，引用 {total_counts.get("quote", 0)} 条，关联内容 {total_counts.get("related", 0)} 条；媒体引用 {total_media} 处，唯一归档图片/媒体文件 {total_unique_media} 个（其中历史补充 {orphan_media_count} 个）；浏览器逐屏滚动快照 {total_snapshots} 份，可见文章块 {total_visible_blocks} 个，去重可见内容块 {total_unique_visible_blocks} 个。

这批内容真正有价值的不是“某个 SEO 技巧”，而是一套从认知、选词、内容、外链、社媒冷启动、代理数据判断到商业化承接的增长系统：

- 认知层：赚钱/创业不是考试，要理解规则、激励和风险收益。
- SEO 层：选词决定入口，长尾负责铺量，内链负责传权，外链负责外部信任。
- 社媒层：推荐流不是搜索流，首图、标题、人设和需求创造更重要。
- 商业层：产品到及格线后，流量和营销决定上限；但产品不能低于承接流量的底线。
- 数据层：没有完美数据时，用 Semrush、GSC、Google Trends、竞品、社媒评论、平台销量做代理验证。

## 道法术器势总拆解

一句话结论：这套内容不是单纯的 SEO 技巧集合，而是一套“用真实需求制造品牌搜索，再用搜索和产品页承接转化”的增长系统。对 EzRemove 来说，`watermark remove` 只是入口，真正要经营的是图片/视频素材处理工作流。

| 层级 | 核心问题 | 从文档里抽出的判断 | 对 EzRemove 的落地 |
|---|---|---|---|
| 道 | 为什么做，边界在哪里 | 增长不能只按平台教程做题，要理解用户、平台和商业系统的激励；但不能把侵权、虚假搜索、低质内容农场当成增长。 | 以“帮助用户处理自己有权使用的素材”为价值边界；所有页面都要说明版权、授权、商用风险，品牌不能被做成灰色工具。 |
| 法 | 用什么系统持续增长 | 先用免费工具和社媒/KOL 创造需求，再用 SEO/GEO 页面承接需求；先打低难度长尾和场景词，再把权重导向核心词。 | 建立“核心工具页 + 长尾教程页 + 对比页 + FAQ/GEO 页 + KOL/PR 内容”的内容系统，不做一次性刷词活动。 |
| 术 | 每天具体做什么 | 选词、页面、内链、外链、KOL、评论挖掘、首图标题、竞品词、FAQ，全部要绑定页面角色和转化指标。 | 重点执行 `watermark remover` 核心页、图片/视频长尾页、竞品替代页、版权安全 FAQ、前后对比素材、KOL brief 和 UTM 追踪。 |
| 器 | 用什么工具和资产沉淀 | Semrush、GSC、Trends、GA4、UTM、X/Twitter 评论、飞书文档、页面模板、图片案例库、raw 抓取数据。 | 每周用数据复盘“词、页、渠道、转化”；把评论问题转成 FAQ，把高表现素材转成页面和 KOL 模板。 |
| 势 | 借什么趋势放大 | AI 图片/视频编辑、电商素材处理、短视频素材复用、免费工具冷启动、品牌搜索和 GEO/LLM 搜索推荐。 | 不把 EzRemove 定位成单点去水印，而是定位成 AI 素材清理和创作者工作流入口。 |

### 道：先定价值边界，不然流量会反噬品牌

这批内容里反复出现“规则、风险收益、平台机制、用户停留”的判断。真正可复用的不是灰色技巧，而是：增长动作必须理解规则，也必须知道哪些边界不能碰。

- 用户价值：帮助用户更快处理自己有授权、可使用、可二次编辑的图片/视频素材。
- 风险边界：不鼓励盗图、搬运、侵权商用，不用虚假搜索、机器人点击、站群伪装去做短期排名。
- 产品底线：上传、处理、预览、下载、注册、付费这些流程必须稳定，否则越投流量越容易放大负反馈。
- 品牌目标：让用户因为真实体验主动搜索 EzRemove，而不是靠人为刷搜索制造假信号。

### 法：先造需求，再承接搜索，再沉淀品牌

文档里的核心方法可以压成一条路径：

`免费工具体验 -> KOL/社媒制造场景需求 -> 用户搜索品牌/问题词 -> SEO/GEO 页面承接 -> 工具转化 -> 数据反哺选词和内容`

这条路径里有三个关键顺序：

1. 冷启动时不要只盯大词。先做能排得动的长尾、场景词和问题词。
2. 社媒和 KOL 不是为了直接讲 SEO 标题，而是为了展示“处理前后对比”和“工作流节省时间”。
3. SEO 页面不是孤立文章，每篇都要把权重、流量和用户带回核心工具页。

### 术：执行动作要按页面角色分工

| 页面/动作 | 负责什么 | 内容要点 | 验收指标 |
|---|---|---|---|
| 核心工具页 | 承接核心词和转化 | `watermark remover`、上传入口、前后对比、免费额度、隐私和版权说明 | 上传率、处理成功率、下载率、注册率、付费率 |
| 长尾教程页 | 拿低难度搜索入口 | remove watermark from image/video、remove logo、remove text、remove date stamp | impression、排名、点击、内链点击 |
| 竞品/替代页 | 承接比较意图 | EzRemove vs 竞品，免费额度、输出质量、速度、价格、隐私 | 停留、上传、跳转工具页 |
| FAQ/GEO 页 | 让搜索引擎和 LLM 更容易引用 | What is EzRemove、Is it legal、How it works、Best use cases | 收录、引用、品牌词曝光 |
| KOL/PR 内容 | 创造需求和品牌搜索 | 前后对比、真实素材处理流程、创作者/电商/剪辑师场景 | 品牌搜索、UTM 访问、上传、注册 |
| 外链合作 | 引入垂直信任 | AI 工具目录、图片编辑教程、视频剪辑资源、电商卖家工具合集 | 来源质量、停留、上传、辅助转化 |

### 器：工具不是摆设，必须进入周复盘

| 工具/资产 | 看什么 | 产出什么 |
|---|---|---|
| Semrush | 搜索量、KD、竞品页面、外链来源 | 关键词池、竞品页清单、外链候选 |
| Google Search Console | impression、query、页面点击、索引状态 | 长尾扩页、标题调整、内链优化 |
| Google Trends | 需求是否上升 | 抢上升词，而不是只追最大词 |
| GA4 + UTM | KOL/外链/页面的真实转化 | 渠道 ROI、KOL 白名单、淘汰名单 |
| X/Twitter 评论与引用 | 真实疑问和反驳 | FAQ、选题、案例、内容补洞 |
| 飞书知识库 | 方法论和执行复盘 | 可复用 SOP、页面模板、KOL brief、周报 |
| 图片/视频案例库 | 处理前后效果 | 页面素材、社媒素材、广告素材 |

### 势：`watermark remove` 要吃的是素材工作流趋势

单看 `watermark remove`，它只是一个工具词；放到趋势里，它背后是几类长期需求：

- AI 图片和视频生成变多，用户需要二次清理、裁剪、修复、去文字、去 logo。
- 电商卖家需要更快处理商品图、素材图、海报图。
- 短视频创作者需要复用素材、清理画面、提高剪辑效率。
- 免费工具更容易冷启动，但稳定后要逐步限制滥用并设计商业化路径。
- GEO/LLM 搜索会偏好结构清晰、FAQ 完整、边界明确、案例充分的页面。

### 最终落地优先级

1. 先把核心工具页做到能承接流量：上传、处理、下载、注册、版权边界。
2. 做 20-40 个长尾教程和 FAQ/GEO 页面，把问题词和场景词铺起来。
3. 用 KOL/PR 做真实前后对比，带动 EzRemove 品牌搜索，不做虚假搜索。
4. 建立内链系统，让长尾页和对比页持续给核心工具页传权。
5. 每周用 GSC、GA4、UTM、Semrush 复盘，留下有效词、有效页、有效 KOL、有效外链。
6. 起量后再商业化：免费额度、批量处理、高清导出、视频处理、团队/电商套餐。

{comment_insights_section(total_counts)}

{sections}

{chr(10).join(orphan_media_markdown(corpus))}

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
      white-space: normal;
      text-align: left;
    }}
    th {{ background: #f1f5f9; }}
    code {{
      background: #eef2f7;
      padding: 2px 5px;
      border-radius: 4px;
      font-size: .92em;
    }}
    img {{
      display: block;
      max-width: min(100%, 920px);
      height: auto;
      border: 1px solid var(--line);
      border-radius: 8px;
      margin: 18px 0 10px;
      background: #f8fafc;
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
    total_media = sum(source.get("media_count", 0) for source in corpus["sources"])
    unique_media = corpus_media_files(corpus)
    archived_media = archived_media_files()
    total_unique_media = len(unique_media | archived_media)
    orphan_media_count = len(archived_media - unique_media)
    total_snapshots = sum((source.get("visible_archive") or {}).get("snapshot_count", 0) for source in corpus["sources"])
    total_visible_blocks = sum((source.get("visible_archive") or {}).get("article_block_count", 0) for source in corpus["sources"])
    total_unique_visible_blocks = sum((source.get("visible_archive") or {}).get("unique_block_count", 0) for source in corpus["sources"])
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
- 媒体引用：{total_media} 处
- 唯一归档图片/媒体文件：{total_unique_media} 个
- 历史补充图片：{orphan_media_count} 个
- 浏览器逐屏滚动快照：{total_snapshots} 份
- 可见文章块：{total_visible_blocks} 个
- 去重可见内容块：{total_unique_visible_blocks} 个

公开版保留链接、配图、公开短线索、结构化拆解、评论/引用线索和 EzRemove 执行映射；完整原始响应和逐屏 DOM 快照只保存在本地忽略目录 `data/raw` 与 `data/processed/public_legacy_content_corpus.json`。
"""


def main() -> int:
    curated_source = ROOT / "content" / "curated-report.md"
    curated_builder = ROOT / "scripts" / "build_curated_site.py"
    if curated_source.exists() and curated_builder.exists():
        subprocess.run([sys.executable, str(curated_builder)], check=True)
        return 0

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
