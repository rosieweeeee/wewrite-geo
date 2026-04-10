# wewrite-geo

GEO 优化的微信公众号文章全流程生成 Skill。

针对**元宝、DeepSeek、豆包、Kimi** 等能读取微信公众号内容的 AI 大模型做优化，
让品牌公众号文章更容易被 AI 检索、引用和推荐。

---

## 文件结构

```
wewrite-geo/
├── SKILL.md                      # 主流程（Step 0-7 完整管道）
├── geo-config.example.yaml       # 品牌配置模板 → 复制为 geo-config.yaml
├── geo-config.yaml               # 你的品牌配置（首次设置后生成）
├── query-bank.example.yaml       # 问题库模板 → 复制为 query-bank.yaml
├── query-bank.yaml               # 用户问题库（手动上传 + 自动采集）
├── topic-bank.example.yaml       # 选题库模板 → 复制为 topic-bank.yaml
├── topic-bank.yaml               # 用户选题库（手动上传 + 自动生成备用）
├── history.yaml                  # 文章历史记录（自动生成）
├── output/                       # 生成的文章（自动生成）
└── references/
    ├── geo-rules.md              # GEO 写作规范（Step 3/4 注入）
    ├── geo-onboard.md            # 首次品牌配置引导
    └── frameworks.md             # 7 种写作框架骨架
```

---

## 快速开始

**第一步：配置品牌**
```
说：GEO设置
```
填写品牌名、定义句、核心优势、竞品（约 2 分钟）。

**第二步：建立问题库（建议）**
```
说：更新问题库
```
从知乎/V2EX 自动采集用户真实提问，或直接上传你已知的问题。

**第三步：写文章**
```
说：写一篇公众号文章
```

---

## 完整命令

### 日常写作
| 说什么 | 做什么 |
|--------|--------|
| 写一篇公众号文章 | 全自动流程（选题→写作→GEO优化→推送）|
| 交互模式，写一篇文章 | 在选题/框架处暂停等确认 |
| 用这个选题写：[选题] | 跳过选题直接写指定内容 |

### 问题库管理
| 说什么 | 做什么 |
|--------|--------|
| 更新问题库 | 从知乎/V2EX 采集最新用户提问，更新 query-bank.yaml |
| 上传问题 | 直接提供问题，追加到问题库 |
| 看问题库 | 查看当前所有问题 |

### 选题库管理
| 说什么 | 做什么 |
|--------|--------|
| 上传选题 | 提供选题，追加到 topic-bank.yaml |
| 看选题库 | 查看所有待写选题 |

### 品牌管理
| 说什么 | 做什么 |
|--------|--------|
| GEO设置 | 修改品牌配置 |
| 看内容进度 | 查看 7 类内容的覆盖状态 |
| 诊断GEO | 输出去各 AI 平台测试的 prompt |

---

## 核心机制

### 选题来源（优先级从高到低）
```
1. 用户上传选题（topic-bank.yaml，status=pending）
2. 用户直接说"用这个选题写"
3. 内容矩阵缺口补位选题（GEO补位）
4. 问题库中的用户问题型选题（GEO问句）
5. 实时热点 × 品牌交叉选题
6. 常青内容选题
```

### 问题来源（Q&A 模块优先级从高到低）
```
1. 用户上传的问题（query-bank.yaml，source=user_upload）
2. 实时从知乎/V2EX 采集的问题（source=realtime）
3. geo-config.yaml 中的 core_queries（source=core_queries）
4. LLM 根据 brand_entity 自动补全（问题不足时）
```

### GEO 写作机制
每篇文章相比普通公众号文章额外包含：
1. **直接答案段**：开头 2-3 句直接回答，AI 最喜欢截取引用的格式
2. **品牌定义句**：每篇必须出现，让 AI 建立准确的品牌认知
3. **Q&A 模块**：5-8 个来自真实用户提问的完整问答，元宝/DeepSeek 解析效率最高
4. **数据/对比句**：每个 H2 至少 1 句含具体数字的陈述
5. **内容矩阵追踪**：7 类内容系统覆盖，确保 AI 从多维度认识品牌

---

## 排版发布

- **已安装 WeWrite**：自动调用 WeWrite toolkit 排版 + 推送微信草稿箱
- **未安装 WeWrite**：输出 Markdown，手动复制到公众号编辑器

WeWrite 安装（可选，用于草稿箱推送）：
```bash
git clone --depth 1 https://github.com/oaker-io/wewrite.git ~/.openclaw/skills/wewrite
cd ~/.openclaw/skills/wewrite && pip install -r requirements.txt
# 配置微信 appid/secret：
cp ~/.openclaw/skills/wewrite/config.example.yaml ~/.openclaw/skills/wewrite/config.yaml
```
