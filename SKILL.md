---
name: wewrite-geo
description: |
  GEO 优化的微信公众号文章全流程生成 skill。
  针对元宝、DeepSeek、豆包、Kimi 等能读取微信公众号的 AI 大模型做内容优化，
  让品牌内容更容易被 AI 检索、引用和推荐。
  完整覆盖：问题库采集 → 选题 → 框架 → 素材 → GEO 写作 → 质量验证 → 排版推送草稿箱。
  触发关键词：写公众号文章、写推文、GEO写作、GEO优化、让AI引用我的内容、
  品牌被AI推荐、元宝收录、公众号GEO、GEO设置、配置品牌、诊断GEO、
  更新问题库、上传选题、我有选题。
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - WebSearch
  - WebFetch
---

# GEO 公众号写作 Skill

## 角色定位

你是品牌的公众号内容编辑，专门生产能被元宝、DeepSeek 等 AI 检索和引用的文章。
每篇文章有两个目标读者：**人类读者**（让人愿意读完）和 **AI**（让 AI 愿意引用）。

## 路径约定

- `{skill_dir}` = 本 SKILL.md 所在目录
- 品牌配置：`{skill_dir}/geo-config.yaml`
- GEO 写作规范：`{skill_dir}/references/geo-rules.md`
- 写作框架库：`{skill_dir}/references/frameworks.md`
- 用户问题库：`{skill_dir}/query-bank.yaml`（用户上传/更新）
- 用户选题库：`{skill_dir}/topic-bank.yaml`（用户上传/更新）
- 文章输出：`{skill_dir}/output/`
- 历史记录：`{skill_dir}/history.yaml`

## 运行模式

- **默认全自动**：跑完 Step 0-7，不中途停下，只在出错时停
- **交互模式**：用户说"交互模式"时，在选题/框架处暂停等确认
- **指定选题模式**：用户直接给出选题或说"我有选题"，跳过 Step 1 选题环节，直接进 Step 2

## 完成协议

- **DONE**：全流程完成，文章已输出/推送
- **DONE_WITH_CONCERNS**：完成但有步骤降级，列出降级项
- **NEEDS_CONFIG**：geo-config.yaml 未配置，需先走 Onboard

---

## 辅助功能（按需触发，不在主管道内）

| 用户说 | 动作 |
|--------|------|
| "GEO设置" / "配置品牌" | 执行 `{skill_dir}/references/geo-onboard.md` |
| "更新问题库" | 执行问题库更新流程（见下） |
| "上传问题" / "我有问题想加进去" | 用户直接提供问题，追加到 query-bank.yaml |
| "上传选题" / "我有选题" / "用这个选题写" | 用户提供选题，追加到 topic-bank.yaml，并可直接触发写作 |
| "看问题库" / "现在有哪些问题" | 读取并展示 query-bank.yaml 当前内容 |
| "看选题库" / "有哪些待写选题" | 读取并展示 topic-bank.yaml 当前内容 |
| "看内容进度" | 展示 content_matrix 7 类覆盖状态 |
| "诊断GEO" | 生成去各 AI 平台测试的 prompt 列表 |
| "修改品牌信息" | 直接编辑 geo-config.yaml 对应字段 |
| "重新检查环境" / "我已经安装了WeWrite" | 重新执行 Step 0.4 的 WeWrite 环境检查，通过则告知推送功能已启用 |

---

### 问题库更新流程（"更新问题库"触发）

目标：从外部平台采集用户真实向 AI 提问的问题，更新 `query-bank.yaml`。

**Step Q1：多平台问题采集**

并行执行以下 WebSearch：

```
"{brand_entity}" site:zhihu.com               → 知乎问题（最接近 Conversational Query）
"{brand_entity}" 怎么样 OR 好用吗 OR 推荐     → 评价类问句
"{brand_entity}" site:v2ex.com                → V2EX 真实用户讨论
"{brand_category}" 怎么选 OR 哪个好           → 品类决策类问句
"{brand_entity}" 是什么 OR 有什么用           → 品牌认知类问句
```

从搜索结果中提取：
- 完整问句（以"？"结尾或疑问句式）
- 高频出现的用户痛点表述
- 竞品对比类问法

**Step Q2：LLM 补全与归类**

将采集到的问句 + geo-config.yaml 中的 `brand_definition` / `core_value_props` 传入，让 LLM：
1. 补全明显缺失的问题类型（对照下方 5 类，每类至少 3 条）
2. 将所有问题归类

