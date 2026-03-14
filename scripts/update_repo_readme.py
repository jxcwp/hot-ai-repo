#!/usr/bin/env python3

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "content/top3/index.json"
README_ZH = ROOT / "README.md"
README_EN = ROOT / "README.en.md"


def load_entries() -> list[dict]:
    data = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    return data.get("entries", [])


def render_latest(entries: list[dict]) -> tuple[str, str, str, str]:
    latest = entries[-1] if entries else {}
    title = latest.get("title", "今天最值得关注的 3 个 AI 开源项目")
    date = latest.get("date", "YYYY-MM-DD")
    path = latest.get("wechat_path", "content/top3/README.md")
    projects = " / ".join(project.get("name", "") for project in latest.get("projects", []) if project.get("name"))
    return title, date, path, projects


def render_updates(entries: list[dict], limit: int = 5) -> tuple[list[str], list[str]]:
    selected = list(reversed(entries[-limit:]))
    zh_lines = []
    en_lines = []
    for entry in selected:
        date = entry.get("date", "YYYY-MM-DD")
        title = entry.get("title", "Untitled")
        path = entry.get("wechat_path", "content/top3/README.md")
        zh_lines.append(f"- [`{date} | {title}`]({path})")
        en_lines.append(f"- [`{date} | {title}`]({path})")
    return zh_lines, en_lines


def update_zh(entries: list[dict]) -> None:
    title, date, path, projects = render_latest(entries)
    latest_updates, _ = render_updates(entries)
    content = f"""# AI Open Source Radar

[![GitHub Repo stars](https://img.shields.io/github/stars/jxcwp/hot-ai-repo?style=flat-square)](https://github.com/jxcwp/hot-ai-repo/stargazers)
[![GitHub last commit](https://img.shields.io/github/last-commit/jxcwp/hot-ai-repo?style=flat-square)](https://github.com/jxcwp/hot-ai-repo/commits/main)
[![Daily Top 3](https://img.shields.io/badge/daily-top%203-blue?style=flat-square)](content/top3/README.md)
[![WeChat](https://img.shields.io/badge/WeChat-%E7%A2%B3%E5%9F%BA%E7%94%9F%E7%89%A9%E8%A7%82%E5%AF%9F%E5%B1%80-07C160?style=flat-square)](#follow)
[![Language](https://img.shields.io/badge/language-%E4%B8%AD%E6%96%87%E4%B8%BA%E4%B8%BB-orange?style=flat-square)](README.en.md)

每天筛选最值得关注的 3 个 AI 开源项目，提供中文解读、同类对比、上手教程和商业视角。

英文版说明见：[`README.en.md`](README.en.md)

这是一个面向中文开发者、产品经理和 AI 创业者的 GitHub 内容仓库：不只看 Star，更看最近的增长势能、技术价值和落地机会。

如果你也在追踪 AI、Agent、RAG、Coding、Voice、Video 等方向，欢迎先 `Star` 这个仓库，再去看今天的 Top 3。

## 今日 Top 3

- 今日更新：[`{title}`]({path})
- 日期：`{date}`
- 入选项目：`{projects}`
- 历史归档：[`content/top3/README.md`](content/top3/README.md)
- GitHub Pages：[`docs/index.html`](docs/index.html)

## 这个仓库的价值

- 中文解读：不是搬运 README，而是解释项目到底解决什么问题
- 同类对比：帮你判断它和现有方案相比值不值得继续跟踪
- 上手教程：降低第一次试用门槛，节省调研时间
- 商业视角：补充产品化、服务化和副业方向的思考
- 每日筛选：优先关注最近真的在升温的项目，而不是只看历史明星仓库

## 你能获得什么

- 每天 1 篇 GitHub AI 开源 Top 3 精选
- 每篇 3 个项目的中文拆解
- 为什么现在值得关注
- 和同类项目的关键差异
- 快速上手建议
- 商业建议和风险提示

## 最新更新

{chr(10).join(latest_updates)}

## 重点关注方向

- Agent
- Coding
- RAG
- Voice
- Video
- AI Infra

后续会继续把这些方向整理成专题归档。

## 仓库结构

- [`content/top3/`](content/top3/)：每日推文和归档
- [`content/top3/index.json`](content/top3/index.json)：机器可读索引
- [`content/top3/README.md`](content/top3/README.md)：人工浏览索引
- [`docs/index.html`](docs/index.html)：GitHub Pages 首页
- [`.github/workflows/deploy-pages.yml`](.github/workflows/deploy-pages.yml)：GitHub Pages 自动部署 workflow
- [`scripts/update_top3_archive.py`](scripts/update_top3_archive.py)：根据 `index.json` 自动刷新归档页
- [`scripts/update_repo_readme.py`](scripts/update_repo_readme.py)：根据 `index.json` 自动刷新 README

## 如何使用

- 每天先看 `今日 Top 3`
- 想系统跟踪趋势时，看归档页
- 想做产品、内容或副业时，重点看每篇里的商用建议

## 关注

如果你也在关注 AI、Agent 和最新开源趋势，欢迎 `Star` 本仓库，并关注我的微信公众号：`碳基生物观察局`。

我会持续分享：

- 值得跟踪的 AI 开源项目
- 产品观察
- 实战解读
- 趋势判断
"""
    README_ZH.write_text(content + "\n", encoding="utf-8")


