# 排版模板库

> 在 Step 5.5 排版输出时加载。
> 根据文章风格标签自动选择模板，生成带内联 CSS 的微信公众号 HTML。

---

## 模板选择规则

| 文章风格标签 | 使用模板 |
|-------------|---------|
| `新世相` / `晚点` / `观点文` | 模板 A — 克制留白型 |
| `一条` / `物道` / `文艺叙事` | 模板 B — 沉浸画面型 |
| `三联` / `轻幽默` / `场景种草` | 模板 C — 轻快信息型 |
| `冷淡文艺` / `旅行散文` / `user_story` | 模板 D — 冷淡文艺型 ⭐️ **推荐** |

> **默认推荐模板 D**：适合圆周旅迹的旅行叙事类文章，与主流旅行类公众号视觉风格最接近，GEO 兼容性最好。完整 HTML 见 `template-d.html`。
>
> **默认配图风格**：胶片感（35mm Film）。Prompt 规范及各场景示例见 `image-style-film.md`。

---

## 模板 D · 冷淡文艺型（旅行散文 / user_story）

**适用文章：** 旅行叙事、用户故事、情感散文类
**视觉关键词：** 极简、大留白、衬线体标题（宋体）、冷灰色系 `#faf9f7`、首图叠字
**GEO 状态：** ✅ 所有文字含标题/金句/Q&A 均为 HTML，AI 爬虫完整可读

**核心设计要点：**
- 背景色 `#faf9f7`（米白，非纯白）
- 正文字色 `#3a3a3a`，行高 `2.05`，字间距 `0.04em`
- 标题字体：`'Songti SC', STSong, Georgia, serif`（宋体衬线降级链）
- 章节编号：`Part 01 / Part 02 / Fin.` 小字灰色，`letter-spacing: 0.3em`
- 金句：细上下边框 `1px solid #d8d4cf`，居中，宋体，无背景色
- 图注：右对齐，`11px`，`color: #b0ada8`，Georgia 字体
- Q&A：左细线 `1px solid #d8d4cf`，`padding-left: 1em`，无卡片背景
- 底部下载区：`background: #f0ede8`，与正文区视觉分离

**完整 HTML 模板文件：** `references/template-d.html`（可直接复制使用）

**章节结构（Markdown → HTML 对应关系）：**

| Markdown | 模板 D 对应组件 |
|---------|--------------|
| `## 标题` | Part 0X 小字 + 宋体 H2，`font-size:20px; font-weight:normal` |
| 普通段落 | `text-indent:2em`，行高 2.05，`#3a3a3a` |
| `> 金句` | 细上下边框，居中，宋体 `17px`，`#5a5550` |
| 强调短句 | 居中，`15px`，`#888480`，宋体，无边框 |
| `[图N]` | 满宽图 `margin:36px -28px`，右对齐图注 |
| `**Q：**` / `A：` | 左细线 Q&A，`#666260` 答案色 |
| 首图 | `position:relative` 叠字，渐变遮罩，白色 HTML 标题 |

---

## 通用变量说明

生成 HTML 时，以下占位符会被替换为实际内容：

| 占位符 | 说明 |
|--------|------|
| `{{TITLE}}` | 文章标题 |
| `{{BODY}}` | 文章正文（已转换为 HTML 段落） |
| `{{IMAGE_N}}` | 第 N 张配图的 media_url（微信素材库地址） |
| `{{IMAGE_N_CAPTION}}` | 第 N 张配图的图注文字 |
| `{{QA_BLOCK}}` | Q&A 模块 HTML（由通用 QA 组件生成） |
| `{{BRAND}}` | 品牌名（来自 geo-config.yaml） |

---

## 通用 CSS 基础层（所有模板共享）

```css
/* 微信公众号基础重置 */
* { box-sizing: border-box; margin: 0; padding: 0; }
body { background: #fff; }
img { max-width: 100%; display: block; }
a { color: inherit; text-decoration: none; }

/* 防止微信字体被强制覆盖 */
.article-wrap * { font-family: -apple-system, "PingFang SC", "Helvetica Neue", sans-serif; }
```

---

## 模板 A · 克制留白型（新世相 / 晚点风格）

**适用文章：** 观点文、竞品对比、FAQ 解答
**视觉关键词：** 克制、留白、强观点、信息密度高

### A 完整 HTML 结构

