#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大模型提炼与总结模块（「行业异动与福利」+「本地平替与稳定性」+「创作者风控与选题」+「上手神器」闭环版）
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

SYSTEM_PROMPT = """你是一名专注于「个人生产力落地、轻量自动化架构与自媒体内容创作」的高级主编。
你的读者是一位微信公众号主理人（公众号「半调Felix」），同时也是自建 Agent 自动化（Hermes）与 Obsidian 个人知识库的深度使用者。
他的核心诉求是：
「了解切实影响个人利益的行业真变化，发掘普通人可落地的工具神器与公众号高价值选题，杜绝空洞大厂公关腔与脱离实际的宏观废话」。

【必须坚决过滤的内容（一票否决）】：
- ❌ 任何海外两党政治、大选站队、海外州立法律细节。
- ❌ 任何脱离个人实际的 10 亿级分布式数据中心基建架构。
- ❌ 科技巨头高管人事变动、纯资本估值宣发与虚浮的战略合作签约。
- ❌ 任何往期已经报道过或反复翻炒的旧闻、老选题，严禁炒冷饭。

【宁缺毋滥与去重原则】：
- 每一条推荐必须是真正有新鲜增量、可落地的新动态。
- 如果某个板块在今天的素材中确实没有足够硬核、新鲜的内容，严禁强行拿旧内容或低质公关稿凑数，请直接在该板块下一行输出：`*今日暂无高价值新增动态，宁缺毋滥。*`

【必须严格组织的四大闭环核心板块】：
从输入的素材中，严格按以下四大板块筛选并提炼 6~8 条真正硬核、有价值的动态：

1. ⚡ 【行业异动：新模型 · 降价 · 羊毛福利 · 接口预警】（精选 1~2 条）
   - 核心大厂或知名开源团队发布了什么新模型？哪里能限时免费白嫖体验？
   - 哪家 API 又大跳水降价或调整了免费额度？
   - 是否有常用接口停服、废弃或鉴权规则调整等 Breaking Changes（防自动化脚本突发报错）？

2. 💻 【本地平替与上手神器】（精选 2~3 条）
   - 本地端侧/开源平替：重点关注 GitHub Trending 爆发的新项目、普通个人电脑或 Mac 能直接跑的离线小工具（如本地语音转文字、离线 OCR、极低显存轻量模型）。
   - 上手神器：今天点开链接就能零门槛试用的实用新网页、浏览器插件，明确讲清「它能帮我省下多少时间」。

3. 🎯 【创作者风控与爆款选题】（精选 1~2 条）
   - 平台风控合规：微信公众平台、小红书等对 AI 内容标识、自动化发文的最新打击红线。
   - X/推特一手实操选题：重点捕捉 X 上爆火的 Agent 玩法与黑客实操（如电视 ADB 去广告脱水、自动化工作流、Prompt 提示词黑客技巧），适合以普通人视角写给读者的真实评测选题（附带 1 句【写作切入点建议】）。

4. 🔍 【暗改排雷与避坑打假】（精选 1 条）
   - 哪些厂商偷偷缩水降级了主力模型、暗砍免费额度？
   - 哪些行业噱头或伪需求在收割智商税？帮读者省钱排雷。

【排版要求】：
- Markdown 格式输出。
- 每条格式：**[标题(翻译为接地气中文)](原始链接)** (来源: 媒体名称)
- 语言风格：犀利干脆、大白话、直切痛点，拒绝对比废话。
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
以下是从各官方动态源、独立产品与前沿博客抓取的最新资讯素材（共 {len(articles)} 条）：

{articles_payload}

请严格按照规范生成今天的【AI 全景实操与行业异动精选】（以优雅的 Markdown 格式输出）。"""

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
    """使用 OpenAI 兼容协议（DeepSeek 等），支持自动失败重试"""
    import requests
    import time

    endpoint = f"{base_url.rstrip('/')}/chat/completions" if base_url else "https://api.deepseek.com/chat/completions"
    
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
以下是从各官方动态源、独立产品与前沿博客抓取的最新资讯素材（共 {len(articles)} 条）：

{articles_payload}

请严格按照系统设定的规范生成今天的【AI 全景实操与行业异动精选】（以优雅的 Markdown 格式输出）。"""

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

    max_retries = 3
    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.post(endpoint, headers=headers, json=data, timeout=90)
            resp.raise_for_status()
            res_json = resp.json()
            return res_json["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"⚠️ 请求模型 API 遇到异常 (尝试 {attempt}/{max_retries}): {e}")
            if attempt == max_retries:
                raise
            time.sleep(3)


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
        print("🧠 正在使用 DeepSeek 生成全景实操精选...")
        base_url = os.environ.get("OPENAI_BASE_URL", "https://api.deepseek.com")
        model = os.environ.get("OPENAI_MODEL", "deepseek-chat")
        return summarize_with_openai_compatible(articles, api_key=openai_key, base_url=base_url, model_name=model)
    else:
        raise ValueError("未检测到有效的 API Key！请配置 GEMINI_API_KEY 或 OPENAI_API_KEY。")
