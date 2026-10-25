#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大模型提炼与总结模块
支持 Google Gemini (推荐) 与 OpenAI 兼容接口 (DeepSeek, 阿里百炼等)
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

import json
import datetime as dt

SYSTEM_PROMPT = """你是一名资深的全球 AI 科技主编兼投资分析师。
你的任务是将传入的全球 AI 行业多源新闻与技术文章，加工为一份极具信息价值、结构严谨、语言精炼的【AI 行业每日晨报】。

输出规范与格式要求：
1. 语言：简体中文。
2. 过滤噪声：剔除毫无实质内容的公关稿与重复同质化新闻，精选最关键事件。
3. 结构分块：
   - 🌟 【今日头条 / Top Stories】：精选 2~3 条最具行业冲击力的重大事件，附带 1 句精炼的影响力点评。
   - 🤖 【大厂动态与模型进展】：涵盖 OpenAI、Google、Anthropic、开源模型（Llama/Qwen 等）的核心发布与迭代。
   - 🛠️ 【实用工具与落地产品】：适合开发者或职场人的高生产力 AI 工具、Agent 平台或开源项目。
   - 💡 【深度观察与学术研究】：重磅 Paper（如 Hugging Face 趋势）、行业政策或专栏观点。
4. 每条条目格式：
   - **[文章标题(翻译为精炼中文)](原始URL)** (来源: 媒体名称)
   - 1~2 句直接说明「核心更新是什么」以及「对开发者/行业的意义」，拒绝废话。
5. 末尾生成一句话「今日行业思考 / Takeaway」。
"""

def summarize_with_gemini(articles: list[dict], api_key: str, model_name: str = "gemini-2.5-flash") -> str:
    """使用 Google GenAI 官方 SDK 调用 Gemini"""
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        raise ImportError("请先安装 google-genai: pip install google-genai")

    client = genai.Client(api_key=api_key)

    # 组装文章列表提示词
    items_text = []
    for idx, item in enumerate(articles, 1):
        items_text.append(
            f"{idx}. [{item.get('category')}] {item.get('source')}: {item.get('title')}\n"
            f"   链接: {item.get('link')}\n"
            f"   发布时间: {item.get('published_at')}\n"
            f"   正文摘要: {item.get('summary')[:400]}"
        )
    articles_payload = "\n\n".join(items_text)

    prompt = f"""今天是 {dt.date.today().strftime('%Y年%m月%d日')}。
以下是从各官方源与顶级科技媒体抓取的最新资讯素材（共 {len(articles)} 条）：

{articles_payload}

请严格按照规范生成今天的【AI 每日早报】（以优雅的 Markdown 格式输出）。"""

    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.3,
        )
    )
    return response.text

def summarize_with_openai_compatible(articles: list[dict], api_key: str, base_url: str | None = None, model_name: str = "deepseek-chat") -> str:
    """使用 OpenAI 兼容协议（如 DeepSeek, Moonshot, 阿里百炼等）"""
    import requests

    endpoint = f"{base_url.rstrip('/')}/chat/completions" if base_url else "https://api.openai.com/v1/chat/completions"
    
    items_text = []
    for idx, item in enumerate(articles, 1):
        items_text.append(
            f"{idx}. [{item.get('category')}] {item.get('source')}: {item.get('title')}\n"
            f"   链接: {item.get('link')}\n"
            f"   发布时间: {item.get('published_at')}\n"
            f"   正文摘要: {item.get('summary')[:400]}"
        )
    articles_payload = "\n\n".join(items_text)

    prompt = f"""今天是 {dt.date.today().strftime('%Y年%m月%d日')}。
以下是从各官方源与顶级科技媒体抓取的最新资讯素材（共 {len(articles)} 条）：

{articles_payload}

请严格按照规范生成今天的【AI 每日早报】（以优雅的 Markdown 格式输出）。"""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }
    resp = requests.post(endpoint, headers=headers, json=data, timeout=60)
    resp.raise_for_status()
    res_json = resp.json()
    return res_json["choices"][0]["message"]["content"]

def generate_daily_digest(articles: list[dict], config: dict) -> str:
    """统一生成总结入口"""
    if not articles:
        return "今日暂无满足筛选条件的重大新闻更新。"

    settings = config.get("settings", {})
    provider = settings.get("llm_provider", "gemini")

    # 优先检测环境变量中的 Key
    gemini_key = os.environ.get("GEMINI_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")

    if provider == "gemini" and gemini_key:
        print("🧠 正在使用 Google Gemini 生成每日摘要...")
        model = settings.get("gemini_model", "gemini-2.5-flash")
        return summarize_with_gemini(articles, api_key=gemini_key, model_name=model)
    elif openai_key:
        print("🧠 正在使用 OpenAI 兼容 API 生成每日摘要...")
        base_url = os.environ.get("OPENAI_BASE_URL")
        model = os.environ.get("OPENAI_MODEL", "deepseek-chat")
        return summarize_with_openai_compatible(articles, api_key=openai_key, base_url=base_url, model_name=model)
    else:
        print("⚠️ 未检测到 API Key，正在以本地离线摘要模式生成预览...")
        # 本地离线样例模式
        mock_lines = [
            "## 🌟 【今日头条 / Top Stories】",
            f"- **[{articles[0]['title']}]({articles[0]['link']})** (来源: {articles[0]['source']})",
            f"  > 摘要概述: {articles[0]['summary'][:120]}...",
            "",
            "## 🤖 【大厂动态与模型进展】"
        ]
        for a in articles[1:4]:
            mock_lines.append(f"- **[{a['title']}]({a['link']})** (来源: {a['source']})")
            mock_lines.append(f"  {a['summary'][:100]}...\n")

        mock_lines.extend([
            "## 🛠️ 【实用工具与落地产品】",
        ])
        for a in articles[4:7]:
            mock_lines.append(f"- **[{a['title']}]({a['link']})** (来源: {a['source']})")
            mock_lines.append(f"  {a['summary'][:100]}...\n")

        mock_lines.extend([
            "## 💡 【今日行业思考 / Takeaway】",
            "全球 AI 产业正加速从「单点模型发布」向「工程化落地与垂直商业化」延伸，端侧大模型与垂直 Agent 生态进入爆发期。"
        ])
        return "\n".join(mock_lines)

