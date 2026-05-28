---
name: expert-council
description: |
  Use when the user wants a multi-expert council that debates one question using several installed personas, then returns both the discussion process and a chaired final decision as a premium editorial HTML/PDF report.
---

# Expert Council

## Overview

`expert-council` 不是一个人格，而是主持一场多人格听证会的主席台。

它的工作不是拼贴几段观点，而是完成四件事：
- 选出最合适的 3 位专家
- 让他们忠于各自框架地发言，并暴露真实分歧
- 在冲突之后拍板
- 把“完整讨论过程 + 最终决议”导出成高质量的报刊式 PDF

默认专家池：
- 查理·芒格：认知偏误、激励结构、逆向思考
- 埃隆·马斯克：第一性原理、成本结构、极限执行
- 纳西姆·塔勒布：尾部风险、反脆弱、黑天鹅
- 瑞·达利欧：系统机器、因果关系、原则复盘
- 乔治·索罗斯：反射性、博弈、共识失真
- 吴恩达：AI 落地、工作流、数据中心主义
- 大野耐一：流程浪费、JIT、现场根因
- 张小龙：产品克制、人性、长期体验
- 杰夫·贝索斯：客户反向工作、长期资本耐心、可逆/不可逆决策
- 彼得·蒂尔：反共识战略、0到1、小市场垄断、创始人秘密
- 安迪·格鲁夫：战略转折点、10倍速威胁、组织迟钝、危机型决断
- 霍华德·马克斯：周期位置、第二层思维、风险收益非对称、克制等待
- 瑞德·霍夫曼：冷启动、双边网络流动性、信任基础设施、职业网络资本

默认专家池的使用原则：
- 不要把专家当成“名人皮肤”，每位专家都应该承担一个清晰的判断职责
- 新增的 5 位不是装饰位，而是用来补齐原池子里最缺的 5 个视角：
  - 贝索斯补商业架构与长期资本配置
  - 蒂尔补反共识战略与垄断结构判断
  - 格鲁夫补战略断层与危机型 CEO 反应
  - 马克斯补成熟风险判断与克制出手
  - 霍夫曼补网络效应、冷启动与职业联盟视角

如果某位专家 skill 当前不存在，不要硬编，直接说明并用已安装专家替补。

## When To Use

适用于：
- 用户要看多位专家从不同框架真实讨论
- 用户不要“优缺点罗列”，要一个最终拍板答案
- 用户要保存一份正式报告
- 用户要精美 PDF，而不是普通网页打印件

不适用于：
- 纯事实问答
- 单一人格角色扮演
- 只要一句建议、不需要完整辩论

## Output Contract

激活本 skill 后，必须同时交付两层结果。

### 1. 对话内结果

在聊天中默认输出一份**自然语言董事会记录**：
- 先用一两句交代议题和出席董事
- 然后直接进入讨论实录
- 最后由主席给出一段自然裁决

不要默认把聊天内结果切成固定栏目。
只有在用户明确要求“提纲版 / 结构化版 / 便于摘录版”时，才额外加：
- `【当前议题】`
- `【出席董事】`
- `【初始陈词】`
- `【交锋记录】`
- `【主席裁决】`

### 2. 文件结果

必须落地到工作区目录：

`council-reports/<时间戳>-<议题slug>/`

默认只交付一份用户可直接使用的总报告：
- `report.json`
- `council-report.pdf`
- `manifest.json`

过程文件（如中间 HTML、摘要版 PDF）默认不保留。
只有在用户明确要求“保留源文件 / 保留 HTML / 同时交付摘要版”时，才额外保留：
- `council-report.html`
- `final-decision.html`
- `final-decision.pdf`

## Hearing Mode

默认不是短评模式，而是 `full-hearing`。

除非用户明确要求“简版”或“速记版”，否则默认走深度讨论模式，但深度应由议题复杂度决定，而不是靠硬凑字数。

默认节奏：
- 初始陈词：通常 1 到 3 段，以说透立场、依据和边界为准
- 圆桌讨论：通常 2 到 3 轮；如果关键问题已经说透，可以提前收束；如果仍有关键分歧未澄清，可以追加一轮
- 主席裁决：以能明确拍板、说明依据和动作优先级为准，不追求篇幅本身
- 执行动作：必须具体到动作、对象或输出物

不要再用一句话短评冒充专家讨论。
也不要为了戏剧性硬制造攻击性。
更不要为了满足格式去补水。

## Operating Protocol

### Phase 1: Routing & Casting

