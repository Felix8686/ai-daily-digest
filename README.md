# ⚡ AI Daily Digest - 全球 AI 行业每日早报自动化推送

自动化抓取全球顶尖 AI 实验室、前沿科技媒体与行业周刊素材，利用 Google Gemini 大模型提炼关键进展，并通过 GitHub Actions 每天早上 8:00 定时生成精美排版邮件投递到你的邮箱。**完全零服务器成本、零运维维护。**

---

## 🌟 特性概览

*   **多源聚合**：内置 Google DeepMind、OpenAI、Hugging Face、TechCrunch、Import AI、Interconnects、机器之心、量子位等权威源。
*   **智能降噪**：大模型剔除纯商业 PR 稿，自动提炼「核心更新」与「行业深远影响」，拒绝对比复读。
*   **精美排版**：自适应响应式 HTML 邮件模板，支持暗色模式，保留原始新闻可点击跳转链接。
*   **零成本运行**：依赖免费的 GitHub Actions 定时任务 + Google Gemini API 免费层 + 个人邮箱 SMTP。
*   **自动归档**：每次生成的简报自动留存于 `archive/` 目录供日后检索。

---

## 🚀 3 步快速部署到 GitHub Actions

### 第一步：创建 GitHub 仓库并推送代码

在本地项目根目录初始化并推送到你的 GitHub（私有或公开仓库均可）：

```bash
cd ai-daily-digest
git init
git add .
git commit -m "feat: initial commit for ai daily digest"
git branch -M main
git remote add origin https://github.com/<你的用户名>/<你的仓库名>.git
git push -u origin main
```

---

### 第二步：配置 GitHub Secrets（密钥）

进入 GitHub 仓库页面，点击 **Settings** $\to$ **Secrets and variables** $\to$ **Actions** $\to$ **New repository secret**，添加以下配置项：

| 变量名 | 必填 | 示例 / 说明 |
| :--- | :---: | :--- |
| `GEMINI_API_KEY` | 是 | [Google AI Studio 免费申请](https://aistudio.google.com/) 的 API Key |
| `SMTP_HOST` | 是 | 邮箱 SMTP 服务器（如 QQ 为 `smtp.qq.com`，163 为 `smtp.163.com`） |
| `SMTP_PORT` | 是 | 端口（SSL 推荐填 `465`） |
| `SMTP_USER` | 是 | 发件人邮箱地址（如 `yourname@qq.com`） |
| `SMTP_PASS` | 是 | 邮箱**授权码 / 应用密码**（非邮箱登录密码，需在邮箱设置开启 POP3/SMTP 获得） |
| `RECEIVER_EMAIL` | 是 | 接收晨报的邮箱地址（可填自己的邮箱，多个以英文逗号分隔） |

> 💡 如果想使用 DeepSeek 或其他国产模型，也可以添加 `OPENAI_API_KEY` 和 `OPENAI_BASE_URL`。

---

### 第三步：手动触发测试

1. 点击仓库顶部的 **Actions** 标签页。
2. 在左侧点击 **AI Daily Digest** 工作流。
3. 点击右侧 **Run workflow** 下拉按钮，点击绿色的 **Run workflow** 按钮。
4. 几分钟后，查看工作流运行日志，打开你的收件箱查收首份 AI 行业晨报！

*(默认定时为每天北京时间早上 08:00 自动触发，如需修改时间可编辑 `.github/workflows/daily-digest.yml` 中的 cron 表达式)*

---

## 💻 本地运行与调试

如果想在本地直接测试抓取与效果：

1. **安装依赖**：
   ```bash
   pip install -r requirements.txt
   ```

2. **配置环境变量**：
   ```bash
   copy .env.example .env
   # 编辑 .env 文件填入你的 GEMINI_API_KEY
   ```

3. **本地模拟预览（不实际发信）**：
   ```bash
   python main.py --dry-run
   ```
   *程序将抓取最新文章、生成总结并输出 `preview.html`，可在浏览器直接打开查看效果。*

4. **测试 SMTP 发信**：
   ```bash
   python main.py --test-mail
   ```

---

## 🛠️ 自定义订阅源

打开 [`config.yaml`](config.yaml) 文件，按需增删 RSS 订阅源或调整时间窗口：

```yaml
settings:
  time_window_hours: 24   # 抓取过去多少小时内的文章
  max_items_per_feed: 5   # 单源最大抓取条数

feeds:
  - name: "自定义媒体名"
    category: "大厂官方动态"
    url: "https://example.com/feed.xml"
```