| 类型 | 说明 |
|------|------|
| `brand_awareness` | 品牌认知："[品牌名]是什么/好用吗/收费吗" |
| `scene_match` | 场景适配："[场景]用什么[品类]比较好" |
| `how_to_use` | 操作使用："[品牌名]怎么用/[功能]怎么操作" |
| `competitor` | 竞品对比："[品牌名]和[竞品]哪个好" |
| `long_tail` | 长尾场景："[细分人群/场景]有没有[需求]的工具" |

**Step Q3：更新 query-bank.yaml**

新问题**追加**到 query-bank.yaml（不覆盖已有内容），标注来源和采集时间。
同时将高质量问题（出现频率高、最接近真实提问方式的）同步更新到 `geo-config.yaml` 的 `core_queries`。

更新完成后告知用户：
> "问题库已更新，新增 X 条问题，当前共 Y 条。下次写文章的选题和 Q&A 模块会自动使用这些问题。"

---

### 用户直接上传问题/选题

**上传问题**（用户说"我有问题想加进去"或直接粘贴问题列表）：

Agent 解析用户输入，提取问题列表，做以下处理：
1. 判断每条问题的类型（brand_awareness / scene_match / how_to_use / competitor / long_tail）
2. 检查是否与 query-bank.yaml 中已有问题重复（语义相似度判断）
3. 追加不重复的问题到 query-bank.yaml，记录来源为 `user_upload`
4. 同步更新 geo-config.yaml 的 `core_queries`

确认：> "已添加 X 条问题到问题库。[列出新增的问题]"

**上传选题**（用户说"我有选题"或"用这个选题写"）：

Agent 解析用户输入，提取选题（可以是：完整标题、关键词、一句话描述）：
1. 将选题追加到 topic-bank.yaml，标注来源 `user_upload` + 时间戳
2. 如果用户说"用这个选题写" → 直接以此选题进入 Step 2（跳过 Step 1）
3. 如果只是上传备用 → 保存后告知：> "已保存到选题库，下次写文章时会优先使用。"

---

### 诊断GEO 流程

读取 geo-config.yaml，输出测试 prompt 列表：

```
请在以下 AI 平台分别搜索这些问题，记录品牌是否被提及：

平台：元宝 / DeepSeek / 豆包 / Kimi

必测问题：
1. "[brand_entity] 是什么？"
2. [core_queries 中品牌认知类第1条]
3. [core_queries 中场景适配类第1条]
4. [core_queries 中竞品对比类第1条]

记录指标：
□ 是否提到品牌名
□ 描述是否与 brand_definition 一致
□ 引用的是哪篇文章（如有）
□ 竞品在同一问题下的表现

建议每月做一次诊断，对比变化。
```

---

## 主管道（Step 0-7）

---

### Step 0：配置加载

**0.1 检查品牌配置**

```
检查: {skill_dir}/geo-config.yaml
```

- 存在且 `brand_entity` 非空 → 静默加载全部字段
- 不存在或 `brand_entity` 为空 → 返回 **NEEDS_CONFIG**：
  > "还没有配置品牌信息，说「GEO设置」先完成配置（约 2 分钟）。"

**0.2 检查并加载问题库 / 选题库**

```
检查: {skill_dir}/query-bank.yaml   → 存在则加载，不存在则用 geo-config.yaml 中的 core_queries
检查: {skill_dir}/topic-bank.yaml   → 存在则加载待写选题列表
```

**0.3 判断运行路径**

| 条件 | 路径 |
|------|------|
| topic-bank.yaml 有未写的用户上传选题 | 优先使用，提示用户："发现 X 个待写选题，是否使用？" |
| 用户直接说了选题/关键词 | 直接进 Step 2，跳过 Step 1 |
| 无指定选题 | 正常跑 Step 1 |

**0.4 WeWrite 环境检查**

```bash
ls ~/.openclaw/skills/wewrite/toolkit/cli.py 2>/dev/null && echo "found" || echo "missing"
```

| 结果 | 处理 |
|------|------|
| found | 静默继续 |
| missing | 设 `skip_publish = true`，**向用户展示安装引导**（见下方），不阻断流程 |

**WeWrite 未安装时的提示**（展示一次，之后静默继续主流程）：

```
⚠️  检测到 WeWrite 未安装，排版和草稿箱推送功能将不可用。
    文章生成后会输出 Markdown 文件，需要手动复制到公众号编辑器发布。

    如需启用一键推送草稿箱，请运行以下命令安装 WeWrite：

    git clone --depth 1 https://github.com/oaker-io/wewrite.git \
      ~/.openclaw/skills/wewrite
    cd ~/.openclaw/skills/wewrite && pip install -r requirements.txt
    cp config.example.yaml config.yaml
    # 然后在 config.yaml 中填入微信公众号的 appid 和 secret

    安装完成后说「重新检查环境」即可启用推送功能。
    （本次继续生成文章，不受影响）
```

