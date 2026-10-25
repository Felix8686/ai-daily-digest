#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Daily Digest 主入口调度脚本
"""
from __future__ import annotations

import sys
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import argparse
import datetime as dt

import os
import sys
from pathlib import Path
import yaml
from dotenv import load_dotenv

from fetcher import fetch_all_feeds
from summarizer import generate_daily_digest
from mailer import render_email_html, send_digest_email

# 优先加载当前目录或上级目录的 .env 文件
BASE_DIR = Path(__file__).parent
load_dotenv(BASE_DIR / ".env")

CONFIG_PATH = BASE_DIR / "config.yaml"
ARCHIVE_DIR = BASE_DIR / "archive"

def load_config() -> dict:
    if not CONFIG_PATH.is_file():
        raise FileNotFoundError(f"配置文件不存在: {CONFIG_PATH}")
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def run_digest(dry_run: bool = False, test_mail: bool = False):
    config = load_config()
    today_str = dt.date.today().strftime("%Y年%m月%d日")
    subject = f"⚡ 【AI 提效与实操精选】{today_str} · 写作选题与上手工具"

    if test_mail:
        print("🧪 正在执行测试发信模式...")
        test_md = f"### 这是一封来自 AI Daily Digest 的测试邮件\n\n系统工作正常！当前时间: {dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        html = render_email_html("AI Daily Digest 发信测试", today_str, 0, test_md)
        send_digest_email("🧪 [测试] AI Daily Digest 邮件测试", html, test_md)
        return

    # 1. 抓取新闻源素材
    print("🚀 第一步: 开始抓取配置的订阅源素材...")
    articles = fetch_all_feeds(config)
    if not articles:
        print("⚠️ 未抓取到任何符合条件的文章，任务结束。")
        return

    # 2. 调用大模型提炼晨报
    print(f"🤖 第二步: 调用大模型总结 {len(articles)} 篇新闻文章...")
    summary_md = generate_daily_digest(articles, config)

    # 3. 渲染为精美 HTML 邮件
    print("🎨 第三步: 渲染响应式 HTML 邮件...")
    html_content = render_email_html("AI 行业每日早报", today_str, len(articles), summary_md)

    # 保存存档到本地 archive 目录
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    today_tag = dt.date.today().strftime("%Y-%m-%d")
    archive_file = ARCHIVE_DIR / f"digest-{today_tag}.md"
    archive_file.write_text(summary_md, encoding="utf-8")
    print(f"💾 今日简报已自动存档至: {archive_file}")

    if dry_run:
        preview_html_path = BASE_DIR / "preview.html"
        preview_html_path.write_text(html_content, encoding="utf-8")
        print(f"🔍 [Dry-Run] 模式已开启，未实际发信。")
        print(f"👉 预览文件已生成: {preview_html_path}")
        print("\n" + "=" * 40 + " 今日简报内容 " + "=" * 40)
        print(summary_md)
        print("=" * 90)
        return

    # 4. 发送邮件
    print("📧 第四步: 正在通过 SMTP 发送至订阅邮箱...")
    send_digest_email(subject, html_content, summary_md)
    print("✅ 今日推送任务全部完成！")

def main():
    parser = argparse.ArgumentParser(description="AI Daily Digest 自动化邮件推送系统")
    parser.add_argument("--dry-run", action="store_true", help="仅抓取并生成本地 HTML/MD 预览，不发送邮件")
    parser.add_argument("--test-mail", action="store_true", help="仅测试 SMTP 发信配置是否正常")
    args = parser.parse_args()

    try:
        run_digest(dry_run=args.dry_run, test_mail=args.test_mail)
    except Exception as e:
        print(f"\n❌ 执行遇到异常: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
