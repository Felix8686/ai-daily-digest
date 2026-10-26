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
import re
import time
from typing import Any
from pathlib import Path
from urllib.parse import urlparse, urlunparse
import feedparser
from bs4 import BeautifulSoup
import requests

def normalize_url(url: str) -> str:
    """标准化 URL，去除尾随斜杠、锚点和常见跟踪参数"""
    if not url:
        return ""
    url = url.strip()
    try:
        parsed = urlparse(url)
        query_parts = []
        if parsed.query:
            for q in parsed.query.split("&"):
                k = q.split("=")[0].lower()
                if not (k.startswith("utm_") or k in ("ref", "spm", "from")):
                    query_parts.append(q)
        new_query = "&".join(query_parts)
        return urlunparse((
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            parsed.path.rstrip("/"),
            "",
            new_query,
            ""
        ))
    except Exception:
        return url.rstrip("/")

def extract_historical_urls(archive_dir: Path | None = None, days: int = 14, exclude_date: dt.date | None = None) -> set[str]:
    """从本地 archive 目录的历史 Markdown 简报中提取最近 N 天已收录的链接（排除指定日期如今日，便于同日重新生成）"""
    if archive_dir is None:
        archive_dir = Path(__file__).parent / "archive"
    if not archive_dir.is_dir():
        return set()

    if exclude_date is None:
        exclude_date = dt.date.today()

    seen = set()
    cutoff_date = exclude_date - dt.timedelta(days=days)

    for f in archive_dir.glob("digest-*.md"):
        date_part = f.stem.replace("digest-", "")
        try:
            file_date = dt.datetime.strptime(date_part, "%Y-%m-%d").date()
            if file_date >= exclude_date or file_date < cutoff_date:
                continue
        except ValueError:
            pass

        try:
            content = f.read_text(encoding="utf-8")
            found_urls = re.findall(r'https?://[^\s\)\]\"\'\<\>]+', content)
            for u in found_urls:
                norm = normalize_url(u)
                if norm:
                    seen.add(norm)
        except Exception as e:
            print(f"⚠️ 读取历史归档 {f.name} 出错: {e}")

    print(f"📚 已加载历史归档链接，共 {len(seen)} 个排重目标。")
    return seen

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

def fetch_feed_items(
    feed_cfg: dict, 
    time_window_hours: int = 24, 
    max_items: int = 5,
    seen_urls: set[str] | None = None
) -> list[dict]:
    """抓取单个 RSS 源，返回经过时间过滤、排重和清洗的文章列表"""
    if seen_urls is None:
        seen_urls = set()

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
    # 筛选时间范围内的未收录文章
    for entry in parsed.entries[:25]:
        pub_time = parse_entry_time(entry)
        # 严格基于时间窗口过滤：早于 cutoff 的旧文章坚决剔除
        if pub_time and pub_time < cutoff:
            continue

        link = getattr(entry, "link", "").strip()
        norm_link = normalize_url(link)
        if norm_link and norm_link in seen_urls:
            continue

        raw_summary = getattr(entry, "summary", "") or getattr(entry, "description", "")
        if not raw_summary and hasattr(entry, "content"):
            try:
                raw_summary = entry.content[0].value
            except (IndexError, AttributeError):
                raw_summary = ""

        clean_text = clean_html(raw_summary)
        title = getattr(entry, "title", "无标题").strip()

        items.append({
            "source": name,
            "category": category,
            "title": title,
            "link": link,
            "published_at": pub_time.strftime("%Y-%m-%d %H:%M") if pub_time else "近期",
            "summary": clean_text
        })
        if len(items) >= max_items:
            break

    print(f"✅ [{name}] 获取成功，保留 {len(items)} 条（严格限时与排重）")
    return items

def fetch_all_feeds(config: dict, archive_dir: Path | None = None) -> list[dict]:
    """批量抓取所有已配置的信息源，并执行跨天排重"""
    feeds_config = config.get("feeds", [])
    settings = config.get("settings", {})
    window = settings.get("time_window_hours", 24)
    max_items = settings.get("max_items_per_feed", 5)

    seen_urls = extract_historical_urls(archive_dir=archive_dir, days=14)
    active_seen = set(seen_urls)

    all_articles = []
    for f in feeds_config:
        res = fetch_feed_items(f, time_window_hours=window, max_items=max_items, seen_urls=active_seen)
        for item in res:
            norm = normalize_url(item.get("link", ""))
            if norm:
                active_seen.add(norm)
        all_articles.extend(res)

    print(f"📊 抓取完毕！共获取 {len(all_articles)} 篇新闻文章素材（已过滤往期已报链接）。")
    return all_articles

if __name__ == "__main__":
    from pathlib import Path
    import yaml
    cfg_file = Path(__file__).parent / "config.yaml"
    with open(cfg_file, "r", encoding="utf-8") as fp:
        cfg = yaml.safe_load(fp)
    articles = fetch_all_feeds(cfg)
    print(f"示例第 1 条: {articles[0] if articles else '空'}")

