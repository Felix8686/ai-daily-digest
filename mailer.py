#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
邮件渲染与 SMTP 发送模块
"""
from __future__ import annotations

import sys
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import os

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from pathlib import Path
import markdown
from jinja2 import Template

TEMPLATE_PATH = Path(__file__).parent / "template.html"

def render_email_html(title: str, date_str: str, article_count: int, markdown_content: str, site_password: str = "felix8686") -> str:
    """将 Markdown 转换为带精美 CSS 样式的完整 HTML 邮件"""
    # 转换 Markdown 为 HTML，启用表格与常见扩展
    body_html = markdown.markdown(
        markdown_content,
        extensions=["extra", "nl2br", "sane_lists"]
    )
    
    if TEMPLATE_PATH.is_file():
        template_str = TEMPLATE_PATH.read_text(encoding="utf-8")
        tmpl = Template(template_str)
        return tmpl.render(
            title=title,
            date=date_str,
            article_count=article_count,
            body_html=body_html,
            site_password=site_password
        )
    else:
        # 极简备用 HTML
        return f"<html><body><h1>{title}</h1><div>{body_html}</div></body></html>"

def send_digest_email(
    subject: str,
    html_content: str,
    plain_text: str = ""
) -> bool:
    """通过 SMTP 发送邮件，配置从环境变量读取"""
    host = os.environ.get("SMTP_HOST")
    port = int(os.environ.get("SMTP_PORT", 465))
    user = os.environ.get("SMTP_USER")
    password = os.environ.get("SMTP_PASS")
    receiver = os.environ.get("RECEIVER_EMAIL")

    if not all([host, user, password, receiver]):
        missing = [k for k, v in [("SMTP_HOST", host), ("SMTP_USER", user), ("SMTP_PASS", password), ("RECEIVER_EMAIL", receiver)] if not v]
        raise ValueError(f"缺少 SMTP 环境变量配置: {', '.join(missing)}")

    # 支持多个收件人逗号分割
    receivers = [r.strip() for r in receiver.split(",") if r.strip()]

    msg = MIMEMultipart("alternative")
    msg["Subject"] = Header(subject, "utf-8")
    msg["From"] = f"AI Daily Digest <{user}>"
    msg["To"] = ", ".join(receivers)

    # 优先使用纯文本备用，主要渲染 HTML
    if plain_text:
        msg.attach(MIMEText(plain_text, "plain", "utf-8"))
    msg.attach(MIMEText(html_content, "html", "utf-8"))

    print(f"📧 正在通过 {host}:{port} 发送邮件至: {receivers}...")

    try:
        if port == 465:
            # SSL 加密
            server = smtplib.SMTP_SSL(host, port, timeout=20)
        else:
            # 普通端口或 587 STARTTLS
            server = smtplib.SMTP(host, port, timeout=20)
            server.starttls()

        server.login(user, password)
        server.sendmail(user, receivers, msg.as_string())
        server.quit()
        print("🎉 邮件发送成功！")
        return True
    except Exception as e:
        print(f"❌ 邮件发送失败: {e}")
        raise