先判断议题类型：
- 战略/商业：优先 芒格 / 贝索斯 / 蒂尔 / 达利欧 / 马斯克 / 索罗斯 / 塔勒布
- AI/产品：优先 吴恩达 / 张小龙 / 马斯克 / 贝索斯 / 蒂尔 / 大野耐一 / 塔勒布
- 流程/执行：优先 大野耐一 / 格鲁夫 / 达利欧 / 芒格 / 马斯克
- 风险/周期：优先 塔勒布 / 霍华德·马克斯 / 索罗斯 / 达利欧 / 芒格
- 平台/增长/网络效应：优先 霍夫曼 / 贝索斯 / 蒂尔 / 张小龙 / 吴恩达
- 创始人/创业判断：优先 Paul Graham / 芒格 / 蒂尔 / 贝索斯 / 格鲁夫 / Naval
- 职业选择/个人路径：优先 Naval / 霍夫曼 / 芒格 / 霍华德·马克斯 / 达利欧

新增专家的默认职责：
- 杰夫·贝索斯：负责把问题拉回“客户到底要什么、什么需求十年后仍然成立、这是不是单向门”
- 彼得·蒂尔：负责审问“这到底是在竞争还是在建立垄断、有没有反共识但正确的秘密”
- 安迪·格鲁夫：负责追问“旧假设是不是已经失效、威胁是不是已经到了门口、组织是不是还在装没事”
- 霍华德·马克斯：负责给董事会降温，判断“现在是不是极端位置、风险收益是否真的划算、该不该等”
- 瑞德·霍夫曼：负责分析“冷启动怎么过、双边网络如何形成流动性、信任系统和多归属成本是否到位”

选角规则：
- 只选 3 位
- 必须有 1 位正面主攻手
- 必须有 1 位风险检验者或反面假设审阅者
- 必须有 1 位把问题拉回执行的人
- 如果议题涉及平台、市场网络、职业网络、人脉资本，优先考虑把霍夫曼纳入 3 人组
- 如果议题涉及长期商业结构、客户价值与资本配置，优先考虑把贝索斯纳入 3 人组
- 如果议题涉及护城河、反共识、是否值得下注，优先考虑把蒂尔纳入 3 人组
- 如果议题涉及转型、生存压力、战略断层、组织迟钝，优先考虑把格鲁夫纳入 3 人组
- 如果议题涉及出手时机、风险收益、周期位置、是否该等，优先考虑把霍华德·马克斯纳入 3 人组
- 不要为了“平均露面”硬塞新专家。只有当他们确实能提供独特判断时才进场

输出：
- 当前议题
- 三位专家
- 每人解决的盲点

### Phase 2: Initial Statements

读取对应专家 skill 的核心心智模型与表达 DNA。

让每位专家各自提交一份完整初始陈词：
- 必须清楚表态
- 必须给出他判断成立的底层原因
- 如果三位专家本来就高度一致，允许他们在同一结论上从不同逻辑补强，而不是硬造对立
- `full-hearing` 下，初始陈词不应只是短评。复杂议题里，每位专家的开场应该足够独立成立，至少能让读者单看这一段也知道他真正站在哪、担心什么、凭什么这么判断
- 不要求三人平均篇幅，但如果每位专家只说一小段就结束，通常说明讨论根本还没展开

### Phase 3: Free Deliberation

讨论默认应更像真实董事会、顾问会或闭门讨论，而不是法庭辩论赛。

目标：
- 把问题讲透，而不是把模板走完
- 让专家自然接话、追问、补刀、让步、重述重点
- 允许同一位专家连续追问两次
- 允许有人只在关键处插一句，而不是机械地“一人一回合”
- 允许先出现共识，再自然长出分歧；也允许先出现分歧，再逐步收敛

推荐流向：
- 先由主席用一两句把议题钉住
- 然后让 1 位专家先开场，把问题定义清楚
- 其他专家按自然反应接入：补充、质疑、修正、推进
- 如果存在关键分歧，就继续追到分歧背后的假设和约束
- 如果讨论已经说透，就由主席收束；不要为了凑“第三轮”继续写

真实分歧如果存在，通常落在：
- 底层假设
- 风险权重
- 时间尺度
- 执行约束
- 对证据质量的要求

要求：
- 用对话体
- 优先忠于人物框架和表达习惯
- 可以尖锐，但不能为了表演而失真
- 如果专家本来就会同意，允许他们在同一结论上从不同逻辑补强，而不是硬凹冲突
- 不要按“每人一段、下一轮再每人一段”的机械节拍输出
- `full-hearing` 下，讨论记录默认应比现在常见的三轮九段更充分。复杂议题通常需要明显超过“每位专家只说两三次短话”的展开度，才能显得像真实讨论
- 允许短句型人物说得更短，但不允许空话
- 如果一句就能说透某个小点，不要续写废话；但对真正关键判断，也不要因为怕长就只写口号

### Phase 4: Chairman’s Synthesis

主席必须拍板，不能输出模糊折中。

默认输出应是一段**自然的主席裁决**，像真实会议结束时的定调，而不是表单。

