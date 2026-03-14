#!/usr/bin/env python3

import html
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "content/top3/index.json"
OUTPUT_DIR = ROOT / "docs/posts"
GITHUB_BASE = "https://github.com/jxcwp/hot-ai-repo/blob/main/"


def clean_markdown(markdown: str) -> str:
    lines = markdown.replace("\r", "").split("\n")
    out = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if stripped in {"## 标签", "### 一键收藏标签", "## 一键收藏标签"}:
            i += 1
            while i < len(lines):
                next_line = lines[i].strip()
                if next_line.startswith("#") or next_line == "---":
                    break
                i += 1
            continue
        out.append(line)
        i += 1
    return "\n".join(out)


def render_inline(text: str) -> str:
    escaped = html.escape(text)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", escaped)
    escaped = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', escaped)
    return escaped


def slugify(text: str) -> str:
    slug = re.sub(r"[^\w\u4e00-\u9fff\- ]+", "", text).strip().lower()
    slug = re.sub(r"\s+", "-", slug)
    return slug or "section"


def markdown_to_html(markdown: str) -> tuple[str, list[dict]]:
    lines = markdown.replace("\r", "").split("\n")
    out = []
    toc = []
    anchor_counts = {}
    paragraph = []
    in_code = False
    code_lines = []
    list_type = None

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            out.append(f"<p>{render_inline(' '.join(paragraph))}</p>")
            paragraph = []

    def flush_list() -> None:
        nonlocal list_type
        if list_type:
            out.append(f"</{list_type}>")
            list_type = None

    def flush_code() -> None:
        nonlocal in_code, code_lines
        if in_code:
            out.append("<pre><code>" + html.escape("\n".join(code_lines)) + "</code></pre>")
            in_code = False
            code_lines = []

    for line in lines:
        if line.startswith("```"):
            flush_paragraph()
            flush_list()
            if in_code:
                flush_code()
            else:
                in_code = True
            continue

        if in_code:
            code_lines.append(line)
            continue

        if not line.strip():
            flush_paragraph()
            flush_list()
            continue

        heading = re.match(r"^(#{1,4})\s+(.*)$", line)
        if heading:
            flush_paragraph()
            flush_list()
            level = len(heading.group(1))
            title = heading.group(2)
            anchor = slugify(title)
            count = anchor_counts.get(anchor, 0)
            anchor_counts[anchor] = count + 1
            if count:
                anchor = f"{anchor}-{count + 1}"
            out.append(f'<h{level} id="{anchor}">{render_inline(title)}</h{level}>')
            if level in (2, 3):
                toc.append({"level": level, "title": title, "anchor": anchor})
            continue

        if re.match(r"^---+$", line.strip()):
            flush_paragraph()
            flush_list()
            out.append("<hr>")
            continue

        ul = re.match(r"^[-*]\s+(.*)$", line)
        if ul:
            flush_paragraph()
            if list_type != "ul":
                flush_list()
                out.append("<ul>")
                list_type = "ul"
            out.append(f"<li>{render_inline(ul.group(1))}</li>")
            continue

        ol = re.match(r"^\d+\.\s+(.*)$", line)
        if ol:
            flush_paragraph()
            if list_type != "ol":
                flush_list()
                out.append("<ol>")
                list_type = "ol"
            out.append(f"<li>{render_inline(ol.group(1))}</li>")
            continue

        paragraph.append(line.strip())

    flush_paragraph()
    flush_list()
    flush_code()
    return "\n".join(out), toc


def build_toc_html(toc: list[dict]) -> str:
    if not toc:
        return ""
    items = []
    for item in toc:
        cls = "toc-sub" if item["level"] == 3 else ""
        items.append(f'<a class="{cls}" href="#{html.escape(item["anchor"])}">{html.escape(item["title"])}' + '</a>')
    return '<aside class="toc"><div class="toc-title">目录导航</div><nav>' + ''.join(items) + '</nav></aside>'


