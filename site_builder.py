#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
静态网页与历史归档站点生成器（全新现代化极简杂志风、分类导航、明暗主题切换与安全门禁）
"""
from __future__ import annotations

import sys
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
        sys.stderr.reconfigure(encoding="utf-8", line_buffering=True)
    except Exception:
        pass

import datetime as dt
from pathlib import Path
import markdown
from jinja2 import Template

WEB_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="robots" content="noindex, nofollow, noarchive, nosnippet">
  <title>{{ site_title }} - {{ page_title }}</title>
  <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>⚡</text></svg>">
  <style>
    :root {
      --bg: #f8fafc;
      --card-bg: #ffffff;
      --card-subtle: #f1f5f9;
      --text: #0f172a;
      --text-muted: #64748b;
      --text-light: #94a3b8;
      --border: #e2e8f0;
      --border-focus: #cbd5e1;
      --primary: #2563eb;
      --primary-hover: #1d4ed8;
      --primary-subtle: #eff6ff;
      --accent-monetize: #7c3aed;
      --accent-monetize-bg: #f5f3ff;
      --accent-tool: #059669;
      --accent-tool-bg: #ecfdf5;
      --accent-alert: #d97706;
      --accent-alert-bg: #fffbeb;
      --accent-creator: #e11d48;
      --accent-creator-bg: #fff1f2;
      --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
      --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.07), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
      --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.08), 0 4px 6px -4px rgba(0, 0, 0, 0.04);
    }
    
    html.dark {
      --bg: #090d16;
      --card-bg: #111827;
      --card-subtle: #1f2937;
      --text: #f3f4f6;
      --text-muted: #9ca3af;
      --text-light: #6b7280;
      --border: #1f2937;
      --border-focus: #374151;
      --primary: #3b82f6;
      --primary-hover: #60a5fa;
      --primary-subtle: #1e293b;
      --accent-monetize: #a78bfa;
      --accent-monetize-bg: rgba(139, 92, 246, 0.12);
      --accent-tool: #34d399;
      --accent-tool-bg: rgba(16, 185, 129, 0.12);
      --accent-alert: #fbbf24;
      --accent-alert-bg: rgba(245, 158, 11, 0.12);
      --accent-creator: #fb7185;
      --accent-creator-bg: rgba(244, 63, 94, 0.12);
      --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.3);
      --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.4);
      --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.5);
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }
    
    body {
      background-color: var(--bg);
      color: var(--text);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
      line-height: 1.75;
      font-size: 15px;
      transition: background-color 0.25s ease, color 0.25s ease;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }

    /* 顶部阅读进度条 */
    #progress-bar {
      position: fixed;
      top: 0;
      left: 0;
      height: 3px;
      background: linear-gradient(90deg, var(--primary), var(--accent-monetize));
      width: 0%;
      z-index: 999;
      transition: width 0.1s ease-out;
    }

    /* 密码门禁遮罩层 */
    #auth-overlay {
      position: fixed;
      inset: 0;
      background: rgba(9, 13, 22, 0.88);
      backdrop-filter: blur(16px);
      z-index: 10000;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 20px;
    }
    .auth-card {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 20px;
      padding: 40px 32px;
      max-width: 420px;
      width: 100%;
      text-align: center;
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.35);
    }
    .auth-card h2 {
      font-size: 22px;
      font-weight: 800;
      margin-bottom: 8px;
      letter-spacing: -0.5px;
    }
    .auth-card p {
      font-size: 14px;
      color: var(--text-muted);
      margin-bottom: 24px;
    }
    .auth-card input {
      width: 100%;
      padding: 13px 16px;
      border: 1.5px solid var(--border);
      border-radius: 10px;
      font-size: 16px;
      margin-bottom: 16px;
      background: var(--bg);
      color: var(--text);
      outline: none;
      text-align: center;
      letter-spacing: 3px;
      transition: border-color 0.2s;
    }
    .auth-card input:focus {
      border-color: var(--primary);
    }
    .auth-card button {
      width: 100%;
      padding: 13px;
      background: var(--primary);
      color: #fff;
      border: none;
      border-radius: 10px;
      font-size: 15px;
      font-weight: 600;
      cursor: pointer;
      transition: background 0.2s, transform 0.1s;
    }
    .auth-card button:hover {
      background: var(--primary-hover);
    }
    .auth-card button:active {
      transform: scale(0.99);
    }
    .auth-error {
      color: #ef4444;
      font-size: 13px;
      margin-top: 12px;
      display: none;
      font-weight: 500;
    }

    /* 顶部导航 Header */
    .header {
      background: var(--card-bg);
      border-bottom: 1px solid var(--border);
      position: sticky;
      top: 0;
      z-index: 100;
      backdrop-filter: blur(12px);
      box-shadow: var(--shadow-sm);
    }
    .header-inner {
      max-width: 1100px;
      margin: 0 auto;
      padding: 14px 24px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .brand-area {
      display: flex;
      align-items: center;
      gap: 12px;
      text-decoration: none;
    }
    .brand-icon {
      font-size: 24px;
      line-height: 1;
    }
    .brand-title {
      font-size: 17px;
      font-weight: 800;
      letter-spacing: -0.5px;
      color: var(--text);
    }
    .brand-badge {
      font-size: 11px;
      font-weight: 600;
      background: var(--primary-subtle);
      color: var(--primary);
      padding: 2px 8px;
      border-radius: 12px;
      letter-spacing: 0;
    }
    .brand-subtitle {
      font-size: 12px;
      color: var(--text-muted);
      margin-top: 1px;
    }

    .header-actions {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .action-btn {
      background: var(--card-subtle);
      border: 1px solid var(--border);
      color: var(--text-muted);
      padding: 6px 12px;
      border-radius: 8px;
      font-size: 13px;
      font-weight: 500;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      text-decoration: none;
      transition: all 0.2s ease;
    }
    .action-btn:hover {
      color: var(--text);
      border-color: var(--border-focus);
      background: var(--border);
    }
    .action-btn.active {
      color: var(--primary);
      background: var(--primary-subtle);
      border-color: var(--primary);
    }

    /* 主布局容器 */
    .container {
      max-width: 1100px;
      margin: 32px auto;
      padding: 0 24px;
      display: grid;
      grid-template-columns: 1fr 280px;
      gap: 36px;
      flex: 1;
    }
    @media (max-width: 860px) {
      .container {
        grid-template-columns: 1fr;
        margin: 20px auto;
        padding: 0 16px;
        gap: 28px;
      }
      .sidebar {
        order: 2;
      }
    }

    /* 文章主体卡片 */
    .main-card {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 36px 40px;
      box-shadow: var(--shadow-sm);
    }
    @media (max-width: 640px) {
      .main-card {
        padding: 24px 20px;
        border-radius: 12px;
      }
    }

    .meta-bar {
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
      padding-bottom: 20px;
      margin-bottom: 24px;
      border-bottom: 1px solid var(--border);
    }
    .meta-left {
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .status-pill {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      background: var(--accent-tool-bg);
      color: var(--accent-tool);
      padding: 3px 10px;
      border-radius: 20px;
      font-size: 12px;
      font-weight: 600;
    }
    .status-pill::before {
      content: "";
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: currentColor;
    }
    .meta-date {
      font-size: 14px;
      color: var(--text-muted);
      font-weight: 500;
    }

    /* 快捷分类导航胶囊 (Quick Jump Chips) */
    .section-nav {
      background: var(--card-subtle);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 10px 14px;
      margin-bottom: 30px;
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 8px;
    }
    .section-nav-label {
      font-size: 12px;
      font-weight: 700;
      color: var(--text-light);
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-right: 4px;
    }
    .nav-chip {
      background: var(--card-bg);
      border: 1px solid var(--border);
      color: var(--text-muted);
      font-size: 13px;
      font-weight: 500;
      padding: 4px 12px;
      border-radius: 20px;
      cursor: pointer;
      text-decoration: none;
      transition: all 0.15s ease;
    }
    .nav-chip:hover {
      color: var(--primary);
      border-color: var(--primary);
      background: var(--primary-subtle);
    }

    /* 正文样式排版 */
    .article-body h1 { display: none; }
    
    .article-body h2 {
      font-size: 19px;
      font-weight: 800;
      letter-spacing: -0.4px;
      margin-top: 40px;
      margin-bottom: 20px;
      padding: 10px 16px;
      border-radius: 10px;
      display: flex;
      align-items: center;
      gap: 8px;
      background: var(--card-subtle);
      border-left: 4px solid var(--primary);
      color: var(--text);
    }
    /* 专栏特定色彩标记 */
    .article-body h2:has(span[data-sec="monetize"]),
    .article-body h2:contains("商业变现"),
    .article-body h2:contains("变现") {
      border-left-color: var(--accent-monetize);
      background: var(--accent-monetize-bg);
    }
    .article-body h2:contains("本地平替"),
    .article-body h2:contains("上手神器") {
      border-left-color: var(--accent-tool);
      background: var(--accent-tool-bg);
    }
    .article-body h2:contains("行业异动"),
    .article-body h2:contains("降价") {
      border-left-color: var(--accent-alert);
      background: var(--accent-alert-bg);
    }
    .article-body h2:contains("创作者"),
    .article-body h2:contains("选题") {
      border-left-color: var(--accent-creator);
      background: var(--accent-creator-bg);
    }

    .article-body p {
      margin: 16px 0;
      line-height: 1.8;
      color: var(--text);
    }
    .article-body blockquote {
      border-left: 3px solid var(--primary);
      background: var(--primary-subtle);
      padding: 14px 18px;
      margin: 20px 0;
      border-radius: 0 10px 10px 0;
      font-size: 14.5px;
      color: var(--text);
      font-style: normal;
    }
    .article-body strong {
      font-weight: 700;
      color: var(--text);
    }
    .article-body a {
      color: var(--primary);
      text-decoration: none;
      font-weight: 600;
      border-bottom: 1px dotted var(--primary);
      transition: border-bottom 0.2s;
    }
    .article-body a:hover {
      border-bottom-style: solid;
    }
    .article-body ul, .article-body ol {
      margin: 16px 0;
      padding-left: 24px;
    }
    .article-body li {
      margin-bottom: 12px;
      line-height: 1.75;
    }
    .article-body hr {
      border: none;
      height: 1px;
      background: var(--border);
      margin: 36px 0;
    }

    /* 侧边栏 Widget */
    .sidebar {
      display: flex;
      flex-direction: column;
      gap: 24px;
    }
    .widget-card {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 22px;
      box-shadow: var(--shadow-sm);
    }
    .widget-title {
      font-size: 13px;
      font-weight: 700;
      color: var(--text-light);
      text-transform: uppercase;
      letter-spacing: 0.6px;
      margin-bottom: 16px;
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .archive-nav-list {
      list-style: none;
      display: flex;
      flex-direction: column;
      gap: 6px;
      max-height: 380px;
      overflow-y: auto;
      padding-right: 4px;
    }
    .archive-nav-list::-webkit-scrollbar {
      width: 4px;
    }
    .archive-nav-list::-webkit-scrollbar-thumb {
      background: var(--border);
      border-radius: 4px;
    }
    .archive-link {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 8px 12px;
      border-radius: 8px;
      text-decoration: none;
      color: var(--text);
      font-size: 13.5px;
      transition: all 0.15s ease;
    }
    .archive-link:hover {
      background: var(--card-subtle);
      color: var(--primary);
    }
    .archive-link.active {
      background: var(--primary-subtle);
      color: var(--primary);
      font-weight: 700;
    }
    .archive-tag {
      font-size: 11px;
      color: var(--text-light);
      background: var(--card-subtle);
      padding: 2px 6px;
      border-radius: 4px;
    }
    .archive-link.active .archive-tag {
      background: rgba(37, 99, 235, 0.15);
      color: var(--primary);
    }

    .feature-card {
      background: var(--card-subtle);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 14px;
      font-size: 13px;
      line-height: 1.6;
      color: var(--text-muted);
    }
    .feature-card a {
      color: var(--primary);
      text-decoration: none;
      font-weight: 600;
      display: inline-block;
      margin-top: 8px;
    }

    /* 底部 Footer */
    .footer {
      border-top: 1px solid var(--border);
      background: var(--card-bg);
      padding: 32px 24px;
      margin-top: 60px;
      text-align: center;
      font-size: 13px;
      color: var(--text-muted);
    }
    .footer a {
      color: var(--primary);
      text-decoration: none;
    }
  </style>
</head>
<body>
  <!-- 阅读进度条 -->
  <div id="progress-bar"></div>

  <!-- 密码门禁 -->
  <div id="auth-overlay">
    <div class="auth-card">
      <div style="font-size: 40px; margin-bottom: 12px;">🔒</div>
      <h2>半调Felix · 私人前沿情报库</h2>
      <p>专注 AI 商业变现、接地气实操与个人生产力</p>
      <form id="auth-form" onsubmit="event.preventDefault(); verifyPass();">
        <input type="password" id="pass-input" placeholder="输入访问口令" autocomplete="current-password" autofocus />
        <button type="submit">解锁阅读</button>
        <div id="auth-err" class="auth-error">口令错误，请重新输入</div>
      </form>
    </div>
  </div>

  <!-- 顶部导航 -->
  <header class="header">
    <div class="header-inner">
      <a href="/" class="brand-area">
        <span class="brand-icon">⚡</span>
        <div>
          <div style="display: flex; align-items: center; gap: 8px;">
            <span class="brand-title">{{ site_title }}</span>
            <span class="brand-badge">PRO</span>
          </div>
          <div class="brand-subtitle">商业变现 · 接地气实操 · 纯网页端</div>
        </div>
      </a>
      <div class="header-actions">
        <button class="action-btn" id="theme-btn" onclick="toggleTheme();" title="切换明暗主题">
          <span id="theme-icon">🌙</span> <span style="display: none; @media(min-width: 600px){ display: inline; }">外观</span>
        </button>
        <button class="action-btn" onclick="lockSite();" title="锁定站点">
          <span>🔒</span> 锁定
        </button>
      </div>
    </div>
  </header>

  <!-- 主容器 -->
  <div class="container">
    <main class="main-card">
      <!-- 头部元信息 -->
      <div class="meta-bar">
        <div class="meta-left">
          <span class="status-pill">精选 5 大闭环</span>
          <span class="meta-date">📅 {{ date_str }}</span>
        </div>
        <div style="font-size: 13px; color: var(--text-light);">
          <span>⏱️ 阅读约需 5 分钟</span>
        </div>
      </div>

      <!-- 快捷跳跃胶囊 -->
      <div class="section-nav" id="section-nav">
        <span class="section-nav-label">快速跳转</span>
        <button class="nav-chip" onclick="scrollToHeading('行业异动')">⚡ 行业异动</button>
        <button class="nav-chip" onclick="scrollToHeading('商业变现')">💰 商业变现</button>
        <button class="nav-chip" onclick="scrollToHeading('本地平替')">💻 上手神器</button>
        <button class="nav-chip" onclick="scrollToHeading('创作者风控')">🎯 选题与风控</button>
        <button class="nav-chip" onclick="scrollToHeading('暗改排雷')">🔍 暗改排雷</button>
      </div>

      <!-- 正文内容 -->
      <article class="article-body" id="article-content">
        {{ body_html | safe }}
      </article>
    </main>

    <!-- 侧边栏 -->
    <aside class="sidebar">
      <!-- 专栏定位卡 -->
      <div class="widget-card">
        <div class="widget-title">📌 核心聚焦</div>
        <div class="feature-card">
          <p>每日 08:00 自动抓取全球一手信源，专挑「影响个人利益、能变现搞钱、能拿来省时间」的真动态，杜绝公关大词。</p>
          <a href="https://github.com/Felix8686/ai-daily-digest/issues" target="_blank">👉 提交内容反馈 &rarr;</a>
        </div>
      </div>

      <!-- 历史归档列表 -->
      <div class="widget-card">
        <div class="widget-title">📅 历史归档</div>
        <ul class="archive-nav-list">
          {% for item in archives %}
          <li>
            <a href="{{ item.url }}" class="archive-link {% if item.is_current %}active{% endif %}">
              <span>{{ item.date }}</span>
              <span class="archive-tag">{{ item.tag }}</span>
            </a>
          </li>
          {% endfor %}
        </ul>
      </div>
    </aside>
  </div>

  <!-- 页脚 -->
  <footer class="footer">
    <p>© {{ year }} 半调Felix · 基于云端自动化 + DeepSeek 全流程提炼 · 商业洞察与实操沉淀</p>
  </footer>

  <script>
    const CORRECT_PASS = "{{ site_password }}";
    const AUTH_KEY = "ai_digest_auth_token";
    const THEME_KEY = "ai_digest_theme";

    // 1. 主题初始化与切换
    function initTheme() {
      const savedTheme = localStorage.getItem(THEME_KEY);
      const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
      if (savedTheme === "dark" || (!savedTheme && prefersDark)) {
        document.documentElement.classList.add("dark");
        document.getElementById("theme-icon").textContent = "☀️";
      } else {
        document.documentElement.classList.remove("dark");
        document.getElementById("theme-icon").textContent = "🌙";
      }
    }

    function toggleTheme() {
      const isDark = document.documentElement.classList.toggle("dark");
      localStorage.setItem(THEME_KEY, isDark ? "dark" : "light");
      document.getElementById("theme-icon").textContent = isDark ? "☀️" : "🌙";
    }

    // 2. 门禁校验
    function checkAuth() {
      const saved = localStorage.getItem(AUTH_KEY);
      if (saved === CORRECT_PASS) {
        document.getElementById("auth-overlay").style.display = "none";
      } else {
        document.getElementById("auth-overlay").style.display = "flex";
      }
    }

    function verifyPass() {
      const val = document.getElementById("pass-input").value.trim();
      if (val === CORRECT_PASS) {
        localStorage.setItem(AUTH_KEY, val);
        document.getElementById("auth-overlay").style.display = "none";
        document.getElementById("auth-err").style.display = "none";
      } else {
        document.getElementById("auth-err").style.display = "block";
      }
    }

    function lockSite() {
      localStorage.removeItem(AUTH_KEY);
      document.getElementById("pass-input").value = "";
      document.getElementById("auth-overlay").style.display = "flex";
    }

    // 3. 快速平滑滚动跳转
    function scrollToHeading(keyword) {
      const headings = document.querySelectorAll(".article-body h2");
      for (const h of headings) {
        if (h.textContent.includes(keyword)) {
          h.scrollIntoView({ behavior: "smooth", block: "start" });
          h.style.transition = "background-color 0.4s ease";
          const origBg = h.style.backgroundColor;
          h.style.backgroundColor = "var(--primary-subtle)";
          setTimeout(() => { h.style.backgroundColor = origBg; }, 1200);
          return;
        }
      }
    }

    // 4. 阅读进度条
    window.addEventListener("scroll", () => {
      const winScroll = document.body.scrollTop || document.documentElement.scrollTop;
      const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
      const scrolled = height > 0 ? (winScroll / height) * 100 : 0;
      document.getElementById("progress-bar").style.width = scrolled + "%";
    });

    // 立即初始化
    initTheme();
    checkAuth();
  </script>
</body>
</html>
"""

