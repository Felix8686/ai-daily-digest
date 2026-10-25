#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
静态网页与历史归档站点生成器 (含反爬虫 robots.txt、noindex 与前端密码门禁)
"""
from __future__ import annotations

import sys
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
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
      --text: #0f172a;
      --text-muted: #64748b;
      --border: #e2e8f0;
      --primary: #2563eb;
      --primary-hover: #1d4ed8;
      --tag-bg: #eff6ff;
      --tag-text: #1d4ed8;
    }
    @media (prefers-color-scheme: dark) {
      :root {
        --bg: #090d16;
        --card-bg: #131b2e;
        --text: #f1f5f9;
        --text-muted: #94a3b8;
        --border: #1e293b;
        --primary: #3b82f6;
        --primary-hover: #60a5fa;
        --tag-bg: #1e293b;
        --tag-text: #93c5fd;
      }
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background-color: var(--bg);
      color: var(--text);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
      line-height: 1.7;
    }
    /* 密码门禁遮罩层 */
    #auth-overlay {
      position: fixed;
      inset: 0;
      background: rgba(9, 13, 22, 0.85);
      backdrop-filter: blur(12px);
      z-index: 9999;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 20px;
    }
    .auth-card {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 36px 32px;
      max-width: 400px;
      width: 100%;
      text-align: center;
      box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
    }
    .auth-card h2 {
      font-size: 20px;
      margin-bottom: 8px;
    }
    .auth-card p {
      font-size: 13px;
      color: var(--text-muted);
      margin-bottom: 24px;
    }
    .auth-card input {
      width: 100%;
      padding: 12px 16px;
      border: 1px solid var(--border);
      border-radius: 8px;
      font-size: 15px;
      margin-bottom: 16px;
      background: var(--bg);
      color: var(--text);
      outline: none;
      text-align: center;
      letter-spacing: 2px;
    }
    .auth-card input:focus {
      border-color: var(--primary);
    }
    .auth-card button {
      width: 100%;
      padding: 12px;
      background: var(--primary);
      color: #fff;
      border: none;
      border-radius: 8px;
      font-size: 15px;
      font-weight: 600;
      cursor: pointer;
      transition: background 0.2s;
    }
    .auth-card button:hover {
      background: var(--primary-hover);
    }
    .auth-error {
      color: #ef4444;
      font-size: 13px;
      margin-top: 12px;
      display: none;
    }

    .header {
      background: var(--card-bg);
      border-bottom: 1px solid var(--border);
      padding: 24px 20px;
      position: sticky;
      top: 0;
      z-index: 50;
      backdrop-filter: blur(8px);
    }
    .header-inner {
      max-width: 900px;
      margin: 0 auto;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .logo-area h1 {
      font-size: 20px;
      font-weight: 800;
      letter-spacing: -0.5px;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .logo-area p {
      font-size: 13px;
      color: var(--text-muted);
      margin-top: 2px;
    }
    .nav-links {
      display: flex;
      gap: 16px;
      align-items: center;
      font-size: 14px;
    }
    .nav-links a {
      color: var(--text-muted);
      text-decoration: none;
      transition: color 0.2s;
    }
    .nav-links a:hover { color: var(--primary); }
    .btn-lock {
      background: none;
      border: 1px solid var(--border);
      padding: 4px 10px;
      border-radius: 6px;
      color: var(--text-muted);
      cursor: pointer;
      font-size: 12px;
    }
    .btn-lock:hover { color: #ef4444; border-color: #ef4444; }

    .container {
      max-width: 900px;
      margin: 36px auto;
      padding: 0 20px;
      display: grid;
      grid-template-columns: 1fr 240px;
      gap: 32px;
    }
    @media (max-width: 768px) {
      .container { grid-template-columns: 1fr; }
      .sidebar { order: 2; }
    }
    .main-content {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 36px 32px;
      box-shadow: 0 4px 20px rgba(0,0,0,0.02);
    }
    .post-meta {
      display: flex;
      gap: 12px;
      align-items: center;
      margin-bottom: 24px;
      padding-bottom: 16px;
      border-bottom: 1px solid var(--border);
      font-size: 13px;
      color: var(--text-muted);
    }
    .badge {
      background: var(--tag-bg);
      color: var(--tag-text);
      padding: 3px 10px;
      border-radius: 20px;
      font-weight: 600;
      font-size: 12px;
    }
    .article-body h1 { display: none; }
    .article-body h2 {
      font-size: 20px;
      margin-top: 32px;
      margin-bottom: 16px;
      padding-bottom: 8px;
      border-bottom: 2px solid var(--border);
      color: var(--text);
    }
    .article-body p {
      margin: 14px 0;
      font-size: 15px;
      color: var(--text);
    }
    .article-body blockquote {
      border-left: 3px solid var(--primary);
      padding: 10px 16px;
      margin: 16px 0;
      background: var(--tag-bg);
      border-radius: 0 8px 8px 0;
      font-size: 14px;
    }
    .article-body a {
      color: var(--primary);
      text-decoration: none;
      font-weight: 600;
    }
    .article-body a:hover { text-decoration: underline; }
    .article-body ul {
      padding-left: 20px;
      margin: 14px 0;
    }
    .article-body li {
      margin-bottom: 10px;
      font-size: 15px;
    }
    .sidebar {
      display: flex;
      flex-direction: column;
      gap: 24px;
    }
    .sidebar-widget {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 20px;
    }
    .sidebar-widget h3 {
      font-size: 14px;
      font-weight: 700;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-bottom: 14px;
    }
    .archive-list {
      list-style: none;
      display: flex;
      flex-direction: column;
      gap: 8px;
      font-size: 14px;
    }
    .archive-list a {
      color: var(--text);
      text-decoration: none;
      display: flex;
      justify-content: space-between;
      transition: color 0.15s;
    }
    .archive-list a:hover { color: var(--primary); }
    .archive-list a.active {
      color: var(--primary);
      font-weight: 700;
    }
    .feedback-box {
      font-size: 13px;
      color: var(--text-muted);
      line-height: 1.6;
    }
    .feedback-box a {
      display: inline-block;
      margin-top: 10px;
      color: var(--primary);
      font-weight: 600;
      text-decoration: none;
    }
    .footer {
      text-align: center;
      padding: 40px 20px;
      font-size: 13px;
      color: var(--text-muted);
      border-top: 1px solid var(--border);
      margin-top: 60px;
    }
  </style>
</head>
<body>
  <!-- 密码门禁 -->
  <div id="auth-overlay">
    <div class="auth-card">
      <h2>🔒 私人档案库</h2>
      <p>本站点为个人订阅精选 · 请输入访问口令</p>
      <form id="auth-form" onsubmit="event.preventDefault(); verifyPass();">
        <input type="password" id="pass-input" placeholder="输入访问密码" autocomplete="current-password" autofocus />
        <button type="submit">解锁访问</button>
        <div id="auth-err" class="auth-error">口令错误，请重试</div>
      </form>
    </div>
  </div>

  <header class="header">
    <div class="header-inner">
      <div class="logo-area">
        <h1>⚡ {{ site_title }}</h1>
        <p>专注接地气实操、轻量自动化与个人知识库 · 每日更新</p>
      </div>
      <div class="nav-links">
        <a href="/">今日最新</a>
        <a href="https://github.com/Felix8686/ai-daily-digest/issues" target="_blank">提交反馈</a>
        <button class="btn-lock" onclick="lockSite();" title="锁定站点">🔒 锁定</button>
      </div>
    </div>
  </header>

  <div class="container">
    <main class="main-content">
      <div class="post-meta">
        <span class="badge">🔥 闭环精选</span>
        <span>📅 {{ date_str }}</span>
        <span>✍️ 主理人: 半调Felix</span>
      </div>
      <article class="article-body">
        {{ body_html | safe }}
      </article>
    </main>

    <aside class="sidebar">
      <div class="sidebar-widget">
        <h3>💬 内容反馈与调优</h3>
        <div class="feedback-box">
          <p>觉得哪些板块有用？哪些内容遥远或不感兴趣？随时告诉大模型，下次自动避开。</p>
          <a href="https://github.com/Felix8686/ai-daily-digest/issues/new?title=%5B%E5%8F%8D%E9%A6%88%5D+%E5%AF%B9%E8%BF%91%E6%9C%9F%E5%86%85%E5%AE%B9%E7%9A%84%E5%81%8F%E5%A5%BD%E8%B0%83%E6%95%B4" target="_blank">👉 提交内容偏好建议 &rarr;</a>
        </div>
      </div>

      <div class="sidebar-widget">
        <h3>📅 历史归档</h3>
        <ul class="archive-list">
          {% for item in archives %}
          <li>
            <a href="{{ item.url }}" class="{% if item.is_current %}active{% endif %}">
              <span>{{ item.date }}</span>
              <span style="color: var(--text-muted);">{{ item.tag }}</span>
            </a>
          </li>
          {% endfor %}
        </ul>
      </div>
    </aside>
  </div>

  <footer class="footer">
    <p>© {{ year }} 半调Felix · 基于 GitHub Actions + DeepSeek 全自动化运行 · 保持好奇心与独立思考</p>
  </footer>

  <script>
    const CORRECT_PASS = "{{ site_password }}";
    const AUTH_KEY = "ai_digest_auth_token";

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

    // 立即执行校验
    checkAuth();
  </script>
</body>
</html>
"""

def build_static_site(project_dir: Path, current_markdown: str, today_str: str, cname: str = "news.felix8686.top", site_password: str = "felix8686") -> Path:
    """生成包含 index.html、robots.txt、密码遮罩与历史归档的静态站点目录 dist/"""
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
        site_title="半调Felix 的 AI 提效周刊",
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
            site_title="半调Felix 的 AI 提效周刊",
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

    print(f"🚀 静态网页站点生成完毕！输出目录: {dist_dir} (已配置前端口令与反爬)")
    return dist_dir

if __name__ == "__main__":
    p_dir = Path(__file__).parent
    sample_md = (p_dir / "archive" / f"digest-{dt.date.today().strftime('%Y-%m-%d')}.md").read_text(encoding="utf-8")
    build_static_site(p_dir, sample_md, dt.date.today().strftime("%Y年%m月%d日"), "news.felix8686.top", "felix8686")