def build_page(entry: dict, prev_entry: dict | None, next_entry: dict | None) -> str:
    title = entry.get("title", "AI Open Source Radar")
    date = entry.get("date", "未知日期")
    article_path = ROOT / entry.get("wechat_path", "")
    markdown = article_path.read_text(encoding="utf-8") if article_path.exists() else "# 文章不存在\n"
    markdown = clean_markdown(markdown)
    body_html, toc = markdown_to_html(markdown)
    projects = " / ".join(project.get("name", "") for project in entry.get("projects", []) if project.get("name"))
    github_url = GITHUB_BASE + entry.get("wechat_path", "")
    prev_link = f"../posts/{prev_entry.get('slug')}.html" if prev_entry and prev_entry.get("slug") else ""
    next_link = f"../posts/{next_entry.get('slug')}.html" if next_entry and next_entry.get("slug") else ""
    prev_title = prev_entry.get("title", "") if prev_entry else ""
    next_title = next_entry.get("title", "") if next_entry else ""

    return f"""<!doctype html>
<html lang=\"zh-CN\">
  <head>
    <meta charset=\"utf-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
    <title>{html.escape(title)} | AI Open Source Radar</title>
    <meta name=\"description\" content=\"{html.escape(title)} - AI 开源项目中文解读、对比、上手教程、商用建议与风险提示。\">
    <style>
      :root {{ --bg:#f6f3eb; --panel:rgba(255,251,244,.94); --ink:#1f2320; --muted:#5f665f; --line:rgba(31,35,32,.12); --brand:#0d7a5f; --shadow:0 24px 60px rgba(31,35,32,.12); }}
      * {{ box-sizing:border-box; }}
      body {{ margin:0; font-family:"Source Han Sans SC","Noto Sans SC",sans-serif; color:var(--ink); background:radial-gradient(circle at top left, rgba(202,93,42,.18), transparent 28%), radial-gradient(circle at top right, rgba(13,122,95,.16), transparent 30%), linear-gradient(180deg,#f9f5ee 0%,var(--bg) 100%); }}
      a {{ color:inherit; }}
      .wrap {{ max-width:980px; margin:0 auto; padding:28px 20px 64px; }}
      .topbar {{ display:flex; align-items:center; justify-content:space-between; gap:16px; margin-bottom:18px; }}
      .brand {{ font-size:14px; font-weight:800; letter-spacing:.08em; text-transform:uppercase; color:var(--muted); }}
      .top-actions {{ display:flex; flex-wrap:wrap; gap:10px; }}
      .top-actions a {{ padding:10px 12px; border-radius:999px; border:1px solid var(--line); background:rgba(255,255,255,.58); text-decoration:none; font-size:14px; font-weight:700; }}
      .hero,.article,.footer {{ border:1px solid var(--line); border-radius:28px; background:var(--panel); box-shadow:var(--shadow); }}
      .hero,.footer {{ padding:28px; }}
      .article {{ margin-top:20px; padding:34px; }}
      .eyebrow {{ display:inline-block; margin-bottom:14px; padding:8px 12px; border-radius:999px; background:rgba(13,122,95,.1); color:var(--brand); font-size:13px; font-weight:700; }}
      h1 {{ margin:0; font-size:clamp(32px,5vw,52px); line-height:1.08; }}
      .meta,.lead,.muted {{ color:var(--muted); line-height:1.8; }}
      .lead {{ margin-top:16px; font-size:18px; }}
      .actions {{ display:flex; flex-wrap:wrap; gap:12px; margin-top:22px; }}
      .project-tags {{ display:flex; flex-wrap:wrap; gap:10px; margin-top:18px; }}
      .project-tags span {{ padding:10px 14px; border-radius:999px; border:1px solid var(--line); background:rgba(255,255,255,.68); font-weight:700; }}
      .button {{ display:inline-flex; align-items:center; justify-content:center; padding:12px 16px; border-radius:14px; text-decoration:none; font-weight:700; }}
      .button.primary {{ background:var(--ink); color:#fff; }}
      .button.secondary {{ border:1px solid var(--line); background:rgba(255,255,255,.6); }}
      .article-content h1,.article-content h2,.article-content h3,.article-content h4 {{ margin:32px 0 14px; line-height:1.3; }}
      .article-content h1 {{ font-size:34px; }} .article-content h2 {{ font-size:28px; }} .article-content h3 {{ font-size:22px; }} .article-content h4 {{ font-size:18px; }}
      .article-content p,.article-content li {{ line-height:1.9; font-size:17px; }}
      .article-content ul,.article-content ol {{ padding-left:22px; }}
      .article-content hr {{ border:0; border-top:1px solid var(--line); margin:28px 0; }}
      .article-content code {{ padding:2px 6px; border-radius:8px; background:rgba(31,35,32,.06); font-family:"JetBrains Mono","Fira Code",monospace; font-size:.92em; }}
      .article-content pre {{ overflow-x:auto; padding:16px; border-radius:18px; background:#171a18; color:#f7f3eb; }}
      .article-content pre code {{ padding:0; background:transparent; color:inherit; }}
      .article-content a {{ color:var(--brand); text-decoration:none; border-bottom:1px solid rgba(13,122,95,.22); }}
      .article-content a:hover {{ border-bottom-color: rgba(13,122,95,.5); }}
      .content-grid {{ display:grid; grid-template-columns:minmax(0, 1fr) 240px; gap:22px; align-items:start; }}
      .toc {{ position:sticky; top:20px; padding:18px; border-radius:22px; border:1px solid var(--line); background:rgba(255,255,255,.64); }}
      .toc-title {{ margin-bottom:12px; font-size:14px; font-weight:800; color:var(--muted); letter-spacing:.06em; text-transform:uppercase; }}
      .toc nav {{ display:grid; gap:10px; }}
      .toc a {{ color:var(--ink); text-decoration:none; border:0; line-height:1.5; }}
      .toc a.toc-sub {{ padding-left:14px; color:var(--muted); font-size:14px; }}
      .pager {{ display:grid; grid-template-columns:1fr 1fr; gap:14px; margin-top:24px; }}
      .pager a {{ display:block; padding:18px; border-radius:20px; border:1px solid var(--line); background:rgba(255,255,255,.62); text-decoration:none; }}
      .pager small {{ display:block; color:var(--muted); margin-bottom:6px; font-size:13px; font-weight:700; }}
      .pager strong {{ display:block; line-height:1.5; }}
      .footer {{ margin-top:20px; background:linear-gradient(135deg, rgba(13,122,95,.08), rgba(202,93,42,.08)); }}
      @media (max-width:900px) {{ .content-grid {{ grid-template-columns:1fr; }} .toc {{ position:static; order:-1; }} }}
      @media (max-width:720px) {{ .topbar {{ flex-direction:column; align-items:flex-start; }} .hero,.article,.footer {{ padding:22px; }} .article-content p,.article-content li {{ font-size:16px; }} .pager {{ grid-template-columns:1fr; }} }}
    </style>
  </head>
  <body>
    <main class=\"wrap\">
      <div class=\"topbar\">
        <div class=\"brand\">AI Open Source Radar</div>
        <div class=\"top-actions\">
          <a href=\"../index.html\">首页</a>
          <a href=\"../content/top3/README.md\">归档</a>
          <a href=\"https://github.com/jxcwp/hot-ai-repo\" target=\"_blank\" rel=\"noreferrer\">GitHub</a>
        </div>
      </div>
      <section class=\"hero\">
        <div class=\"eyebrow\">AI Open Source Radar</div>
        <p class=\"meta\">发布于 {html.escape(date)}</p>
        <h1>{html.escape(title)}</h1>
        <p class=\"lead\">入选项目：{html.escape(projects or '今日 AI 开源项目精选')}</p>
        <div class=\"project-tags\">{''.join(f'<span>{html.escape(name)}</span>' for name in projects.split(' / ') if name)}</div>
        <div class=\"actions\">
          <a class=\"button secondary\" href=\"../index.html\">返回首页</a>
          <a class=\"button secondary\" href=\"../content/top3/README.md\">查看归档</a>
          <a class=\"button primary\" href=\"../{html.escape(entry.get('wechat_path', ''))}\">查看原文</a>
          <a class=\"button secondary\" href=\"{html.escape(github_url)}\" target=\"_blank\" rel=\"noreferrer\">GitHub 文件</a>
        </div>
      </section>
      <article class=\"article\"><div class=\"content-grid\"><div class=\"article-content\">{body_html}{build_pager_html(prev_link, prev_title, next_link, next_title)}</div>{build_toc_html(toc)}</div></article>
      <section class=\"footer\"><p class=\"muted\">如果你也在关注 AI、Agent 和最新开源趋势，欢迎关注微信公众号：碳基生物观察局。我会持续分享值得跟踪的 AI 项目、产品观察和实战解读。</p></section>
    </main>
  </body>
</html>
"""


def main() -> None:
    data = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    entries = data.get("entries", [])
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for idx, entry in enumerate(entries):
        slug = entry.get("slug")
        if not slug:
            continue
        output_file = OUTPUT_DIR / f"{slug}.html"
        prev_entry = entries[idx - 1] if idx > 0 else None
        next_entry = entries[idx + 1] if idx + 1 < len(entries) else None
        output_file.write_text(build_page(entry, prev_entry, next_entry), encoding="utf-8")


def build_pager_html(prev_link: str, prev_title: str, next_link: str, next_title: str) -> str:
    items = []
    if prev_link:
        items.append(
            f'<a href="{html.escape(prev_link)}"><small>上一篇</small><strong>{html.escape(prev_title)}</strong></a>'
        )
    else:
        items.append('<div></div>')
    if next_link:
        items.append(
            f'<a href="{html.escape(next_link)}"><small>下一篇</small><strong>{html.escape(next_title)}</strong></a>'
        )
    else:
        items.append('<div></div>')
    return '<div class="pager">' + ''.join(items) + '</div>'


if __name__ == "__main__":
    main()