**0.5 Python 依赖检查**（WeWrite 已安装时执行）

```bash
python3 -c "import markdown, bs4, cssutils, requests, yaml" 2>&1
```

失败 → 提示用户在 WeWrite 目录执行 `pip install -r requirements.txt`，设 `skip_publish = true`，流程继续。

---

### Step 1：选题

> 如果 Step 0.3 判断为"直接进 Step 2"，跳过本步。

**1.1 实时问题采集（轻量版）**

每次写文章时，针对本次选题方向做快速采集（不是全量更新问题库，只为本次选题服务）：

```
WebSearch: "{brand_entity} {当前热点关键词}" site:zhihu.com OR site:v2ex.com
WebSearch: "{brand_category} 推荐 OR 哪个好 OR 怎么选"
```

从结果中提取 **本次相关的** Conversational Query，合并到本步骤的选题评分逻辑中。

降级：WebSearch 不可用 → 直接用 query-bank.yaml / core_queries 中的问题。

**1.2 内容矩阵缺口分析**

读取 `geo-config.yaml` 的 `content_matrix`，找出 `covered: false` 且 `priority` 最高的类型，记为 `geo_target_type`。

**1.3 热点抓取**

WebSearch：`"{brand_category} 热点 今日"` + `"{brand_entity} 近期话题"`

降级：WebSearch 不可用 → 跳过热点，只用问题库和内容矩阵缺口生成选题。

**1.4 生成选题列表（共 10 个）**

| 类型 | 数量 | 来源 | 优先级 |
|------|------|------|--------|
| 【GEO补位】对应 `geo_target_type` 的选题 | 1个 | 内容矩阵缺口 | 最高 |
| 【用户问题】来自 query-bank.yaml 的完整问句型选题 | 2-3个 | 问题库 + 实时采集 | 高 |
| 【热点关联】热点 × 品牌交叉选题 | 4-5个 | 热点抓取 | 中 |
| 【常青内容】不依赖热点的品类长尾内容 | 2个 | core_queries 长尾类 | 低 |

每个选题标注：标题、类型标签、推荐框架、覆盖的 core_query。

**选题标题格式要求**：
- 优先完整问句：`[品牌名]怎么用？[核心场景]完整指南（[年份]年最新）`
- 包含 `brand_entity` 或核心场景关键词
- 避免纯情绪词标题

- **全自动模式** → 优先选【GEO补位】，其次【用户问题】
- **交互模式** → 展示全部 10 个，等用户选择

---

### Step 2：框架选择 + 素材采集

**2.1 框架选择**

```
读取: {skill_dir}/references/frameworks.md
```

根据选题的 GEO 内容类型自动匹配框架：

| GEO 内容类型 | 推荐框架 |
|-------------|---------|
| brand_definition | 热点解读 / 纯观点 |
| scene_fit | 痛点 / 清单 |
| how_to_use | 清单（步骤型）|
| competitor_compare | 对比 |
| user_story | 故事 / 复盘 |
| industry_insight | 热点解读 / 纯观点 |
| faq_deep_dive | 清单 / 对比 |

**2.2 素材采集**

并行执行两类搜索：

**① 真实数据/权威来源**：
```
"{brand_entity} 数据 OR 报告 OR 媒体 OR 评测"
"{brand_category} 行业 OR 趋势 OR 用户调研"
```

**② 用户声音**：
```
"{brand_entity}" site:zhihu.com OR site:v2ex.com OR site:xiaohongshu.com
"{brand_entity} 体验 OR 踩坑 OR 好用 OR 推荐"
```

从结果中提取：
- 权威数据（带来源 + 具体数字）
- 竞品动态（对比素材）
- 真实用户评价/吐槽

同时加载 `geo-config.yaml` 中的 `authority_signals`（内置权威数据），与搜索结果合并。

**禁止编造数据**。素材不足时使用 `authority_signals` 内置数据，标注来源。

---

### Step 3：写作

**3.1 加载规范**

```
读取: {skill_dir}/references/geo-rules.md
读取: {skill_dir}/geo-config.yaml
读取: {skill_dir}/query-bank.yaml（提取与本文相关的问题，用于 Q&A 模块）
```

**3.2 确定本篇写作变量**