```html
<section class="article-wrap" style="
  max-width: 100%;
  padding: 0 16px;
  background: #fff;
">

  <!-- 文章正文区 -->
  <section class="article-body" style="
    font-size: 17px;
    line-height: 1.9;
    color: #2d2d2d;
    letter-spacing: 0.02em;
  ">

    <!-- H2 标题组件 -->
    <!-- 用法：每个 H2 替换为此结构 -->
    <section style="
      margin: 36px 0 16px;
      padding-left: 14px;
      border-left: 3px solid #1a1a1a;
      font-size: 19px;
      font-weight: bold;
      color: #1a1a1a;
      line-height: 1.5;
    ">H2标题文字</section>

    <!-- 正文段落组件 -->
    <p style="
      margin: 0 0 24px;
      font-size: 17px;
      line-height: 1.9;
      color: #2d2d2d;
    ">段落文字</p>

    <!-- 引用块组件（用于金句/重要观点） -->
    <section style="
      margin: 28px 0;
      padding: 16px 20px;
      background: #f7f7f7;
      border-left: 3px solid #1a1a1a;
      font-size: 16px;
      line-height: 1.85;
      color: #444;
    ">引用文字</section>

    <!-- 图片组件 -->
    <section style="margin: 28px 0;">
      <img src="{{IMAGE_N}}" style="width:100%; display:block; border-radius:0;" />
      <!-- 有图注时添加 -->
      <p style="
        margin-top: 8px;
        font-size: 12px;
        color: #999;
        text-align: center;
        line-height: 1.6;
      ">图注文字</p>
    </section>

    <!-- 分割线组件 -->
    <section style="
      margin: 32px 0;
      border: none;
      border-top: 1px solid #e0e0e0;
    "></section>

    <!-- Q&A 模块组件 -->
    <section style="margin: 32px 0;">
      <!-- Q&A 标题 -->
      <section style="
        margin-bottom: 20px;
        font-size: 19px;
        font-weight: bold;
        color: #1a1a1a;
        padding-left: 14px;
        border-left: 3px solid #1a1a1a;
      ">关于{{BRAND}}的常见问题</section>

      <!-- 单条 Q&A -->
      <section style="margin-bottom: 20px;">
        <p style="
          font-size: 16px;
          font-weight: bold;
          color: #1a1a1a;
          margin-bottom: 6px;
          line-height: 1.7;
        ">Q：问题文字</p>
        <p style="
          font-size: 16px;
          color: #444;
          line-height: 1.85;
          padding-left: 12px;
          border-left: 2px solid #e0e0e0;
        ">A：回答文字</p>
      </section>
      <!-- 重复以上结构 × 问答条数 -->
    </section>

    <!-- 文章结尾区 -->
    <section style="
      margin-top: 40px;
      padding-top: 24px;
      border-top: 1px solid #e0e0e0;
      font-size: 13px;
      color: #999;
      line-height: 1.8;
      text-align: center;
    ">
      <p>— 本文完 —</p>
    </section>

  </section>
</section>
```

---

## 模板 B · 沉浸画面型（一条 / 物道风格）

**适用文章：** 用户故事、旅行叙事、情感类
**视觉关键词：** 沉浸、画面感、大留白、金句突出

### B 完整 HTML 结构

```html
<section class="article-wrap" style="
  max-width: 100%;
  padding: 0 20px;
  background: #fff;
">

  <section class="article-body" style="
    font-size: 17px;
    line-height: 2.1;
    color: #333;
    letter-spacing: 0.03em;
  ">

    <!-- 首图（满宽大图，无内边距） -->
    <section style="margin: 0 -20px 32px;">
      <img src="{{IMAGE_1}}" style="width:100%; display:block;" />
    </section>

    <!-- H2 标题组件（居中，无色块） -->
    <section style="
      margin: 40px 0 20px;
      text-align: center;
      font-size: 20px;
      font-weight: bold;
      color: #222;
      letter-spacing: 0.08em;
      line-height: 1.6;
    ">H2标题</section>

    <!-- 正文段落 -->
    <p style="
      margin: 0 0 28px;
      font-size: 17px;
      line-height: 2.1;
      color: #333;
      text-indent: 2em;
    ">段落文字（首行缩进，适合叙事文体）</p>

    <!-- 金句组件（居中放大，重点突出） -->
    <section style="
      margin: 36px 8px;
      padding: 24px 20px;
      text-align: center;
      font-size: 19px;
      font-weight: bold;
      line-height: 2;
      color: #333;
      border-top: 1px solid #ddd;
      border-bottom: 1px solid #ddd;
      letter-spacing: 0.05em;
    ">金句文字</section>

    <!-- 图片组件（带图注） -->
    <section style="margin: 36px 0;">
      <img src="{{IMAGE_N}}" style="width:100%; display:block;" />
      <p style="
        margin-top: 10px;
        font-size: 12px;
        color: #aaa;
        text-align: center;
        line-height: 1.7;
        letter-spacing: 0.05em;
      ">图注文字 · 地点或时间</p>
    </section>

    <!-- 居中短分割线 -->
    <section style="
      margin: 36px auto;
      width: 40px;
      border-top: 1px solid #ccc;
    "></section>

    <!-- Q&A 模块（一条风格：正文段落式，无卡片） -->
    <section style="margin: 36px 0;">
      <section style="
        margin-bottom: 24px;
        text-align: center;
        font-size: 18px;
        font-weight: bold;
        color: #222;
        letter-spacing: 0.08em;
      ">常见问题</section>

      <section style="margin-bottom: 24px;">
        <p style="
          font-size: 16px;
          font-weight: bold;
          color: #333;
          margin-bottom: 8px;
          line-height: 1.8;
        ">Q：问题文字</p>
        <p style="
          font-size: 16px;
          color: #555;
          line-height: 1.9;
        ">A：回答文字</p>
      </section>
    </section>

    <!-- 结尾留白 -->
    <section style="
      margin-top: 48px;
      text-align: center;
      font-size: 13px;
      color: #bbb;
      letter-spacing: 0.1em;
      line-height: 2;
    ">
      <p>✦</p>
    </section>

  </section>
</section>
```