def update_en(entries: list[dict]) -> None:
    title, date, path, projects = render_latest(entries)
    _, latest_updates = render_updates(entries)
    content = f"""# AI Open Source Radar

[![GitHub Repo stars](https://img.shields.io/github/stars/jxcwp/hot-ai-repo?style=flat-square)](https://github.com/jxcwp/hot-ai-repo/stargazers)
[![GitHub last commit](https://img.shields.io/github/last-commit/jxcwp/hot-ai-repo?style=flat-square)](https://github.com/jxcwp/hot-ai-repo/commits/main)
[![Daily Top 3](https://img.shields.io/badge/daily-top%203-blue?style=flat-square)](content/top3/README.md)
[![WeChat](https://img.shields.io/badge/WeChat-%E7%A2%B3%E5%9F%BA%E7%94%9F%E7%89%A9%E8%A7%82%E5%AF%9F%E5%B1%80-07C160?style=flat-square)](#follow)
[![Language](https://img.shields.io/badge/language-English-blue?style=flat-square)](README.md)

Daily top 3 AI open source picks with Chinese analysis, peer comparison, quickstart notes, and product-minded insights.

Chinese version: [`README.md`](README.md)

This repo is built for developers, product teams, and AI builders who want signal instead of noise. It focuses on what is rising now on GitHub, not just old famous repositories.

If you care about AI, agents, RAG, coding, voice, and video, `Star` this repo first and start with today's Top 3.

## Today Top 3

- Latest: [`{title}`]({path})
- Date: `{date}`
- Picks: `{projects}`
- Archive: [`content/top3/README.md`](content/top3/README.md)
- GitHub Pages: [`docs/index.html`](docs/index.html)

## Why This Repo

- Chinese analysis instead of raw README translation
- Peer comparison so you can judge what is worth tracking
- Quickstart guidance to lower the first-use barrier
- Business-minded notes for builders, creators, and founders
- Daily curation based on recent momentum, not just historical fame

## What You Can Get

- One daily GitHub AI Top 3 post
- Chinese breakdowns for 3 selected projects
- Why they matter now
- What makes them different from similar tools
- Quickstart notes
- Business advice and risk notes

## Latest Updates

{chr(10).join(latest_updates)}

## Focus Areas

- Agent
- Coding
- RAG
- Voice
- Video
- AI Infra

More thematic collections are coming.

## Repo Structure

- [`content/top3/`](content/top3/): daily posts and archive
- [`content/top3/index.json`](content/top3/index.json): machine-readable index
- [`content/top3/README.md`](content/top3/README.md): human-readable archive
- [`docs/index.html`](docs/index.html): GitHub Pages homepage
- [`.github/workflows/deploy-pages.yml`](.github/workflows/deploy-pages.yml): GitHub Pages deployment workflow
- [`scripts/update_top3_archive.py`](scripts/update_top3_archive.py): archive updater
- [`scripts/update_repo_readme.py`](scripts/update_repo_readme.py): README updater

## How To Use

- Start with `Today Top 3`
- Use the archive to track trends over time
- Read the business notes if you are building products or content

## Follow

If you want more AI open source tracking, product observations, and practical breakdowns, please `Star` this repo and follow my WeChat public account: `碳基生物观察局`.

I will keep sharing:

- high-signal AI open source projects
- product observations
- practical breakdowns
- trend analysis
"""
    README_EN.write_text(content + "\n", encoding="utf-8")


def main() -> None:
    entries = load_entries()
    update_zh(entries)
    update_en(entries)


if __name__ == "__main__":
    main()
