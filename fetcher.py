#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RSS / Feed 抓取与清洗模块（集成跨天排重 + 本地已用工具过滤 + GitHub老旧项目拦截）
"""
from __future__ import annotations

import sys
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
        sys.stderr.reconfigure(encoding="utf-8", line_buffering=True)
    except Exception:
        pass

import os
import datetime as dt
import re
import time
from typing import Any
from pathlib import Path
from urllib.parse import urlparse, urlunparse
import feedparser
from bs4 import BeautifulSoup
import requests

_GITHUB_AGE_CACHE: dict[str, tuple[bool, int, str]] = {}

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

def discover_local_known_skills() -> set[str]:
    """自动扫描本机或服务器已安装的技能与工具目录"""
    candidates = [
        Path("D:/Codex Projects/AI-Tools/codex-skills"),
        Path("D:/Codex Projects/AI-Tools"),
        Path("D:/antigravity/.agents/skills"),
        Path.home() / ".agents" / "skills",
        Path.home() / ".gemini" / "config" / "skills",
        Path("/home/mzer8/.agents/skills"),
        Path("/home/mzer8/.agent-reach"),
    ]
    discovered = set()
    for base in candidates:
        try:
            if base.is_dir():
                for p in base.iterdir():
                    if p.is_dir() and not p.name.startswith("."):
                        discovered.add(p.name.lower())
        except Exception:
            pass
    return discovered

def get_known_tools_set(config: dict) -> set[str]:
    """合并配置中的 known_tools 与本地自动发现的技能库"""
    filters_cfg = config.get("filters", {})
    configured = filters_cfg.get("known_tools", [])
    result = {str(item).strip().lower() for item in configured if item}
    result.update(discover_local_known_skills())
    return result

def is_known_or_excluded_item(title: str, link: str, summary: str, known_tools: set[str]) -> tuple[bool, str]:
    """判断当前条目是否命中读者已知工具/技能黑名单"""
    if not known_tools:
        return False, ""

    gh_match = re.search(r'github\.com/([^/]+/[^/#\?]+)', link, re.IGNORECASE)
    gh_slug = gh_match.group(1).rstrip('.git').lower() if gh_match else ""
    gh_repo_name = gh_slug.split('/')[-1] if '/' in gh_slug else ""

    title_lower = title.lower()
    summary_lower = summary[:300].lower()

    for tool in known_tools:
        t = tool.strip().lower()
        if not t:
            continue
        # 1. 精确匹配完整 slug
        if '/' in t and gh_slug == t:
            return True, tool
        # 2. 精确匹配 repo 名
        if gh_repo_name and gh_repo_name == t:
            return True, tool
        # 3. 匹配标题或链接中的单词边界
        pattern = r'(?<![a-zA-Z0-9_-])' + re.escape(t) + r'(?![a-zA-Z0-9_-])'
        if re.search(pattern, title_lower):
            return True, tool
        if gh_slug and re.search(pattern, gh_slug):
            return True, tool

    return False, ""

def check_github_repo_age(link: str, max_age_days: int) -> tuple[bool, int, str]:
    """
    检查 GitHub 仓库的创建时间，拦截老项目重新翻红冲榜。
    返回: (是否通过(True为新项目/无法确认, False为老项目), 项目已存在天数, 创建时间字符串)
    """
    gh_match = re.search(r'github\.com/([^/]+/[^/#\?]+)', link, re.IGNORECASE)
    if not gh_match:
        return True, 0, ""

    slug = gh_match.group(1).rstrip('.git')
    if slug.lower().startswith(('trending', 'topics', 'collections', 'explore', 'orgs')):
        return True, 0, ""

    if slug in _GITHUB_AGE_CACHE:
        return _GITHUB_AGE_CACHE[slug]

    api_url = f"https://api.github.com/repos/{slug}"
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; AIDailyDigest/2.0)",
        "Accept": "application/vnd.github.v3+json"
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"token {token}"

    try:
        resp = requests.get(api_url, headers=headers, timeout=4)
        if resp.status_code == 200:
            data = resp.json()
            created_at_str = data.get("created_at")
            if created_at_str:
                created_at = dt.datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
                now = dt.datetime.now(dt.timezone.utc)
                days_old = (now - created_at).days
                if days_old > max_age_days:
                    res = (False, days_old, created_at.strftime("%Y-%m-%d"))
                    _GITHUB_AGE_CACHE[slug] = res
                    return res
                else:
                    res = (True, days_old, created_at.strftime("%Y-%m-%d"))
                    _GITHUB_AGE_CACHE[slug] = res
                    return res
    except Exception:
        pass

    res = (True, 0, "")
    _GITHUB_AGE_CACHE[slug] = res
    return res

def clean_html(raw_html: str) -> str:
    """去除 HTML 标签，返回纯文本"""
    if not raw_html:
        return ""
    soup = BeautifulSoup(raw_html, "html.parser")
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
    seen_urls: set[str] | None = None,
    known_tools: set[str] | None = None,
    max_repo_age_days: int = 90
) -> list[dict]:
    """抓取单个 RSS 源，返回经过时间过滤、排重、黑名单过滤和清洗的文章列表"""
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
    for entry in parsed.entries[:25]:
        pub_time = parse_entry_time(entry)
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

        # 1. 过滤读者已知技能/工具黑名单
        if known_tools:
            is_known, matched_tool = is_known_or_excluded_item(title, link, clean_text, known_tools)
            if is_known:
                print(f"  🚫 过滤已知/已安装技能 [{title}]: 命中读者已知工具黑名单 '{matched_tool}'")
                continue

        # 2. 针对 GitHub 仓库校验项目创建时间（防止老项目二次翻红被当做新工具）
        if max_repo_age_days and "github.com" in link:
            is_new, days_old, created_str = check_github_repo_age(link, max_repo_age_days)
            if not is_new:
                print(f"  ⌛ 过滤老旧仓库 [{title}]: 创建于 {created_str} ({days_old}天前)，超过 {max_repo_age_days} 天限制")
                continue

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
    """批量抓取所有已配置的信息源，并执行跨天排重与已知工具过滤"""
    feeds_config = config.get("feeds", [])
    settings = config.get("settings", {})
    window = settings.get("time_window_hours", 24)
    max_items = settings.get("max_items_per_feed", 5)
    max_repo_age_days = settings.get("github_max_repo_age_days", 90)

    seen_urls = extract_historical_urls(archive_dir=archive_dir, days=14)
    active_seen = set(seen_urls)
    known_tools = get_known_tools_set(config)
    print(f"🛡️ 已加载已知工具/技能排除库，共 {len(known_tools)} 个过滤标识（含自动扫描）。")

    all_articles = []
    for f in feeds_config:
        res = fetch_feed_items(
            f, 
            time_window_hours=window, 
            max_items=max_items, 
            seen_urls=active_seen,
            known_tools=known_tools,
            max_repo_age_days=max_repo_age_days
        )
        for item in res:
            norm = normalize_url(item.get("link", ""))
            if norm:
                active_seen.add(norm)
        all_articles.extend(res)

    print(f"📊 抓取完毕！共获取 {len(all_articles)} 篇新闻文章素材（已过滤往期已报链接与已知工具）。")
    return all_articles

if __name__ == "__main__":
    import yaml
    cfg_file = Path(__file__).parent / "config.yaml"
    with open(cfg_file, "r", encoding="utf-8") as fp:
        cfg = yaml.safe_load(fp)
    articles = fetch_all_feeds(cfg)
    print(f"示例第 1 条: {articles[0] if articles else '空'}")
