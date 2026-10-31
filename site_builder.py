#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
静态网页与历史归档站点生成器（全新现代化极简杂志风、分类导航、明暗主题切换、收藏/派发与安全门禁）
"""
from __future__ import annotations

import sys
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
        sys.stderr.reconfigure(encoding="utf-8", line_buffering=True)
    except Exception:
        pass

import datetime as dt
import hashlib
from pathlib import Path
import markdown
from bs4 import BeautifulSoup
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
      --card-subtle: #f1f5f9;
      --text: #0f172a;
      --text-muted: #64748b;
      --text-light: #94a3b8;
      --border: #e2e8f0;
      --border-focus: #cbd5e1;
      --primary: #2563eb;
      --primary-hover: #1d4ed8;
      --primary-subtle: #eff6ff;
      --accent-monetize: #7c3aed;
      --accent-monetize-bg: #f5f3ff;
      --accent-tool: #059669;
      --accent-tool-bg: #ecfdf5;
      --accent-alert: #d97706;
      --accent-alert-bg: #fffbeb;
      --accent-creator: #e11d48;
      --accent-creator-bg: #fff1f2;
      --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
      --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.07), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
      --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.08), 0 4px 6px -4px rgba(0, 0, 0, 0.04);
    }
    
    html.dark {
      --bg: #090d16;
      --card-bg: #111827;
      --card-subtle: #1f2937;
      --text: #f3f4f6;
      --text-muted: #9ca3af;
      --text-light: #6b7280;
      --border: #1f2937;
      --border-focus: #374151;
      --primary: #3b82f6;
      --primary-hover: #60a5fa;
      --primary-subtle: #1e293b;
      --accent-monetize: #a78bfa;
      --accent-monetize-bg: rgba(139, 92, 246, 0.12);
      --accent-tool: #34d399;
      --accent-tool-bg: rgba(16, 185, 129, 0.12);
      --accent-alert: #fbbf24;
      --accent-alert-bg: rgba(245, 158, 11, 0.12);
      --accent-creator: #fb7185;
      --accent-creator-bg: rgba(244, 63, 94, 0.12);
      --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.3);
      --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.4);
      --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.5);
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }
    
    body {
      background-color: var(--bg);
      color: var(--text);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
      line-height: 1.75;
      font-size: 15px;
      transition: background-color 0.25s ease, color 0.25s ease;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }

    /* 顶部阅读进度条 */
    #progress-bar {
      position: fixed;
      top: 0;
      left: 0;
      height: 3px;
      background: linear-gradient(90deg, var(--primary), var(--accent-monetize));
      width: 0%;
      z-index: 999;
      transition: width 0.1s ease-out;
    }

    /* 密码门禁遮罩层 */
    #auth-overlay {
      position: fixed;
      inset: 0;
      background: rgba(9, 13, 22, 0.88);
      backdrop-filter: blur(16px);
      z-index: 10000;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 20px;
    }
    .auth-card {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 20px;
      padding: 40px 32px;
      max-width: 420px;
      width: 100%;
      text-align: center;
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.35);
    }
    .auth-card h2 {
      font-size: 22px;
      font-weight: 800;
      margin-bottom: 8px;
      letter-spacing: -0.5px;
    }
    .auth-card p {
      font-size: 14px;
      color: var(--text-muted);
      margin-bottom: 24px;
    }
    .auth-card input {
      width: 100%;
      padding: 13px 16px;
      border: 1.5px solid var(--border);
      border-radius: 10px;
      font-size: 16px;
      margin-bottom: 16px;
      background: var(--bg);
      color: var(--text);
      outline: none;
      text-align: center;
      letter-spacing: 3px;
      transition: border-color 0.2s;
    }
    .auth-card input:focus {
      border-color: var(--primary);
    }
    .auth-card button {
      width: 100%;
      padding: 13px;
      background: var(--primary);
      color: #fff;
      border: none;
      border-radius: 10px;
      font-size: 15px;
      font-weight: 600;
      cursor: pointer;
      transition: background 0.2s, transform 0.1s;
    }
    .auth-card button:hover {
      background: var(--primary-hover);
    }
    .auth-card button:active {
      transform: scale(0.99);
    }
    .auth-error {
      color: #ef4444;
      font-size: 13px;
      margin-top: 12px;
      display: none;
      font-weight: 500;
    }

    /* 顶部导航 Header */
    .header {
      background: var(--card-bg);
      border-bottom: 1px solid var(--border);
      position: sticky;
      top: 0;
      z-index: 100;
      backdrop-filter: blur(12px);
      box-shadow: var(--shadow-sm);
    }
    .header-inner {
      max-width: 1100px;
      margin: 0 auto;
      padding: 14px 24px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .brand-area {
      display: flex;
      align-items: center;
      gap: 12px;
      text-decoration: none;
    }
    .brand-icon {
      font-size: 24px;
      line-height: 1;
    }
    .brand-title {
      font-size: 17px;
      font-weight: 800;
      letter-spacing: -0.5px;
      color: var(--text);
    }
    .brand-badge {
      font-size: 11px;
      font-weight: 600;
      background: var(--primary-subtle);
      color: var(--primary);
      padding: 2px 8px;
      border-radius: 12px;
      letter-spacing: 0;
    }
    .brand-subtitle {
      font-size: 12px;
      color: var(--text-muted);
      margin-top: 1px;
    }

    .header-actions {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .action-btn {
      background: var(--card-subtle);
      border: 1px solid var(--border);
      color: var(--text-muted);
      padding: 6px 12px;
      border-radius: 8px;
      font-size: 13px;
      font-weight: 500;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      text-decoration: none;
      transition: all 0.2s ease;
    }
    .action-btn:hover {
      color: var(--text);
      border-color: var(--border-focus);
      background: var(--border);
    }
    .action-btn.active {
      color: var(--primary);
      background: var(--primary-subtle);
      border-color: var(--primary);
    }

    /* 主布局容器 */
    .container {
      max-width: 1100px;
      margin: 32px auto;
      padding: 0 24px;
      display: grid;
      grid-template-columns: 1fr 280px;
      gap: 36px;
      flex: 1;
    }
    @media (max-width: 860px) {
      .container {
        grid-template-columns: 1fr;
        margin: 20px auto;
        padding: 0 16px;
        gap: 28px;
      }
      .sidebar {
        order: 2;
      }
    }

    /* 文章主体卡片 */
    .main-card {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 36px 40px;
      box-shadow: var(--shadow-sm);
    }
    @media (max-width: 640px) {
      .main-card {
        padding: 24px 20px;
        border-radius: 12px;
      }
    }

    .meta-bar {
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
      padding-bottom: 20px;
      margin-bottom: 24px;
      border-bottom: 1px solid var(--border);
    }
    .meta-left {
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .status-pill {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      background: var(--accent-tool-bg);
      color: var(--accent-tool);
      padding: 3px 10px;
      border-radius: 20px;
      font-size: 12px;
      font-weight: 600;
    }
    .status-pill::before {
      content: "";
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: currentColor;
    }
    .meta-date {
      font-size: 14px;
      color: var(--text-muted);
      font-weight: 500;
    }

    /* 快捷分类导航胶囊 (Quick Jump Chips) */
    .section-nav {
      background: var(--card-subtle);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 10px 14px;
      margin-bottom: 30px;
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 8px;
    }
    .section-nav-label {
      font-size: 12px;
      font-weight: 700;
      color: var(--text-light);
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-right: 4px;
    }
    .nav-chip {
      background: var(--card-bg);
      border: 1px solid var(--border);
      color: var(--text-muted);
      font-size: 13px;
      font-weight: 500;
      padding: 4px 12px;
      border-radius: 20px;
      cursor: pointer;
      text-decoration: none;
      transition: all 0.15s ease;
    }
    .nav-chip:hover {
      color: var(--primary);
      border-color: var(--primary);
      background: var(--primary-subtle);
    }
    .nav-chip.nav-chip-fav {
      background: var(--card-bg);
      border-color: #f59e0b;
      color: #d97706;
      font-weight: 600;
    }
    html.dark .nav-chip.nav-chip-fav {
      color: #fbbf24;
    }
    .nav-chip.nav-chip-fav:hover {
      background: rgba(245, 158, 11, 0.15);
    }
    .nav-chip.nav-chip-fav.active {
      background: #f59e0b;
      color: #ffffff;
      border-color: #f59e0b;
    }

    /* 收藏筛选空状态 */
    .fav-empty-banner {
      display: none;
      background: var(--card-subtle);
      border: 1px dashed var(--border-focus);
      border-radius: 12px;
      padding: 32px 24px;
      text-align: center;
      margin: 24px 0;
      color: var(--text-muted);
      font-size: 14px;
    }
    .fav-empty-banner h3 {
      font-size: 16px;
      color: var(--text);
      margin-bottom: 6px;
    }

    /* 正文样式排版 */
    .article-body h1 { display: none; }
    
    .article-body h2 {
      font-size: 18px;
      font-weight: 800;
      letter-spacing: -0.4px;
      margin-top: 36px;
      margin-bottom: 18px;
      padding: 10px 16px;
      border-radius: 10px;
      display: flex;
      align-items: center;
      gap: 8px;
      background: var(--card-subtle);
      border-left: 4px solid var(--primary);
      color: var(--text);
    }

    /* 专栏特定色彩标记 */
    .article-body h2[data-category="monetize"] {
      border-left-color: var(--accent-monetize);
      background: var(--accent-monetize-bg);
    }
    .article-body h2[data-category="tool"] {
      border-left-color: var(--accent-tool);
      background: var(--accent-tool-bg);
    }
    .article-body h2[data-category="trend"] {
      border-left-color: var(--accent-alert);
      background: var(--accent-alert-bg);
    }
    .article-body h2[data-category="creator"] {
      border-left-color: var(--accent-creator);
      background: var(--accent-creator-bg);
    }

    .article-body p {
      margin: 14px 0;
      line-height: 1.8;
      color: var(--text);
    }
    .article-body blockquote {
      border-left: 3px solid var(--primary);
      background: var(--primary-subtle);
      padding: 14px 18px;
      margin: 20px 0;
      border-radius: 0 10px 10px 0;
      font-size: 14.5px;
      color: var(--text);
      font-style: normal;
    }
    .article-body strong {
      font-weight: 700;
      color: var(--text);
    }
    .article-body a {
      color: var(--primary);
      text-decoration: none;
      font-weight: 600;
      border-bottom: 1px dotted var(--primary);
      transition: border-bottom 0.2s;
    }
    .article-body a:hover {
      border-bottom-style: solid;
    }

    /* 单条情报交互卡片 (News Card) */
    .news-card {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 22px 24px;
      margin: 20px 0;
      box-shadow: var(--shadow-sm);
      transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
      position: relative;
    }
    .news-card:hover {
      border-color: var(--border-focus);
      box-shadow: var(--shadow-md);
      transform: translateY(-1px);
    }

    /* 板块细致侧边标识线 */
    .news-card.cat-trend { border-left: 4px solid var(--accent-alert); }
    .news-card.cat-monetize { border-left: 4px solid var(--accent-monetize); }
    .news-card.cat-tool { border-left: 4px solid var(--accent-tool); }
    .news-card.cat-creator { border-left: 4px solid var(--accent-creator); }
    .news-card.cat-alert { border-left: 4px solid #ef4444; }

    .news-card-body p:first-child {
      margin-top: 0;
      font-size: 16px;
      line-height: 1.6;
    }
    .news-card-body p:last-child {
      margin-bottom: 0;
    }

    /* 卡片底栏操作区 */
    .news-card-actions {
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
      margin-top: 18px;
      padding-top: 14px;
      border-top: 1px dashed var(--border);
    }
    .action-left-info {
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .card-cat-badge {
      font-size: 11px;
      font-weight: 600;
      padding: 2px 8px;
      border-radius: 6px;
      background: var(--card-subtle);
      color: var(--text-muted);
      border: 1px solid var(--border);
    }
    .action-right-btns {
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .item-action-btn {
      background: var(--card-subtle);
      border: 1px solid var(--border);
      color: var(--text-muted);
      border-radius: 8px;
      padding: 5px 12px;
      font-size: 12.5px;
      font-weight: 500;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 5px;
      transition: all 0.15s ease;
      outline: none;
    }
    .item-action-btn:hover {
      color: var(--text);
      border-color: var(--border-focus);
      background: var(--border);
    }
    
    /* 收藏高亮状态 */
    .item-action-btn.fav-btn.is-fav {
      background: rgba(245, 158, 11, 0.14);
      border-color: #f59e0b;
      color: #d97706;
      font-weight: 600;
    }
    html.dark .item-action-btn.fav-btn.is-fav {
      color: #fbbf24;
    }
    .item-action-btn.fav-btn.is-fav .star-icon {
      color: #f59e0b;
      transform: scale(1.15);
    }

    /* 分享按钮悬停 */
    .item-action-btn.share-btn:hover {
      color: var(--primary);
      border-color: var(--primary);
      background: var(--primary-subtle);
    }

    /* 侧边栏 Widget */
    .sidebar {
      display: flex;
      flex-direction: column;
      gap: 24px;
    }
    .widget-card {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 22px;
      box-shadow: var(--shadow-sm);
    }
    .widget-title {
      font-size: 13px;
      font-weight: 700;
      color: var(--text-light);
      text-transform: uppercase;
      letter-spacing: 0.6px;
      margin-bottom: 16px;
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .archive-nav-list {
      list-style: none;
      display: flex;
      flex-direction: column;
      gap: 6px;
      max-height: 380px;
      overflow-y: auto;
      padding-right: 4px;
    }
    .archive-nav-list::-webkit-scrollbar {
      width: 4px;
    }
    .archive-nav-list::-webkit-scrollbar-thumb {
      background: var(--border);
      border-radius: 4px;
    }
    .archive-link {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 8px 12px;
      border-radius: 8px;
      text-decoration: none;
      color: var(--text);
      font-size: 13.5px;
      transition: all 0.15s ease;
    }
    .archive-link:hover {
      background: var(--card-subtle);
      color: var(--primary);
    }
    .archive-link.active {
      background: var(--primary-subtle);
      color: var(--primary);
      font-weight: 700;
    }
    .archive-tag {
      font-size: 11px;
      color: var(--text-light);
      background: var(--card-subtle);
      padding: 2px 6px;
      border-radius: 4px;
    }
    .archive-link.active .archive-tag {
      background: rgba(37, 99, 235, 0.15);
      color: var(--primary);
    }

    .feature-card {
      background: var(--card-subtle);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 14px;
      font-size: 13px;
      line-height: 1.6;
      color: var(--text-muted);
    }
    .feature-card a {
      color: var(--primary);
      text-decoration: none;
      font-weight: 600;
      display: inline-block;
      margin-top: 8px;
    }

    /* 派发与分享弹窗 Modal */
    #share-modal {
      position: fixed;
      inset: 0;
      background: rgba(9, 13, 22, 0.75);
      backdrop-filter: blur(8px);
      z-index: 10001;
      display: none;
      align-items: center;
      justify-content: center;
      padding: 20px;
    }
    .share-modal-card {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 18px;
      max-width: 520px;
      width: 100%;
      box-shadow: var(--shadow-lg);
      padding: 26px 28px;
      animation: modalFadeIn 0.2s cubic-bezier(0.16, 1, 0.3, 1);
    }
    @keyframes modalFadeIn {
      from { opacity: 0; transform: translateY(10px) scale(0.98); }
      to { opacity: 1; transform: translateY(0) scale(1); }
    }
    .modal-head {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 14px;
      border-bottom: 1px solid var(--border);
      padding-bottom: 12px;
    }
    .modal-head h3 {
      font-size: 17px;
      font-weight: 700;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .modal-close-btn {
      background: none;
      border: none;
      font-size: 18px;
      color: var(--text-light);
      cursor: pointer;
      padding: 4px;
      border-radius: 6px;
    }
    .modal-close-btn:hover {
      color: var(--text);
      background: var(--card-subtle);
    }
    .modal-item-title {
      font-size: 14px;
      font-weight: 600;
      color: var(--text);
      background: var(--card-subtle);
      border-radius: 8px;
      padding: 10px 14px;
      margin-bottom: 18px;
      line-height: 1.5;
      border: 1px solid var(--border);
      max-height: 80px;
      overflow-y: auto;
    }
    .modal-action-list {
      display: flex;
      flex-direction: column;
      gap: 10px;
    }
    .modal-action-btn {
      background: var(--card-subtle);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 12px 16px;
      text-align: left;
      font-size: 14px;
      font-weight: 500;
      color: var(--text);
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: space-between;
      transition: all 0.15s ease;
      text-decoration: none;
    }
    .modal-action-btn:hover {
      background: var(--primary-subtle);
      border-color: var(--primary);
      color: var(--primary);
    }
    .modal-action-btn .btn-left {
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .modal-action-btn .btn-desc {
      font-size: 12px;
      color: var(--text-muted);
      margin-top: 2px;
    }

    /* 浮动轻提示 Toast */
    #toast-notify {
      position: fixed;
      bottom: 28px;
      left: 50%;
      transform: translateX(-50%) translateY(100px);
      background: #0f172a;
      color: #ffffff;
      padding: 10px 20px;
      border-radius: 30px;
      font-size: 13.5px;
      font-weight: 500;
      box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
      z-index: 10002;
      opacity: 0;
      pointer-events: none;
      transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.25s ease;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    html.dark #toast-notify {
      background: #ffffff;
      color: #0f172a;
    }
    #toast-notify.show {
      transform: translateX(-50%) translateY(0);
      opacity: 1;
    }

    /* 页脚 Footer */
    .footer {
      border-top: 1px solid var(--border);
      background: var(--card-bg);
      padding: 32px 24px;
      margin-top: 60px;
      text-align: center;
      font-size: 13px;
      color: var(--text-muted);
    }
    .footer a {
      color: var(--primary);
      text-decoration: none;
    }
  </style>
</head>
<body>
  <!-- 阅读进度条 -->
  <div id="progress-bar"></div>

  <!-- 浮动轻提示 -->
  <div id="toast-notify"></div>

  <!-- 派发与分享弹窗 -->
  <div id="share-modal" onclick="if(event.target === this) closeShareModal();">
    <div class="share-modal-card">
      <div class="modal-head">
        <h3><span>🔗</span> 派发与分享情报</h3>
        <button class="modal-close-btn" onclick="closeShareModal();" title="关闭">✕</button>
      </div>
      <div class="modal-item-title" id="modal-target-title">情报标题</div>
      <div class="modal-action-list">
        <!-- 动作 1: 发送到 Telegram / Hermes -->
        <a id="btn-share-tg" href="#" target="_blank" class="modal-action-btn">
          <div class="btn-left">
            <span style="font-size: 20px;">🤖</span>
            <div>
              <div>发送至 Telegram / Hermes</div>
              <div class="btn-desc">调用 TG 接口预填结构化深度调研 Prompt</div>
            </div>
          </div>
          <span>&rarr;</span>
        </a>

        <!-- 动作 2: 复制 Codex 终端指令 -->
        <button type="button" class="modal-action-btn" onclick="copyCodexCommand();">
          <div class="btn-left">
            <span style="font-size: 20px;">💻</span>
            <div>
              <div>复制 Codex / Agent 终端指令</div>
              <div class="btn-desc">生成 <code>codex "调研并评估..."</code> 粘贴即跑</div>
            </div>
          </div>
          <span style="font-size: 12px; font-weight: 600;">📋 复制</span>
        </button>

        <!-- 动作 3: 复制完整 Prompt 研报指令 -->
        <button type="button" class="modal-action-btn" onclick="copyFullPrompt();">
          <div class="btn-left">
            <span style="font-size: 20px;">📝</span>
            <div>
              <div>复制深度调研完整 Prompt</div>
              <div class="btn-desc">适合粘贴到 ChatGPT / Claude / Gemini 深度追问</div>
            </div>
          </div>
          <span style="font-size: 12px; font-weight: 600;">📋 复制</span>
        </button>

        <!-- 动作 4: 复制原文链接 -->
        <button type="button" class="modal-action-btn" onclick="copyOriginalLink();">
          <div class="btn-left">
            <span style="font-size: 20px;">🔗</span>
            <div>
              <div>复制原始情报链接</div>
              <div class="btn-desc">纯净 URL，便于快速转发与查阅</div>
            </div>
          </div>
          <span style="font-size: 12px; font-weight: 600;">📋 复制</span>
        </button>
      </div>
    </div>
  </div>

  <!-- 密码门禁 -->
  <div id="auth-overlay">
    <div class="auth-card">
      <div style="font-size: 40px; margin-bottom: 12px;">🔒</div>
      <h2>半调Felix · 私人前沿情报库</h2>
      <p>专注 AI 商业变现、接地气实操与个人生产力</p>
      <form id="auth-form" onsubmit="event.preventDefault(); verifyPass();">
        <input type="password" id="pass-input" placeholder="输入访问口令" autocomplete="current-password" autofocus />
        <button type="submit">解锁阅读</button>
        <div id="auth-err" class="auth-error">口令错误，请重新输入</div>
      </form>
    </div>
  </div>

  <!-- 顶部导航 -->
  <header class="header">
    <div class="header-inner">
      <a href="/" class="brand-area">
        <span class="brand-icon">⚡</span>
        <div>
          <div style="display: flex; align-items: center; gap: 8px;">
            <span class="brand-title">{{ site_title }}</span>
            <span class="brand-badge">PRO</span>
          </div>
          <div class="brand-subtitle">商业变现 · 接地气实操 · 纯网页端</div>
        </div>
      </a>
      <div class="header-actions">
        <button class="action-btn" id="theme-btn" onclick="toggleTheme();" title="切换明暗主题">
          <span id="theme-icon">🌙</span> <span style="display: none; @media(min-width: 600px){ display: inline; }">外观</span>
        </button>
        <button class="action-btn" onclick="lockSite();" title="锁定站点">
          <span>🔒</span> 锁定
        </button>
      </div>
    </div>
  </header>

  <!-- 主容器 -->
  <div class="container">
    <main class="main-card">
      <!-- 头部元信息 -->
      <div class="meta-bar">
        <div class="meta-left">
          <span class="status-pill">精选 5 大闭环</span>
          <span class="meta-date">📅 {{ date_str }}</span>
        </div>
        <div style="font-size: 13px; color: var(--text-light);">
          <span>⏱️ 阅读约需 5 分钟</span>
        </div>
      </div>

      <!-- 快捷跳转胶囊 -->
      <div class="section-nav" id="section-nav">
        <span class="section-nav-label">快速跳转</span>
        <button class="nav-chip" onclick="scrollToHeading('行业异动')">⚡ 行业异动</button>
        <button class="nav-chip" onclick="scrollToHeading('商业变现')">💰 商业变现</button>
        <button class="nav-chip" onclick="scrollToHeading('本地平替')">💻 上手神器</button>
        <button class="nav-chip" onclick="scrollToHeading('创作者风控')">🎯 选题与风控</button>
        <button class="nav-chip" onclick="scrollToHeading('暗改排雷')">🔍 暗改排雷</button>
        <button class="nav-chip nav-chip-fav" id="filter-fav-btn" onclick="toggleFavoritesFilter();">⭐ 我的收藏 (<span id="fav-count">0</span>)</button>
      </div>

      <!-- 收藏夹过滤空状态提示 -->
      <div id="fav-empty-banner" class="fav-empty-banner">
        <h3>⭐ 暂未收藏任何情报</h3>
        <p>在任意新闻卡片底部点击【⭐ 收藏】，即可将感兴趣的情报沉淀在此处快速查阅。</p>
      </div>

      <!-- 正文内容 -->
      <article class="article-body" id="article-content">
        {{ body_html | safe }}
      </article>
    </main>

    <!-- 侧边栏 -->
    <aside class="sidebar">
      <!-- 专栏定位卡 -->
      <div class="widget-card">
        <div class="widget-title">📌 核心聚焦</div>
        <div class="feature-card">
          <p>每日 08:00 自动抓取全球一手信源，专挑「影响个人利益、能变现搞钱、能拿来省时间」的真动态，杜绝公关大词。</p>
          <a href="https://github.com/Felix8686/ai-daily-digest/issues" target="_blank">👉 提交内容反馈 &rarr;</a>
        </div>
      </div>

      <!-- 历史归档列表 -->
      <div class="widget-card">
        <div class="widget-title">📅 历史归档</div>
        <ul class="archive-nav-list">
          {% for item in archives %}
          <li>
            <a href="{{ item.url }}" class="archive-link {% if item.is_current %}active{% endif %}">
              <span>{{ item.date }}</span>
              <span class="archive-tag">{{ item.tag }}</span>
            </a>
          </li>
          {% endfor %}
        </ul>
      </div>
    </aside>
  </div>

  <!-- 页脚 -->
  <footer class="footer">
    <p>© {{ year }} 半调Felix · 基于云端自动化 + DeepSeek 全流程提炼 · 商业洞察与实操沉淀</p>
  </footer>

  <script>
    const CORRECT_PASS = "{{ site_password }}";
    const AUTH_KEY = "ai_digest_auth_token";
    const THEME_KEY = "ai_digest_theme";
    const FAV_KEY = "ai_digest_favorites";

    let activeModalNews = null;
    let isFilterFavOnly = false;

    // 1. 主题初始化与切换
    function initTheme() {
      const savedTheme = localStorage.getItem(THEME_KEY);
      const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
      if (savedTheme === "dark" || (!savedTheme && prefersDark)) {
        document.documentElement.classList.add("dark");
        document.getElementById("theme-icon").textContent = "☀️";
      } else {
        document.documentElement.classList.remove("dark");
        document.getElementById("theme-icon").textContent = "🌙";
      }
    }

    function toggleTheme() {
      const isDark = document.documentElement.classList.toggle("dark");
      localStorage.setItem(THEME_KEY, isDark ? "dark" : "light");
      document.getElementById("theme-icon").textContent = isDark ? "☀️" : "🌙";
    }

    // 2. 门禁校验
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

    // 3. 快速平滑滚动跳转
    function scrollToHeading(keyword) {
      if (isFilterFavOnly) {
        toggleFavoritesFilter(); // 恢复全部显示
      }
      const headings = document.querySelectorAll(".article-body h2");
      for (const h of headings) {
        if (h.textContent.includes(keyword)) {
          h.scrollIntoView({ behavior: "smooth", block: "start" });
          h.style.transition = "background-color 0.4s ease";
          const origBg = h.style.backgroundColor;
          h.style.backgroundColor = "var(--primary-subtle)";
          setTimeout(() => { h.style.backgroundColor = origBg; }, 1200);
          return;
        }
      }
    }

    // 4. 阅读进度条
    window.addEventListener("scroll", () => {
      const winScroll = document.body.scrollTop || document.documentElement.scrollTop;
      const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
      const scrolled = height > 0 ? (winScroll / height) * 100 : 0;
      document.getElementById("progress-bar").style.width = scrolled + "%";
    });

    // 5. 轻提示 Toast
    function showToast(msg, duration = 2400) {
      const toast = document.getElementById("toast-notify");
      toast.innerHTML = msg;
      toast.classList.add("show");
      setTimeout(() => {
        toast.classList.remove("show");
      }, duration);
    }

    // 6. 收藏机制 (Local Storage)
    function getFavorites() {
      try {
        return JSON.parse(localStorage.getItem(FAV_KEY) || "{}");
      } catch (e) {
        return {};
      }
    }

    function saveFavorites(favs) {
      localStorage.setItem(FAV_KEY, JSON.stringify(favs));
      updateFavUI();
    }

    function toggleFavorite(btn, newsId) {
      const favs = getFavorites();
      const card = document.querySelector(`.news-card[data-news-id="${newsId}"]`);
      if (!card) return;

      if (favs[newsId]) {
        delete favs[newsId];
        saveFavorites(favs);
        showToast("✕ 已取消收藏");
      } else {
        favs[newsId] = {
          id: newsId,
          title: card.getAttribute("data-title") || "",
          url: card.getAttribute("data-url") || "",
          source: card.getAttribute("data-source") || "",
          category: card.getAttribute("data-category") || "",
          summary: card.getAttribute("data-summary") || "",
          date: card.getAttribute("data-date") || "",
          favAt: Date.now()
        };
        saveFavorites(favs);
        showToast("⭐ 已加入我的收藏！");
      }
    }

    function updateFavUI() {
      const favs = getFavorites();
      const count = Object.keys(favs).length;
      const countEl = document.getElementById("fav-count");
      if (countEl) countEl.textContent = count;

      const cards = document.querySelectorAll(".news-card");
      cards.forEach(card => {
        const nid = card.getAttribute("data-news-id");
        const favBtn = card.querySelector(".fav-btn");
        if (favBtn) {
          if (favs[nid]) {
            favBtn.classList.add("is-fav");
            favBtn.querySelector(".star-icon").textContent = "★";
            favBtn.querySelector(".btn-label").textContent = "已收藏";
            card.classList.add("is-favorited");
          } else {
            favBtn.classList.remove("is-fav");
            favBtn.querySelector(".star-icon").textContent = "☆";
            favBtn.querySelector(".btn-label").textContent = "收藏";
            card.classList.remove("is-favorited");
          }
        }
      });

      // 如果当前正处于筛选模式，刷新展示状态
      if (isFilterFavOnly) {
        applyFavFilter();
      }
    }

    function toggleFavoritesFilter() {
      isFilterFavOnly = !isFilterFavOnly;
      const btn = document.getElementById("filter-fav-btn");
      if (btn) btn.classList.toggle("active", isFilterFavOnly);
      applyFavFilter();
    }

    function applyFavFilter() {
      const favs = getFavorites();
      const favCount = Object.keys(favs).length;
      const emptyBanner = document.getElementById("fav-empty-banner");
      const headings = document.querySelectorAll(".article-body h2");
      const cards = document.querySelectorAll(".news-card");

      if (isFilterFavOnly) {
        if (favCount === 0) {
          emptyBanner.style.display = "block";
          headings.forEach(h => h.style.display = "none");
          cards.forEach(c => c.style.display = "none");
        } else {
          emptyBanner.style.display = "none";
          // 隐藏非收藏卡片
          cards.forEach(card => {
            const isFav = card.classList.contains("is-favorited");
            card.style.display = isFav ? "block" : "none";
          });
          // 检查每个 h2 下面是否有可见卡片，没有则隐藏该板块标题
          headings.forEach(h2 => {
            let hasVisible = false;
            let sibling = h2.nextElementSibling;
            while (sibling && sibling.tagName !== "H2") {
              if (sibling.classList.contains("news-card") && sibling.style.display !== "none") {
                hasVisible = true;
                break;
              }
              sibling = sibling.nextElementSibling;
            }
            h2.style.display = hasVisible ? "flex" : "none";
          });
        }
        showToast("已切换至【⭐ 仅看收藏】");
      } else {
        emptyBanner.style.display = "none";
        headings.forEach(h => h.style.display = "flex");
        cards.forEach(c => c.style.display = "block");
      }
    }

    // 7. 分享与派发 Modal
    function openShareModal(newsId) {
      const card = document.querySelector(`.news-card[data-news-id="${newsId}"]`);
      if (!card) return;

      activeModalNews = {
        id: newsId,
        title: card.getAttribute("data-title") || "",
        url: card.getAttribute("data-url") || "",
        source: card.getAttribute("data-source") || "",
        category: card.getAttribute("data-category") || "",
        summary: card.getAttribute("data-summary") || "",
        date: card.getAttribute("data-date") || ""
      };

      document.getElementById("modal-target-title").textContent = activeModalNews.title;

      // 构造 Telegram 直发链接
      const promptText = `【AI 情报深度调研任务】\\n📌 标题：${activeModalNews.title}\\n🔗 链接：${activeModalNews.url}\\n🏷️ 板块：${activeModalNews.category} (来源: ${activeModalNews.source})\\n💡 核心事实：${activeModalNews.summary}\\n\\n👉 请 Hermes/Agent 结合以上情报展开调研：其技术底层原理、商业变现路径及可复用的实践打法。`;
      const tgUrl = `https://t.me/share/url?url=${encodeURIComponent(activeModalNews.url)}&text=${encodeURIComponent(promptText)}`;
      document.getElementById("btn-share-tg").href = tgUrl;

      document.getElementById("share-modal").style.display = "flex";
    }

    function closeShareModal() {
      document.getElementById("share-modal").style.display = "none";
      activeModalNews = null;
    }

    function copyCodexCommand() {
      if (!activeModalNews) return;
      const cmd = `codex "深度调研与落地评估：${activeModalNews.title} (${activeModalNews.url})，分析其商业变现模式与技术落地可行性"`;
      navigator.clipboard.writeText(cmd).then(() => {
        showToast("✓ 已复制 Codex 终端指令！");
        closeShareModal();
      }).catch(() => {
        showToast("复制失败，请手动长按复制");
      });
    }

    function copyFullPrompt() {
      if (!activeModalNews) return;
      const prompt = `请针对以下 AI 前沿动态开展深度调研与评估：\\n【标题】${activeModalNews.title}\\n【链接】${activeModalNews.url}\\n【来源】${activeModalNews.source} (${activeModalNews.category})\\n【核心事实】\\n${activeModalNews.summary}\\n\\n【调研重点要求】\\n1. 剖析底层核心技术与技术路径；\\n2. 分析其商业变现逻辑与同类竞品差异；\\n3. 给出适合一人公司或小团队落地的具体行动建议。`;
      navigator.clipboard.writeText(prompt).then(() => {
        showToast("✓ 已复制深度调研 Prompt！");
        closeShareModal();
      }).catch(() => {
        showToast("复制失败，请手动长按复制");
      });
    }

    function copyOriginalLink() {
      if (!activeModalNews) return;
      navigator.clipboard.writeText(activeModalNews.url).then(() => {
        showToast("✓ 已复制原始链接！");
        closeShareModal();
      }).catch(() => {
        showToast("复制失败，请手动长按复制");
      });
    }

    // 页面加载完成初始化
    document.addEventListener("DOMContentLoaded", () => {
      initTheme();
      checkAuth();
      updateFavUI();
    });

    // 立即执行以防 DOMContentLoaded 已过
    initTheme();
    checkAuth();
    updateFavUI();
  </script>
</body>
</html>
"""

