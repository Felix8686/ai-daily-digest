# ⚡ AI Daily Digest · AI 提效与商业变现周刊

> 专注 **AI商业变现案例、落地实操、轻量自动化架构与自媒体内容选题** 的全自动情报生成与静态站点系统。  
> 每日早上 08:00 自动抓取全球一手信源，经大模型结构化提炼后自动发布至私有静态站点，现已支持**情报一键收藏与派发至 Hermes/Codex** 的行动闭环。

🌐 **在线站点**：[news.felix8686.top](https://news.felix8686.top)  
🔒 **访问口令**：`felix8686`（客户端 `localStorage` 记忆保护）

---

## 🌟 核心特性与架构

```
[多平台一手信源] ──> [抓取与三重防护过滤] ──> [LLM 结构化提炼] ──> [现代化静态站构建] ──> [行动与偏好闭环]
 (变现/工具/实操)    (去重 / 黑名单 / 年龄)     (五大闭环核心专栏)      (news.felix8686.top)     (⭐收藏 / 🔗派发Agent)
```

1. **情报交互卡片：收藏与派发行动闭环**：
   - ⭐ **本地快捷收藏与专属视图**：每张情报卡片均提供一键收藏，状态基于 `localStorage` 离线持久化；顶部胶囊提供 `⭐ 我的收藏 (N)` 专属视图，一键过滤高价值干货，形成个人品味与资产沉淀。
   - 🔗 **一键派发至 Hermes / Codex / 复制 Prompt**：卡片底部提供轻量派发弹窗：
     - **直发 Telegram / Hermes**：调用 TG 接口预填结构化调研 Prompt，快速让云端 Agent 展开全网深度调研；
     - **复制 Codex / Agent 终端指令**：一键生成 `codex "..."` 命令行指令，方便本地直接拉起 Agent 执行深度代码分析与环境试跑；
     - **复制完整 Prompt 研报指令**：一键复制结构化调研 Prompt，适合无缝粘贴至 ChatGPT / Claude / Gemini 深度追问。

2. **纯静态网页驱动，下线邮件依赖**：
   - 全面转向独立网页沉浸式阅读，告别邮件垃圾箱拦截与格式错乱。
   - 适配移动端与桌面端自适应排版，支持**明暗主题手动/跟随系统切换**。
   - 配备**顶部阅读进度条**、**分类快速跳转胶囊**与**历史归档按日检索**。

3. **五大闭环核心专栏**：
   - ⚡ **【行业异动：新模型 · 降价 · 羊毛福利 · 接口预警】**：大厂重磅模型、API 降价与免费额度调整、Breaking Changes 预警。
   - 💰 **【商业变现与一人公司打法】**：独立开发微型 SaaS、海外一人团队 0 到 1 赚钱案例、出海套利与 MRR 营收拆解（每条必附【商业启发】）。
   - 💻 **【本地平替与上手神器】**：普通电脑或 Mac 即刻可跑的端侧工具、零门槛省时神器，坚决剔除脱离实际的学术底层推导。
   - 🎯 **【创作者风控与爆款选题】**：公众号与社交媒体风控红线、X 爆款 Agent 玩法与黑客实操（附带【写作切入点建议】）。
   - 🔍 **【暗改排雷与避坑打假】**：揭露厂商缩水降级、虚假开源噱头，为工具选型省钱避坑。

4. **三重防幻觉与去噪防线**：
   - **跨天排重（14 天历史库）**：严格剔除往期简报已报道过的重复链接。
   - **已知技能/工具黑名单拦截**：自动扫描本机与云端已安装工具（如 `agent-reach`、`opencli`、`hermes` 等），绝不把读者已知熟知的工具二次推荐为“新神器”。
   - **GitHub 仓库年龄深度鉴伪**：校验 GitHub 仓库首次创建时间（默认上限 90 天），自动拦截开源已久、仅靠短期刷星翻红的老旧项目。

---

## 🛠️ 项目结构

```
ai-daily-digest/
├── config.yaml          # 订阅源列表、时间窗口、已知工具黑名单与站点参数
├── fetcher.py           # RSS 抓取清洗、跨天去重、仓库年龄鉴伪与黑名单过滤
├── summarizer.py        # 5 大专栏系统提示词（Prompt）与 LLM 调用逻辑
├── site_builder.py      # 现代化静态网页生成器（含收藏夹、派发弹窗、密码门禁、主题切换、反爬配置）
├── main.py              # 主调度入口（抓取 -> 提炼 -> 归档 -> 构建站点）
├── template.html        # 响应式邮件备用模板
├── mailer.py            # SMTP 发信组件（可选备用）
├── archive/             # 历史简报 Markdown 存档库 (digest-YYYY-MM-DD.md)
├── dist/                # 静态网页输出目录（自动生成 robots.txt 与 CNAME）
└── .github/workflows/   # GitHub Actions 自动化部署到 Pages 工作流
```

---

## 🚀 本地运行与调度

### 1. 安装依赖
```bash
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 2. 配置环境变量 (`.env`)
复制 `.env.example` 为 `.env` 并填写相关模型 Key：
```ini
# 大模型配置（推荐 DeepSeek）
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.deepseek.com
OPENAI_MODEL=deepseek-chat

# 可选 GitHub Token（用于提升 GitHub 仓库年龄检查的 API 配额）
GITHUB_TOKEN=ghp_...
```

### 3. 执行运行命令
```bash
# 正常执行：抓取、AI提炼、归档 Markdown 并生成静态网页 dist/
python main.py

# 预览模式：仅抓取并提炼输出控制台，不更新归档
python main.py --dry-run

# 仅重新构建静态网页（将 archive/ 中的历史简报重新编译为包含交互卡片的 HTML）
python site_builder.py

# 如需临时额外发送一份邮件给配置邮箱
python main.py --send-mail
```

---

## ⚙️ 订阅源管理 (`config.yaml`)

修改 [`config.yaml`](config.yaml) 即可增删订阅源或调整过滤策略：

```yaml
settings:
  time_window_hours: 36         # 抓取最近 36 小时内的文章
  max_items_per_feed: 5         # 单源最多保留条数
  enable_email: false           # 邮件推送默认关闭（纯网页驱动）
  github_max_repo_age_days: 90  # GitHub 仓库最大天数限制

filters:
  known_tools:                  # 读者已知工具黑名单
    - "agent-reach"
    - "hermes"
    - "opencli"

feeds:
  - name: "Growth in Reverse (一人商业变现与MRR拆解)"
    category: "商业变现与一人公司"
    url: "https://growthinreverse.com/feed/"
  ...
```

---

## 🔒 静态站点安全与部署机制

1. **反爬与防索引**：自动在输出目录生成 `robots.txt`（`Disallow: /`），并在所有页面 `head` 中注入 `noindex, nofollow, noarchive`。
2. **自动化发布**：
   - 云端定时任务每日 08:00 运行 `main.py`，生成新归档并推送至 GitHub 仓库。
   - GitHub Actions 监听 `archive/**` 变动，自动运行 `site_builder.py` 并通过 GitHub Pages 零延迟发布。
