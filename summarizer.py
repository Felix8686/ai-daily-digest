#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大模型提炼与总结模块（接地气·个人实操与内容创作定制版）
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

SYSTEM_PROMPT = """你是一名专注于「个人生产力落地、轻量自动化与个人知识库」的资深内容主编。
你的读者是一位微信公众号主理人（公众号「半调Felix」），其核心定位是：
「以真诚、非程序员、接地气的普通人视角，输出高质量 AI 提效、工具实操、思维认知与变现经验，杜绝空洞假大空的 AI 味与公关说辞」。

【绝对禁止收录（一票否决）】：
- ❌ 任何关于美国大选、政治立场、海外两党争论的内容。
- ❌ 任何地方性立法案、海外政策研讨会文稿。
- ❌ 任何脱离个人实际的宏大底层基建（如 10 亿用户超大规模分布式数据中心架构）。
- ❌ 科技巨头高管人事变动、八卦诉讼或资本估值吹嘘。

【必须遵循的四大板块与筛选准绳】：
从输入的多源素材中，严格挑选与普通人、个人创作者、轻量开发者强相关的 6~8 条高价值信息，按以下板块呈现：

1. 🎯 【公众号爆款选题与实战灵感】（精选 1~2 条）
   - 最值得拆解成推文写给读者的选题（贴合：小白、踩坑、复盘、避坑、真实体验）。
   - 附带 1 句【写作切入点建议】：教读者如何从普通人角度去写。

2. 🛠️ 【今天就能上手玩的新神器】（精选 2~3 条）
   - 点开链接就能免费玩或低门槛试用的新产品、新网站、Chrome 插件或桌面小工具。
   - 说明：它是干嘛的？怎么帮我省时间？

3. 🧠 【个人知识库与 Agent 玩法】（精选 1~2 条）
   - 与个人知识沉淀（如 Obsidian、Markdown）、单人轻量 Agent（如 Hermes 体系）、实用 Prompt 或高性价比模型调用（如 DeepSeek、端侧模型）相关的实操动态。

4. 💡 【独立变现与避坑提醒】（精选 1 条）
   - 单人单机利用 AI 探索副业、变现或自动化流程的案例复盘；或揭露虚假宣传、收割智商税的排雷提醒。

【排版格式】：
- Markdown 格式输出。
- 每条包含：**[文章/工具标题(翻译为接地气中文)](原始链接)** (来源: 媒体名称)
- 语言风格：精炼干脆、通俗易懂、直击痛点，拒绝打官腔与假大空。
"""

def summarize_with_gemini(articles: list[dict], api_key: str, model_name: str = "gemini-2.5-flash") -> str:
    """使用 Google GenAI 官方 SDK 调用 Gemini"""
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)

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
以下是从各实操源、独立产品与前沿博客抓取的最新资讯素材（共 {len(articles)} 条）：

{articles_payload}

请严格按照规范生成今天的【AI 实操与提效每日精选】（以优雅的 Markdown 格式输出）。"""

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
    """使用 OpenAI 兼容协议（DeepSeek 等）"""
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
以下是从各实操源、独立产品与前沿博客抓取的最新资讯素材（共 {len(articles)} 条）：

{articles_payload}

请严格按照系统设定的规范生成今天的【AI 实操与提效每日精选】（以优雅的 Markdown 格式输出）。"""

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
    provider = settings.get("llm_provider", "openai_compatible")

    gemini_key = os.environ.get("GEMINI_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")

    if provider == "gemini" and gemini_key:
        print("🧠 正在使用 Google Gemini 生成实操精选...")
        model = settings.get("gemini_model", "gemini-2.5-flash")
        return summarize_with_gemini(articles, api_key=gemini_key, model_name=model)
    elif openai_key:
        print("🧠 正在使用 DeepSeek (OpenAI 协议) 生成实操精选...")
        base_url = os.environ.get("OPENAI_BASE_URL", "https://api.deepseek.com")
        model = os.environ.get("OPENAI_MODEL", "deepseek-chat")
        return summarize_with_openai_compatible(articles, api_key=openai_key, base_url=base_url, model_name=model)
    else:
        raise ValueError("未检测到有效的 API Key！请配置 GEMINI_API_KEY 或 OPENAI_API_KEY。")