def enhance_html_with_news_cards(raw_html: str, date_str: str) -> str:
    """使用 BeautifulSoup 结构化重构新闻正文，为每条动态包装现代交互卡片与【收藏/派发】底栏"""
    soup = BeautifulSoup(raw_html, "html.parser")

    for h2 in soup.find_all("h2"):
        sec_name = h2.get_text(strip=True)
        cat_key = "general"
        if "异动" in sec_name:
            cat_key = "trend"
        elif "变现" in sec_name:
            cat_key = "monetize"
        elif "平替" in sec_name or "神器" in sec_name:
            cat_key = "tool"
        elif "风控" in sec_name or "选题" in sec_name:
            cat_key = "creator"
        elif "排雷" in sec_name or "避坑" in sec_name:
            cat_key = "alert"

        h2["data-category"] = cat_key

        curr = h2.find_next_sibling()
        while curr and curr.name != "h2":
            next_sib = curr.find_next_sibling()
            if curr.name == "p" and curr.find("strong") and curr.find("strong").find("a"):
                # 收集属于当前新闻项的所有兄弟段落，直到下一个新闻项、hr 或 h2
                card_nodes = [curr]
                scan = next_sib
                while scan and scan.name != "h2" and scan.name != "hr":
                    if scan.name == "p" and scan.find("strong") and scan.find("strong").find("a"):
                        break
                    card_nodes.append(scan)
                    scan = scan.find_next_sibling()

                # 提取标题与原始 URL
                title_a = curr.find("strong").find("a")
                title_text = title_a.get_text(strip=True) if title_a else "未命名动态"
                link_url = title_a["href"] if title_a and title_a.has_attr("href") else ""

                # 提取信源
                p_text = curr.get_text()
                source_text = ""
                if "来源:" in p_text or "来源：" in p_text:
                    parts = p_text.split("来源:") if "来源:" in p_text else p_text.split("来源：")
                    source_text = parts[-1].replace(")", "").replace("）", "").strip()

                # 提取摘要正文
                summary_paras = [n.get_text(strip=True) for n in card_nodes[1:] if n.name == "p"]
                summary_text = " ".join(summary_paras)

                # 生成稳定唯一的 News ID
                hash_input = f"{date_str}_{title_text}"
                news_id = "nid_" + hashlib.md5(hash_input.encode("utf-8")).hexdigest()[:10]

                # 构造包含完整语义与交互能力的 news-card
                card_div = soup.new_tag("div")
                card_div["class"] = ["news-card", f"cat-{cat_key}"]
                card_div["data-news-id"] = news_id
                card_div["data-category"] = sec_name
                card_div["data-title"] = title_text
                card_div["data-url"] = link_url
                card_div["data-source"] = source_text
                card_div["data-summary"] = summary_text[:350]
                card_div["data-date"] = date_str

                # 卡片内容主体
                content_div = soup.new_tag("div")
                content_div["class"] = ["news-card-body"]
                for n in card_nodes:
                    content_div.append(n.extract())
                card_div.append(content_div)

                # 底部操作栏（收藏 + 派发）
                cat_badge_label = sec_name.split("：")[0].split(":")[0].strip()
                action_html = f"""
                <div class="news-card-actions">
                    <div class="action-left-info">
                        <span class="card-cat-badge">{cat_badge_label}</span>
                    </div>
                    <div class="action-right-btns">
                        <button type="button" class="item-action-btn fav-btn" onclick="toggleFavorite(this, '{news_id}')" title="收藏至本地">
                            <span class="star-icon">☆</span> <span class="btn-label">收藏</span>
                        </button>
                        <button type="button" class="item-action-btn share-btn" onclick="openShareModal('{news_id}')" title="派发至 Hermes/Codex">
                            <span>🔗</span> <span class="btn-label">分享 / 派发</span>
                        </button>
                    </div>
                </div>
                """
                card_div.append(BeautifulSoup(action_html, "html.parser"))

                if scan:
                    scan.insert_before(card_div)
                else:
                    h2.parent.append(card_div)

                curr = scan
                continue
            curr = next_sib

    # 清理多余的分隔线 <hr />
    for hr in soup.find_all("hr"):
        prev = hr.find_previous_sibling()
        nxt = hr.find_next_sibling()
        if (prev and "news-card" in prev.get("class", [])) or (nxt and "news-card" in nxt.get("class", [])):
            hr.decompose()

    return str(soup)

