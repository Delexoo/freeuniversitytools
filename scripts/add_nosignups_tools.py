"""Import tools from nosignups.net (FckSignups tools.json) into student.html."""
from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
HTML_PATH = ROOT / "data" / "student-directory.html"
NOSIGNUPS_PATH = ROOT / "data" / "nosignups-tools.json"

SECTION_RE = re.compile(
    r'(<section class="tool-category"[^>]*data-category="([^"]+)"[^>]*>.*?<div class="category-tools">)(.*?)(</div>\s*</section>)',
    re.DOTALL,
)

# Map nosignups categories -> our category slugs
CAT_MAP = {
    "productivity": "productivity",
    "design": "design",
    "development": "programming",
    "writing": "writing",
    "privacy": "privacy-tools",
    "utilities": "utilities",
    "data": "data-tools",
    "media": "video",
    "education": "study",
    "lists": "free-stuff",
}

# Keyword overrides for better placement
KEYWORD_CAT = [
    (["whiteboard", "diagram", "flowchart", "excalidraw", "draw.io", "mermaid"], "diagrams"),
    (["pdf"], "pdf"),
    (["markdown", "notepad", "notes"], "notepad"),
    (["regex"], "regex"),
    (["spreadsheet", "sheet"], "spreadsheets"),
    (["resume", "cv"], "resume"),
    (["video", "capcut", "editor"], "video"),
    (["audio", "music", "midi", "daw"], "audio"),
    (["paint", "pixel", "svg", "sprite", "draw"], "drawing"),
    (["vpn", "tor", "privacy.sexy", "encode", "hash", "cyberchef"], "security"),
    (["api", "postman", "hoppscotch"], "api-clients"),
    (["cad", "3d"], "3d"),
    (["file", "transfer", "share", "pairdrop", "localsend"], "file-sharing"),
    (["llm", "ai", "chat", "webllm"], "ai"),
]


def norm_url(url: str) -> str:
    p = urlparse(url.strip().rstrip("/"))
    host = (p.netloc or "").lower().replace("www.", "")
    path = p.path.rstrip("/")
    return f"{host}{path}".lower()


def domain_of(url: str) -> str:
    try:
        return urlparse(url).netloc.replace("www.", "")
    except Exception:
        return ""


def pick_category(tool: dict) -> str:
    blob = " ".join(
        [
            tool.get("name", ""),
            tool.get("description", ""),
            " ".join(tool.get("tags") or []),
            tool.get("id", ""),
            tool.get("url", ""),
        ]
    ).lower()
    for needles, slug in KEYWORD_CAT:
        if any(n in blob for n in needles):
            return slug
    return CAT_MAP.get(tool.get("category", ""), "utilities")


def link_html(url: str, name: str, pricing: str = "free") -> str:
    domain = domain_of(url)
    icon = f"https://icon.horse/icon/{domain}"
    return (
        f' <a href="{url}" target="_blank" rel="noopener noreferrer" class="tool-link" data-pricing="{pricing}">'
        f'<img src="{icon}" data-fallback="{icon}" alt="" class="tool-link-icon">'
        f'<span class="tool-link-name">{name}</span></a>\n'
    )


def ensure_section(html: str, slug: str, title: str) -> str:
    if f'data-category="{slug}"' in html:
        return html
    block = (
        f'\n <section class="tool-category" data-category="{slug}">\n'
        f' <h3 class="category-title">{title}</h3>\n'
        f' <div class="category-tools">\n'
        f" </div>\n"
        f" </section>\n"
    )
    # Insert before OSINT block if present, else before end of tools-directory
    marker = 'data-category="osint-username"'
    idx = html.find(marker)
    if idx != -1:
        # find start of that section
        sec = html.rfind("<section", 0, idx)
        return html[:sec] + block + html[sec:]
    marker2 = '</div>\n </div>\n</main>'
    # fallback: before closing tools-directory
    m = re.search(r'</div>\s*</div>\s*</main>', html)
    if m:
        return html[: m.start()] + block + html[m.start() :]
    return html + block


SECTION_TITLES = {
    "productivity": "Productivity",
    "design": "Design Tools",
    "programming": "Code Learning",
    "writing": "Writing",
    "privacy-tools": "Privacy Tools",
    "utilities": "Utilities",
    "data-tools": "Data Tools",
    "video": "Video Converters",
    "study": "Study",
    "free-stuff": "Free Stuff",
    "diagrams": "Diagrams",
    "pdf": "PDF Tools",
    "notepad": "Notepad",
    "regex": "Regex",
    "spreadsheets": "Spreadsheets",
    "resume": "Resume",
    "audio": "Audio Converters",
    "drawing": "Drawing",
    "security": "Security",
    "api-clients": "API Clients",
    "3d": "3D",
    "file-sharing": "File Sharing",
    "ai": "All-IN-One (AI)",
}


def main() -> None:
    data = json.loads(NOSIGNUPS_PATH.read_text(encoding="utf-8"))
    tools = data["tools"]
    html = HTML_PATH.read_text(encoding="utf-8")

    existing = set()
    for m in re.finditer(r'href="(https?://[^"]+)"', html):
        existing.add(norm_url(m.group(1)))

    by_cat: dict[str, list[tuple[str, str]]] = {}
    skipped = 0
    for tool in tools:
        url = (tool.get("url") or "").strip()
        if not url.startswith("http"):
            continue
        if norm_url(url) in existing:
            skipped += 1
            continue
        name = (tool.get("name") or domain_of(url)).strip()
        slug = pick_category(tool)
        by_cat.setdefault(slug, []).append((url, name))
        existing.add(norm_url(url))

    added = 0
    for slug, items in by_cat.items():
        title = SECTION_TITLES.get(slug, slug.replace("-", " ").title())
        html = ensure_section(html, slug, title)
        m = re.search(
            rf'(<section class="tool-category"[^>]*data-category="{re.escape(slug)}"[^>]*>.*?<div class="category-tools">)(.*?)(</div>\s*</section>)',
            html,
            re.DOTALL,
        )
        if not m:
            print(f"WARN: could not find section {slug}")
            continue
        block = m.group(2)
        new_links = ""
        for url, name in items:
            if norm_url(url) in {norm_url(u) for u in re.findall(r'href="(https?://[^"]+)"', block)}:
                continue
            # Nosignups = open-source, in-browser, no signup → free
            new_links += link_html(url, name, "free")
            added += 1
        html = html[: m.start(2)] + block + new_links + html[m.end(2) :]
        print(f"+{len(items):3d} -> {slug}")

    HTML_PATH.write_text(html, encoding="utf-8")
    print(f"\nAdded {added} new tools (skipped {skipped} already present)")


if __name__ == "__main__":
    main()