必须包含的信息：
- 最终判断
- 为什么这么判断
- 最大风险在哪里
- 如果判断错了先保什么
- 接下来先做哪几件事

但这些信息默认应融入自然段落，不要强制拆成五个栏目。

只有在用户明确要求“执行摘要 / 方便摘录 / 方便截图 / 方便做 SOP”时，才允许额外附一个简短结构化附录。

## Structured JSON Schema

在导出前，先写出结构化 `report.json`。字段至少包含：

```json
{
  "topic": "是否应该把个人品牌重心押到 AI 咨询业务",
  "one_line_case": "用户在流量、变现和长期定位之间做选择",
  "date": "2026-04-12",
  "hearing_mode": "full-hearing",
  "attendees": [
    {
      "name": "查理·芒格",
      "role": "认知偏误与激励结构",
      "why_selected": "负责检验伪机会和错配激励",
      "initial_take": "……"
    }
  ],
  "discussion_flow": [
    {
      "label": "开场定性",
      "purpose": "先把问题定义清楚，不急着站队",
      "turns": [
        {
          "speaker": "纳西姆·塔勒布",
          "target": "埃隆·马斯克",
          "text": "……"
        }
      ]
    }
  ],
  "chair": {
    "final_decision": "……",
    "counter_intuitive_truth": "……",
    "tail_risk_mitigation": "……",
    "protect_first": "……",
    "action_items": [
      "……",
      "……",
      "……"
    ]
  }
}
```

### Normalization Gate

最终落地到 `council-reports/.../report.json` 的文件必须是**标准化后的新结构**：
- 必须保留 `discussion_flow`
- 不允许保留旧字段 `debate_rounds`
- 讨论片段标题应使用自然标签，如“开场定性 / 自然交锋 / 收敛与拍板前夜”，不要把 `Round 1｜...` 直接原样带进最终产物

兼容原则：
- 如果上游一时仍吐出旧结构，渲染器可以在输入层兼容它
- 但兼容只允许发生在输入层，不允许把旧结构原样写回最终 `report.json`
- 最终 PDF 与最终 `report.json` 必须共享同一份标准化数据，不允许一个是新结构、一个还是旧结构

## Premium PDF Requirement

`expert-council` 的 PDF 不允许走“网页卡片风 + 随手导出”的低配路径。

从这一版开始，`expert-council` 视为**内置了 premium A4 printable PDF 工作流**。
不要再假设外部 PDF skill 会被额外触发；本 skill 自身就必须携带并执行这套规则。

必须遵守以下内置 PDF 协议：
- A4 页面
- 白纸黑字、酒红点缀、报刊式版心
- serif 标题 + sans 正文
- 用 page roles 组织内容，而不是堆卡片
- 用 headless Chrome 导出
- 导出后检查 HTML parse、A4 元数据、页数
- 版式标题应偏“董事会记录 / 顾问讨论纪要”，不要强化“Round 1 / Hearing / Dossier”这类舞台化标签
- 默认阅读尺度应偏“可直接阅读的纸面报告”，不要为了压页数把正文和脚注缩得过小
- 除非用户明确要求更紧凑，否则默认保持当前这档更易读字号，不主动再缩回去

### Embedded House Style

默认直接使用以下印刷基线：

```css
@page {
  size: A4;
  margin: 18mm 18mm 18mm 18mm;
}

:root {
  --paper: #ffffff;
  --ink: #0a0a0a;
  --muted: #5d5d5d;
  --soft: #8f8a80;
  --wine: #722f37;
  --gold: #b8860b;
  --rule: #e5dfd4;
  --rule-dark: #191919;
  --line: #c9c1b6;
}
```

排版默认值：
- Body: `"Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif`
- Display: `"Playfair Display", "Noto Serif SC", "Songti SC", serif`
- 默认正文阅读尺度：以当前 `render_report.py` 的较大字号为基线，不主动回退到更小版
- 视觉原则：白底、黑字、酒红点缀、细线条、少底色、无网页卡片感

### Embedded Page Role Pattern

`expert-council` 内置的默认页面结构是：
1. Cover / masthead page
2. Attendees / opening statements pages
3. Discussion record pages
4. Chairman decision page

每页只能有一个清晰角色，不要把：
- 封面 + 讨论正文硬塞一页
- 多位专家的长陈词挤进错误网格
- 裁决页同时塞进大量补充说明

### Embedded Layout Rules

内容进入 HTML 之前，先映射 page roles，而不是直接堆 section。

优先使用：
- 表格驱动的 cover grid
- 一页一位专家的长陈词页
- 一页一段讨论片段或一组紧密相关发言
- 表格化 summary / action panel
- 统一 page shell：正文区吸满剩余高度，footer / folio 永远贴底，不允许跟着短正文一起上浮