def build_static_site(project_dir: Path, current_markdown: str, today_str: str, cname: str = "news.felix8686.top", site_password: str = "felix8686") -> Path:
    """生成包含 index.html、robots.txt、现代化界面与历史归档的静态站点目录 dist/"""
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
    today_body_raw_html = markdown.markdown(current_markdown, extensions=["extra", "nl2br", "sane_lists"])
    today_body_html = enhance_html_with_news_cards(today_body_raw_html, today_str)

    tmpl = Template(WEB_TEMPLATE)
    index_html = tmpl.render(
        site_title="半调Felix 的 AI 提效与商业周刊",
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
        raw_html_text = markdown.markdown(md_text, extensions=["extra", "nl2br", "sane_lists"])
        enhanced_html = enhance_html_with_news_cards(raw_html_text, date_part)
        page_html = tmpl.render(
            site_title="半调Felix 的 AI 提效与商业周刊",
            page_title=f"{date_part} 归档",
            date_str=date_part,
            body_html=enhanced_html,
            archives=archives_meta,
            year=dt.date.today().year,
            site_password=site_password
        )
        (dist_archive_dir / f"{date_part}.html").write_text(page_html, encoding="utf-8")

    # 5. 写入自定义域名 CNAME
    if cname:
        (dist_dir / "CNAME").write_text(cname.strip(), encoding="utf-8")
        print(f"🌐 已生成 CNAME 绑定: {cname}")

    print(f"🚀 现代化静态网页站点生成完毕！输出目录: {dist_dir} (已集成收藏夹、派发弹窗、主题切换与密码门禁)")
    return dist_dir

if __name__ == "__main__":
    p_dir = Path(__file__).parent
    archive_dir = p_dir / "archive"
    archive_files = sorted(archive_dir.glob("digest-*.md"), reverse=True)
    if archive_files:
        latest_file = archive_files[0]
        date_part = latest_file.stem.replace("digest-", "")
        parts = date_part.split("-")
        date_str = f"{parts[0]}年{parts[1]}月{parts[2]}日" if len(parts) == 3 else date_part
        content = latest_file.read_text(encoding="utf-8")
        build_static_site(p_dir, content, date_str, "news.felix8686.top", "felix8686")
    else:
        print("⚠️ 未找到历史归档")