def build_static_site(project_dir: Path, current_markdown: str, today_str: str, cname: str = "news.felix8686.top", site_password: str = "felix8686") -> Path:
    """生成包含 index.html、robots.txt、现代化界面与历史归档的静态站点目录 dist/"""
    dist_dir = project_dir / "dist"
    dist_dir.mkdir(parents=True, exist_ok=True)
    archive_dir = project_dir / "archive"

    # 1. 生成反爬虫 robots.txt
    robots_file = dist_dir / "robots.txt"
    robots_file.write_text("User-agent: *\nDisallow: /\n", encoding="utf-8")
    print("🤖 已生成反爬虫规则文件: dist/robots.txt (Disallow: /)")

    # 2. 扫描所有历史归档
    archive_files = sorted(archive_dir.glob("digest-*.md"), reverse=True)
    archives_meta = []
    for f in archive_files:
        date_part = f.stem.replace("digest-", "")
        is_today = (date_part == dt.date.today().strftime("%Y-%m-%d"))
        archives_meta.append({
            "date": date_part,
            "url": "/" if is_today else f"/archive/{date_part}.html",
            "is_current": is_today,
            "tag": "最新" if is_today else "归档"
        })

    # 3. 渲染今日 index.html
    today_body_html = markdown.markdown(current_markdown, extensions=["extra", "nl2br", "sane_lists"])
    tmpl = Template(WEB_TEMPLATE)
    index_html = tmpl.render(
        site_title="半调Felix 的 AI 提效与商业周刊",
        page_title=today_str,
        date_str=today_str,
        body_html=today_body_html,
        archives=archives_meta,
        year=dt.date.today().year,
        site_password=site_password
    )
    (dist_dir / "index.html").write_text(index_html, encoding="utf-8")

    # 4. 渲染历史文章到 dist/archive/YYYY-MM-DD.html
    dist_archive_dir = dist_dir / "archive"
    dist_archive_dir.mkdir(parents=True, exist_ok=True)
    for f in archive_files:
        date_part = f.stem.replace("digest-", "")
        md_text = f.read_text(encoding="utf-8")
        html_text = markdown.markdown(md_text, extensions=["extra", "nl2br", "sane_lists"])
        page_html = tmpl.render(
            site_title="半调Felix 的 AI 提效与商业周刊",
            page_title=f"{date_part} 归档",
            date_str=date_part,
            body_html=html_text,
            archives=archives_meta,
            year=dt.date.today().year,
            site_password=site_password
        )
        (dist_archive_dir / f"{date_part}.html").write_text(page_html, encoding="utf-8")

    # 5. 写入自定义域名 CNAME
    if cname:
        (dist_dir / "CNAME").write_text(cname.strip(), encoding="utf-8")
        print(f"🌐 已生成 CNAME 绑定: {cname}")

    print(f"🚀 现代化静态网页站点生成完毕！输出目录: {dist_dir} (已集成主题切换、胶囊导航与密码门禁)")
    return dist_dir

if __name__ == "__main__":
    p_dir = Path(__file__).parent
    archive_dir = p_dir / "archive"
    archive_files = sorted(archive_dir.glob("digest-*.md"), reverse=True)
    if archive_files:
        latest_file = archive_files[0]
        date_part = latest_file.stem.replace("digest-", "")
        parts = date_part.split("-")
        date_str = f"{parts[0]}年{parts[1]}月{parts[2]}日" if len(parts) == 3 else date_part
        content = latest_file.read_text(encoding="utf-8")
        build_static_site(p_dir, content, date_str, "news.felix8686.top", "felix8686")
    else:
        print("⚠️ 未找到历史归档")