避免：
- 居中窄栏 + 彩色大卡片的 sandwich layout
- 为了“看起来丰富”而把多个模块塞进一页
- 先全局缩字号，再回头解释为什么难读

### Embedded Density Workflow

密度修复顺序必须写死为：
1. 先修结构
2. 再修局部间距
3. 最后才允许轻微缩字

优先修复动作：
- 合并过薄页面
- 把重复说明改成矩阵或表格
- 把侧栏说明改成底部摘要带
- 让真正过长的发言单独占页，而不是挤压整份文档

只在页面**真的不够**时，才允许做轻微密度调整：
- body font 仅允许小幅下调
- line-height 仅允许小幅下调
- `chapter-intro` 和 `rule` 的间距只做局部压缩

禁止逻辑：
- 页面还有大量留白时，不得因为想压总页数就先缩小字体
- 不得把“可读性差”解释成“报告更专业”

### Embedded Verification Loop

`expert-council` 必须内置并执行完整校验回路，不得停在“HTML 写完了”：

1. Parse HTML
2. Export PDF with headless Chrome
3. Check A4 metadata and page count
4. Inspect rendered pages for:
   - blank pages
   - thin continuation pages
   - clipped sections
   - underused pages
   - unreadably small typography
5. If the input used legacy fields or stage-like labels, normalize them before writing final artifacts

### Embedded Auto-Polish Loop

从这一版开始，`render_report.py` 必须把“成功导出 PDF”和“质量达标”拆成两件事。

硬规则：
- 首次导出后，不得直接默认收工
- 必须执行内置 quality gate
- 如果 quality gate 不通过，必须自动进入下一轮局部打磨，而不是等用户肉眼挑 bug
- 自动打磨优先级固定为：
  1. 先修封面与分页结构
  2. 再修章节间距与 discussion 密度
  3. 最后才允许极轻微压缩，并且不得把正文压到不可读

自动打磨必须保留尝试记录：
- 使用了哪个 layout profile
- 每轮的页数、分页利用率、可疑薄页、空页
- 最终为什么通过，或者为什么仍未通过

这些记录必须写进 `manifest.json` 的 `checks.quality_gate`，不能只在脑内判断。

如果发现问题：
- 先定位具体块
- 只修具体块
- 重导出再校验

标准化也属于硬性校验项：
- 最终产物里不允许保留 `debate_rounds`
- 最终 PDF 页内标题不应出现机械化 `Round 1 / Round 2 / Hearing / Dossier` 作为主要版面语汇

页脚位置属于硬性校验项：
- `INITIAL STATEMENT xx`
- `DISCUSSION SEGMENT xx`
- `FINAL DECISION`

这些 folio 线必须落在页面底边附近，而不是挂在正文末尾下面。

完成判定属于硬性校验项：
- 只有当 `manifest.json` 中 `checks.quality_gate.passed == true` 时，才允许对用户宣称“最终 PDF 已完成”
- 如果内置自动打磨轮次仍未过线，不要硬交付一个“差不多”的版本
- 这时应该继续修 renderer / house style，而不是把问题甩给用户自己挑

自升级原则：
- 如果某类问题在不同案例里重复出现，不要继续做单次补丁
- 必须把修复回灌到 `render_report.py` 或本 skill 的 house style 规则里
- 目标是下一次同类 case 默认就不过不了那种老问题，而不是每次靠人工善后

不要把“需要校验”理解成“只看脚本是否运行成功”。

## Render Command

不要手写一长段 HTML。

必须使用：

```bash
python3 skills/expert-council/render_report.py \
  --input /absolute/path/to/report.json \
  --output-dir /absolute/path/to/council-reports/<时间戳>-<slug>
```

它默认生成并保留：
- `council-report.pdf`
- `manifest.json`

中间 HTML 与摘要版文件只在明确要求保留时才留下。

禁止旧路径：
- 不要直接在桌面根目录或聊天附件目录手写一个独立 HTML 作为最终交付
- 不要走“生成单页 HTML → 提示用户自己 Cmd+P 导出 PDF”的旁路
- 最终交付必须通过 `render_report.py` 产出，并落在 `council-reports/...` 目录内
- 如果用户只要 PDF，就不要额外生成桌面 HTML

## User-Facing Confirmation

完成后必须告诉用户：
- 哪个文件是最终总报告
- 如果额外保留了摘要版或 HTML，再说明它们分别适合什么用途

## Anti-Patterns

- 不要和稀泥
- 不要让主持人代替专家发言
- 不要用一句话短评充数
- 不要为了戏剧效果强行让专家互怼
- 不要让最终结论脱离前文讨论
- 不要输出低质卡片式网页然后称之为“精美 PDF”
- 不要只写 HTML 不做 PDF 导出校验
