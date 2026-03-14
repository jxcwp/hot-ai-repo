#!/usr/bin/env python3

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "content/top3/index.json"
README_PATH = ROOT / "content/top3/README.md"
GITHUB_BASE = "https://github.com/jxcwp/hot-ai-repo/blob/main/"
PAGES_BASE = "https://jxcwp.github.io/hot-ai-repo/"


def main() -> None:
    data = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    entries = data.get("entries", [])

    lines = [
        "# Top 3 Archive",
        "",
        "这里收录每日 AI 开源项目 Top 3 推文归档。",
        "",
        "结构说明：",
        "- `YYYY-MM-DD/标题.json`：结构化 JSON 结果",
        "- `YYYY-MM-DD/标题.md`：常规 Markdown 版本",
        "- `YYYY-MM-DD/标题-wechat.md`：公众号风格版本",
        "- `index.json`：机器可读归档索引",
        "",
        "## Archive",
        "",
    ]

    if not entries:
        lines.append("- 暂无归档")
    else:
        for entry in entries:
            date = entry.get("date", "未知日期")
            title = entry.get("title", "未命名归档")
            path = entry.get("wechat_path", "")
            slug = entry.get("slug", "")
            github_url = GITHUB_BASE + path if path else ""
            pages_url = PAGES_BASE + f"posts/{slug}.html" if slug else (PAGES_BASE + path if path else "")
            project_names = [project.get("name", "") for project in entry.get("projects", []) if project.get("name")]
            summary = " / ".join(project_names)
            link_part = title
            if github_url and pages_url:
                link_part = f"{title} ([GitHub]({github_url}) | [Pages]({pages_url}))"
            elif github_url:
                link_part = f"{title} ([GitHub]({github_url}))"
            elif pages_url:
                link_part = f"{title} ([Pages]({pages_url}))"
            if summary:
                lines.append(f"- `{date}` {link_part} - {summary}")
            else:
                lines.append(f"- `{date}` {link_part}")

    README_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