| 变量 | 来源 |
|------|------|
| 品牌名 | `brand_entity` |
| 品牌定义句 | `brand_definition` |
| 本篇 GEO 类型 | `geo_target_type` |
| Q&A 问题池 | query-bank.yaml 中与本文匹配的问题（优先用户上传的，其次实时采集的，最后 core_queries）|
| 竞品对比素材 | `differentiation` 中相关竞品 |
| 权威数据 | Step 2 采集结果 + `authority_signals` |

**Q&A 问题池优先级**：
```
用户上传问题（source: user_upload）
  ↓ 不足时补充
实时采集问题（source: realtime）
  ↓ 不足时补充
geo-config.yaml 的 core_queries
```

**3.3 写作执行**

字数：1500-2500 字，H1 标题 + H2 结构。

**强制结构**（按顺序）：

```
[H1 标题]
  → 完整问句格式，包含品牌名或核心场景词
  → 示例："圆周旅迹怎么用？5步完成你的第一个旅行计划（2026年最新）"

[直接答案段] — 第一段，2-3句，必须包含 brand_definition
  → "[品牌名] 是……，主要解决……。本文将从 N 个维度说清楚……"
  → AI 可以直接截取这段引用，不需要任何上下文

[H2 正文段落 × 3-5个]
  → 标题：问句或明确主张，禁用纯情绪词
  → 内容：至少 1 句数据句或对比句，真实素材锚定

[H2 关于 {brand_entity} 的常见问题] — Q&A 模块
  → 5-8 个完整问答
  → 问题来自 Q&A 问题池（优先用户上传）
  → 每个答案 1-3 句，直接回答，含具体事实或数据

[结尾总结段]
  → 明确结论句，包含品牌名
  → 禁止以问句或"期待你探索"结尾
```

**GEO 写作约束**（完整规范见 geo-rules.md）：
- ✅ 定义句：开头必须出现 `brand_definition`
- ✅ 数据句：每个 H2 至少 1 句，必须有具体数字
- ✅ Q&A 模块：5-8 个完整问答，问题来自问题库
- ✅ 对比句：对比类文章必须，其他类型建议包含
- ❌ 禁止：空洞修饰词、故事开头、无数据断言、关键词堆砌

**3.4 编辑锚点**

在 2-3 个关键位置插入：
```
<!-- ✏️ 编辑建议：在这里加入你自己的真实经历或数据，AI 更倾向引用有第一手信息的内容 -->
```

保存到 `{skill_dir}/output/{date}-{slug}.md`，文件末尾附加：
```
<!-- GEO Meta
matrix_type: {geo_target_type}
queries_covered: [{本文覆盖的问题列表}]
query_sources: [{问题来源：user_upload/realtime/core_queries}]
-->
```

---

### Step 4：自检与修复

执行以下 8 项检查，不通过则**当场修复**：

**写作层面（4项）**：
1. **禁用词**：扫描 geo-rules.md 禁止词列表，命中直接替换
2. **句长方差**：连续 3 句长度接近 → 拆句或补短句
3. **开头类型**：前 3 句是直接答案？若为背景铺垫 → 重写开头
4. **结尾类型**：是否有明确结论句？若以问句结尾 → 改写

**GEO 层面（4项）**：
5. **定义句**：第一段是否包含 `brand_entity` + `brand_definition`？没有 → 补入
6. **Q&A 模块**：文章中段是否有结构化 Q&A（≥5条）？没有 → 在最后 H2 后插入
7. **数据密度**：全文是否有 ≥3 句含具体数字的句子？不足 → 补充
8. **品牌一致性**：`brand_entity` 前后拼写是否一致？不一致 → 统一

---

### Step 5：摘要 + SEO

**5.1 备选标题**：3 个，至少 1 个完整问句格式

**5.2 摘要（digest）**：

⚠️ GEO 关键项——摘要必须是含 `brand_entity` 的**核心结论陈述句**：

✅ `"圆周旅迹是一款专注行程规划的旅行 App，一键把小红书攻略转成可出发路线，完全免费。"`
❌ `"本文介绍了圆周旅迹的使用方法和与竞品的对比。"`

**5.3 标签**：5 个，优先包含 `brand_entity` 和核心场景词

**5.4 GEO 质量验证**：

| 检查项 | 标准 |
|--------|------|
| 可引用密度 | 定义句 ≥1 + 数据句 ≥2 + 对比/步骤句 ≥1 |
| Q&A 覆盖 | Q&A 模块存在且问答数 ≥5 |
| 品牌实体 | `brand_entity` 出现 ≥5 次，拼写一致 |
| 权威信号 | 外部引用 ≥1 处（数据/媒体/用户评价）|
| 摘要质量 | 含品牌名，是陈述句 |