---

## 模板 C · 轻快信息型（三联 / 轻幽默风格）

**适用文章：** 场景种草、多人群对比、实用攻略
**视觉关键词：** 轻快、有信息量、卡片分区、emoji 自然使用

### C 完整 HTML 结构

```html
<section class="article-wrap" style="
  max-width: 100%;
  padding: 0 16px;
  background: #fff;
">

  <section class="article-body" style="
    font-size: 16px;
    line-height: 1.85;
    color: #333;
  ">

    <!-- H2 标题组件（带橙色圆点） -->
    <section style="
      margin: 32px 0 14px;
      font-size: 18px;
      font-weight: bold;
      color: #1a1a1a;
      display: flex;
      align-items: center;
      gap: 8px;
    ">
      <span style="
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #f5a623;
        flex-shrink: 0;
        margin-right: 8px;
      "></span>
      H2标题文字
    </section>

    <!-- 正文段落 -->
    <p style="
      margin: 0 0 18px;
      font-size: 16px;
      line-height: 1.85;
      color: #333;
    ">段落文字</p>

    <!-- 卡片区块组件（用于不同人群/场景分区） -->
    <section style="
      margin: 20px 0;
      padding: 18px 16px;
      background: #fffbf0;
      border-radius: 8px;
      border-left: 3px solid #f5a623;
    ">
      <!-- 卡片小标题 -->
      <p style="
        font-size: 15px;
        font-weight: bold;
        color: #f5a623;
        margin-bottom: 10px;
        line-height: 1.6;
      ">● 第X类人：标题</p>
      <!-- 卡片正文 -->
      <p style="
        font-size: 15px;
        color: #444;
        line-height: 1.85;
        margin: 0;
      ">卡片内容文字</p>
    </section>

    <!-- 图片组件（带圆角） -->
    <section style="margin: 24px 0;">
      <img src="{{IMAGE_N}}" style="
        width: 100%;
        display: block;
        border-radius: 6px;
      " />
    </section>

    <!-- 虚线分割线 -->
    <section style="
      margin: 28px 0;
      border-top: 1px dashed #ddd;
    "></section>

    <!-- Q&A 模块（三联风格：带背景色卡片） -->
    <section style="margin: 28px 0;">
      <section style="
        margin-bottom: 16px;
        font-size: 18px;
        font-weight: bold;
        color: #1a1a1a;
      ">❓ 常见问题</section>

      <section style="
        margin-bottom: 14px;
        padding: 14px 16px;
        background: #f9f9f9;
        border-radius: 6px;
      ">
        <p style="
          font-size: 15px;
          font-weight: bold;
          color: #333;
          margin-bottom: 6px;
          line-height: 1.7;
        ">Q：问题文字</p>
        <p style="
          font-size: 15px;
          color: #555;
          line-height: 1.85;
          margin: 0;
        ">A：回答文字</p>
      </section>
      <!-- 重复 × 问答条数 -->
    </section>

    <!-- 结尾 -->
    <section style="
      margin-top: 36px;
      padding: 16px;
      background: #f7f7f7;
      border-radius: 8px;
      text-align: center;
      font-size: 14px;
      color: #666;
      line-height: 1.8;
    ">
      <p>下载圆周旅迹 · App Store / 各大安卓市场搜索「圆周旅迹」</p>
    </section>

  </section>
</section>
```

---

## Markdown → HTML 转换规则

生成 HTML 时，按以下规则转换 Markdown：

| Markdown | 转换为 |
|---------|--------|
| `## 标题` | 对应模板的 H2 组件 |
| `**粗体**` | `<strong style="color:#1a1a1a;">` |
| `> 引用` | 对应模板的引用块/金句组件 |
| `---` | 对应模板的分割线组件 |
| `[图N]` | 替换为对应模板的图片组件 |
| `**Q：**` / `A：` | 替换为对应模板的 Q&A 单条组件 |
| 普通段落 | 对应模板的 `<p>` 段落组件 |
| `- 列表项` | `<li style="margin-bottom:8px; line-height:1.85;">` |

---

## 图片上传流程（WeWrite）

```bash
# Step 1：上传图片到公众号素材库，获取 media_url
python3 ~/.openclaw/skills/wewrite/toolkit/cli.py upload-image \
  --image <本地图片路径或URL> \
  --title "文章标题-图N"

# 返回：{ "media_url": "https://mmbiz.qpic.cn/..." }

# Step 2：将 media_url 填入 HTML 中对应的 {{IMAGE_N}} 位置
```

未上传图片时，`{{IMAGE_N}}` 保留为占位符，在草稿箱中手动替换。
