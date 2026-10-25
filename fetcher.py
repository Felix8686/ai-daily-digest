#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RSS / Feed 抓取与清洗模块
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

import time
from typing import Any
import feedparser
from bs4 import BeautifulSoup
import requests

def clean_html(raw_html: str) -> str:
    """去除 HTML 标签，返回纯文本"""
    if not raw_html:
        return ""
    soup = BeautifulSoup(raw_html, "html.parser")
    # 去除 script 和 style
    for elem in soup(["script", "style", "noscript"]):
        elem.extract()
    text = soup.get_text(separator=" ", strip=True)
    return " ".join(text.split())[:800]

def parse_entry_time(entry: Any) -> dt.datetime | None:
    """解析文章发布时间，转换为带 UTC 时区的 datetime"""
    st = getattr(entry, "published_parsed", None) or getattr(entry, "updated_parsed", None)
    if st:
        try:
            return dt.datetime.fromtimestamp(time.mktime(st), tz=dt.timezone.utc)
        except Exception:
            pass
    return None

def fetch_feed_items(feed_cfg: dict, time_window_hours: int = 24, max_items: int = 5) -> list[dict]:
    """抓取单个 RSS 源，返回经过时间过滤和清洗的文章列表"""
    name = feed_cfg.get("name", "Unknown Source")
    category = feed_cfg.get("category", "综合资讯")
    url = feed_cfg.get("url")

    now = dt.datetime.now(dt.timezone.utc)
    cutoff = now - dt.timedelta(hours=time_window_hours)

    print(f"📡 抓取源: [{category}] {name} -> {url}")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml;q=0.9, */*;q=0.8"
    }

    try:
        resp = requests.get(url, headers=headers, timeout=12)
        resp.raise_for_status()
        content = resp.content
    except Exception as e:
        print(f"⚠️ 网络请求失败 [{name}]: {e}")
        return []

    parsed = feedparser.parse(content)
    if not parsed.entries:
        print(f"ℹ️ [{name}] 未解析到条目")
        return []

    items = []
    # 优先筛选时间范围内的
    for entry in parsed.entries[:15]:
        pub_time = parse_entry_time(entry)
        raw_summary = getattr(entry, "summary", "") or getattr(entry, "description", "")
        # 如果某些源有 content 字段
        if not raw_summary and hasattr(entry, "content"):
            try:
                raw_summary = entry.content[0].value
            except (IndexError, AttributeError):
                raw_summary = ""

        clean_text = clean_html(raw_summary)
        link = getattr(entry, "link", "")
        title = getattr(entry, "title", "无标题").strip()

        # 检查是否在时间范围内
        is_recent = False
        if pub_time:
            is_recent = (pub_time >= cutoff)
        else:
            # 若无法解析时间，保留最新 1~2 条
            is_recent = True

        if is_recent:
            items.append({
                "source": name,
                "category": category,
                "title": title,
                "link": link,
                "published_at": pub_time.strftime("%Y-%m-%d %H:%M") if pub_time else "未知",
                "summary": clean_text
            })
            if len(items) >= max_items:
                break

    # 兜底：如果最近 24 小时没有任何更新（例如周刊 Import AI），则取最新 1 篇
    if not items and parsed.entries:
        top_entry = parsed.entries[0]
        pub_time = parse_entry_time(top_entry)
        raw_summary = getattr(top_entry, "summary", "") or getattr(top_entry, "description", "")
        items.append({
            "source": name,
            "category": category,
            "title": getattr(top_entry, "title", "无标题").strip(),
            "link": getattr(top_entry, "link", ""),
            "published_at": pub_time.strftime("%Y-%m-%d %H:%M") if pub_time else "近期",
            "summary": clean_html(raw_summary)
        })

    print(f"✅ [{name}] 获取成功，保留 {len(items)} 条")
    return items

def fetch_all_feeds(config: dict) -> list[dict]:
    """批量抓取所有已配置的信息源"""
    feeds_config = config.get("feeds", [])
    settings = config.get("settings", {})
    window = settings.get("time_window_hours", 24)
    max_items = settings.get("max_items_per_feed", 5)

    all_articles = []
    for f in feeds_config:
        res = fetch_feed_items(f, time_window_hours=window, max_items=max_items)
        all_articles.extend(res)

    print(f"📊 抓取完毕！共获取 {len(all_articles)} 篇新闻文章素材。")
    return all_articles

if __name__ == "__main__":
    from pathlib import Path
    import yaml
    cfg_file = Path(__file__).parent / "config.yaml"
    with open(cfg_file, "r", encoding="utf-8") as fp:
        cfg = yaml.safe_load(fp)
    articles = fetch_all_feeds(cfg)
    print(f"示例第 1 条: {articles[0] if articles else '空'}")

