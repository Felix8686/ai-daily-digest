#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Daily Digest 主入口调度脚本（纯静态网站自动构建与本地归档，支持可选邮件投递）
"""
from __future__ import annotations

import sys
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
        sys.stderr.reconfigure(encoding="utf-8", line_buffering=True)
    except Exception:
        pass

import argparse
import datetime as dt
import os
from pathlib import Path
import yaml
from dotenv import load_dotenv

from fetcher import fetch_all_feeds
from summarizer import generate_daily_digest
from mailer import render_email_html, send_digest_email
from site_builder import build_static_site

BASE_DIR = Path(__file__).parent
load_dotenv(BASE_DIR / ".env")

CONFIG_PATH = BASE_DIR / "config.yaml"
ARCHIVE_DIR = BASE_DIR / "archive"

def load_config() -> dict:
    if not CONFIG_PATH.is_file():
        raise FileNotFoundError(f"配置文件不存在: {CONFIG_PATH}")
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def run_digest(dry_run: bool = False, test_mail: bool = False, force_send_mail: bool = False):
    config = load_config()
    today_str = dt.date.today().strftime("%Y年%m月%d日")
    subject = f"⚡ 【AI 提效与商业变现精选】{today_str}"

    if test_mail:
        print("🧪 正在执行测试发信模式...")
        test_md = f"### 这是一封来自 AI Daily Digest 的测试邮件\n\n系统工作正常！当前时间: {dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        html = render_email_html("AI Daily Digest 发信测试", today_str, 0, test_md)
        send_digest_email("🧪 [测试] AI Daily Digest 邮件测试", html, test_md)
        return

    # 1. 抓取新闻源素材
    print("🚀 第一步: 开始抓取配置的订阅源素材（含商业变现、上手神器与行业异动）...")
    articles = fetch_all_feeds(config, archive_dir=ARCHIVE_DIR)
    if not articles:
        print("⚠️ 未抓取到任何符合条件的文章，任务结束。")
        return

    # 2. 调用大模型提炼晨报
    print(f"🤖 第二步: 调用大模型总结 {len(articles)} 篇新闻素材（精选 5 大闭环板块）...")
    summary_md = generate_daily_digest(articles, config)

    # 保存存档到本地 archive 目录
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    today_tag = dt.date.today().strftime("%Y-%m-%d")
    archive_file = ARCHIVE_DIR / f"digest-{today_tag}.md"
    archive_file.write_text(summary_md, encoding="utf-8")
    print(f"💾 今日简报已自动存档至: {archive_file}")

    # 3. 构建静态站点 (dist/ 目录)
    site_pwd = config.get("settings", {}).get("site_password", "felix8686")
    cname = config.get("settings", {}).get("cname", "news.felix8686.top")
    print("🌐 第三步: 生成高颜值静态网页与历史归档 (dist/)...")
    build_static_site(BASE_DIR, summary_md, today_str, cname=cname, site_password=site_pwd)

    if dry_run:
        print(f"🔍 [Dry-Run] 模式已开启，未实际发信。")
        print("\n" + "=" * 40 + " 今日简报内容 " + "=" * 40)
        print(summary_md)
        print("=" * 90)
        return

    # 4. 邮件推送检查（默认停用，转为纯网页驱动）
    enable_email = force_send_mail or config.get("settings", {}).get("enable_email", False)
    if enable_email:
        print("📧 第四步: 正在通过 SMTP 发送至订阅邮箱...")
        html_content = render_email_html("AI 全景实操与商业变现精选", today_str, len(articles), summary_md, site_password=site_pwd)
        send_digest_email(subject, html_content, summary_md)
        print("✅ 邮件投递完成！")
    else:
        print("ℹ️ 邮件推送已停用，系统已转为纯静态网页驱动模式 (访问: https://news.felix8686.top)")

    print("🎉 今日简报生成与网页更新任务全部完成！")

def main():
    parser = argparse.ArgumentParser(description="AI Daily Digest 自动化网页站点与归档系统")
    parser.add_argument("--dry-run", action="store_true", help="仅抓取并生成本地 HTML/MD 预览，不发送邮件")
    parser.add_argument("--test-mail", action="store_true", help="仅测试 SMTP 发信配置是否正常")
    parser.add_argument("--send-mail", action="store_true", help="显式开启单次邮件发送（默认关闭）")
    args = parser.parse_args()

    try:
        run_digest(dry_run=args.dry_run, test_mail=args.test_mail, force_send_mail=args.send_mail)
    except Exception as e:
        print(f"\n❌ 执行遇到异常: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