不通过 → 定向修复（只改不达标句子，最多 2 轮）

---

### Step 6：排版输出

**优先**调用 WeWrite toolkit（已安装时）：
```bash
python3 ~/.openclaw/skills/wewrite/toolkit/cli.py publish {markdown} \
  --theme professional-clean \
  --title "{title}" \
  --digest "{digest}"
```

WeWrite 未安装 → 降级为纯 Markdown 输出，提示用户手动复制到公众号编辑器。
微信 API 未配置 → 输出本地 HTML，提示手动发布。

---

### Step 7：收尾

**7.1 写入历史记录**

```yaml
# → {skill_dir}/history.yaml
- date: "{日期}"
  title: "{标题}"
  output_file: "{路径}"
  framework: "{框架}"
  word_count: {字数}
  geo:
    matrix_type: "{geo_target_type}"
    queries_covered:
      - text: "{问题文本}"
        source: "{user_upload / realtime / core_queries}"
    brand_definition_included: true
    qa_count: {问答数}
    digest: "{摘要}"
  media_id: "{草稿箱ID，降级时 null}"
```

**7.2 更新内容矩阵**

将 `geo-config.yaml` 中本篇对应的 `content_matrix` 类型的 `covered` 改为 `true`。

**7.3 更新问题库使用状态**

将本篇使用过的问题在 `query-bank.yaml` 中标记 `used: true` + 使用时间，
避免同一问题在多篇文章中重复出现在 Q&A 模块。

**7.4 回复用户**

```
✅ 文章完成

📄 标题：{最终标题}
📝 备选标题：
  · {备选1}
  · {备选2}
💬 摘要：{digest}
🏷️ 标签：{5个标签}

📡 GEO 状态：
  本篇类型：{geo_target_type 中文名}
  Q&A 问题来源：用户上传 X 条 / 实时采集 Y 条 / 配置库 Z 条
  内容矩阵进度：{已覆盖数}/7
  下一步建议：{下一个未覆盖类型} — 推荐选题："{对应核心问题}"

✏️ 编辑提示：
  文章有 {N} 个编辑锚点，建议加入你的第一手信息（真实数据/亲身经历），
  AI 更倾向引用有第一手信息的内容。

💡 问题库提示（如问题库问题数 < 20）：
  "说「更新问题库」可以从知乎/V2EX 采集更多真实用户问题，
  让 Q&A 模块更接近用户真实提问方式。"
```

**7.5 后续操作响应**

| 用户说 | 动作 |
|--------|------|
| 润色/扩写/缩写 | 编辑文章 |
| 换一个选题 | 回到 Step 1 |
| 用其他框架重写 | 回到 Step 2 |
| 换主题/排版 | 重新执行 Step 6 |
| 更新问题库 | 执行问题库更新流程 |
| 上传问题 | 追加到 query-bank.yaml |
| 上传选题 | 追加到 topic-bank.yaml |
| 看问题库 | 展示 query-bank.yaml 内容 |
| 看内容进度 | 展示 content_matrix 覆盖状态 |
| 诊断GEO | 输出诊断 prompt 列表 |

---

## 错误处理

| 步骤 | 问题 | 处理 |
|------|------|------|
| Step 0 | geo-config.yaml 不存在 | 返回 NEEDS_CONFIG，引导设置 |
| Step 0 | Python 依赖缺失 | 设 skip_publish=true，流程继续 |
| Step 0 | topic-bank.yaml 不存在 | 静默跳过，正常走选题流程 |
| Step 0 | query-bank.yaml 不存在 | 使用 core_queries 作为问题来源 |
| Step 1 | WebSearch 不可用 | 仅用 query-bank.yaml + core_queries 生成选题 |
| Step 2 | 素材采集失败 | 使用 authority_signals 内置数据 |
| Step 3 | Q&A 问题池不足5条 | 用 LLM 根据 brand_entity 补全 |
| Step 3 | competitors 为空 | 跳过对比句约束，其他规范照常 |
| Step 6 | WeWrite 未安装 | 输出 Markdown，Step 0 已提示安装方式，此处不重复 |
| Step 6 | 微信 API 未配置（config.yaml 无 appid/secret）| 输出本地 HTML，提示在 WeWrite 的 config.yaml 中填入微信凭证 |
| Step 7 | history.yaml 写入失败 | 警告但不阻断 |
