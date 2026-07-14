"""Import free-for-dev SaaS/tool listings into student.html.

Source: https://github.com/ripienaar/free-for-dev (README.md)
Site:   https://free-for.dev/#/
"""
from __future__ import annotations

import re
import urllib.request
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
HTML_PATH = ROOT / "student.html"
JS_PATH = ROOT / "js" / "student.js"
README_URL = "https://raw.githubusercontent.com/ripienaar/free-for-dev/master/README.md"

SECTION_RE = re.compile(
    r'(<section class="tool-category" data-category="([^"]+)">.*?<div class="category-tools">)(.*?)(</div>\s*</section>)',
    re.DOTALL,
)
HREF_RE = re.compile(r'href="([^"]+)"')
BULLET_RE = re.compile(
    r"^\s*\*\s+\[([^\]]+)\]\((https?://[^)\s]+)\)\s*(.*)?$",
    re.MULTILINE,
)

# free-for-dev README section -> existing student.html data-category slug
SECTION_MAP: dict[str, str] = {
    "Major Cloud Providers": "cloud",
    "Cloud management solutions": "cloud",
    "Source Code Repos": "github-powerhouses",
    "APIs, Data, and ML": "api-platforms",
    "Artifact Repos": "deployment",
    "Tools for Teams and Collaboration": "collaboration",
    "CMS": "cms",
    "Code Generation": "programming-ai",
    "Code Quality": "programming",
    "Code Search and Browsing": "programming",
    "CI and CD": "deployment",
    "Testing": "programming",
    "Security and PKI": "security",
    "Authentication, Authorization, and User Management": "security",
    "Mobile App Distribution and Feedback": "utilities",
    "Management System": "productivity",
    "Messaging and Streaming": "collaboration",
    "Log Management": "utilities",
    "Translation Management": "translation",
    "Monitoring": "utilities",
    "Crash and Exception Handling": "utilities",
    "Search": "utilities",
    "Education and Career Development": "courses",
    "Email": "email",
    "Feature Toggles Management Platforms": "utilities",
    "Font": "fonts",
    "Forms": "utilities",
    "Generative AI": "generative-ai",
    "CDN and Protection": "cloud",
    "PaaS": "deployment",
    "BaaS": "databases",
    "Low-code Platform": "website-builders",
    "Web Hosting": "website-builders",
    "DNS": "utilities",
    "Domain": "utilities",
    "IaaS": "cloud",
    "Managed Data Services": "databases",
    "Tunneling, WebRTC, Web Socket Servers and Other Routers": "utilities",
    "Issue Tracking and Project Management": "productivity",
    "Storage and Media Processing": "file-sharing",
    "Design and UI": "design",
    "Data Visualization on Maps": "maps",
    "Package Build System": "programming",
    "IDE and Code Editing": "code-editors",
    "Analytics, Events and Statistics": "data-tools",
    "Visitor Session Recording": "utilities",
    "International Mobile Number Verification API and SDK": "api-platforms",
    "Payment and Billing Integration": "finance",
    "Docker Related": "devops",
    "Dev Blogging Sites": "writing",
    "Commenting Platforms": "utilities",
    "Screenshot APIs": "api-platforms",
    "Flutter Related and Building IOS Apps without Mac": "programming",
    "Privacy Management": "security",
    "Miscellaneous": "utilities",
    "Remote Desktop Tools": "utilities",
    "Other Free Resources": "free-stuff",
}

SKIP_HOSTS = {
    "github.com/ripienaar/free-for-dev",
    "free-for.dev",
    "www.free-for.dev",
}

KEYWORD_PATCHES = {
    "api-platforms": ["free for dev", "free tier api", "public api free"],
    "deployment": ["paas", "free hosting", "cicd free tier"],
    "cloud": ["free for developers", "free cloud tier"],
    "email": ["transactional email free", "free smtp"],
}


def norm_url(url: str) -> str:
    p = urlparse(url.strip().rstrip("/"))
    host = (p.netloc or "").lower().replace("www.", "")
    path = p.path.rstrip("/")
    return f"{host}{path}".lower()


def github_owner(url: str) -> str | None:
    p = urlparse(url)
    if p.netloc.lower().replace("www.", "") != "github.com":
        return None
    parts = [part for part in p.path.split("/") if part]
    return parts[0] if parts else None


def should_skip(url: str, name: str, note: str) -> bool:
    key = norm_url(url)
    if not key:
        return True
    if "taken down" in note.lower() or "possibly taken down" in note.lower():
        return True
    if key.startswith("github.com/ripienaar/free-for-dev"):
        return True
    host = urlparse(url).netloc.lower().replace("www.", "")
    if host in SKIP_HOSTS:
        return True
    low = name.strip().lower()
    if not low or low in {"back to top", "table of contents"}:
        return True
    return False


def clean_name(name: str, url: str) -> str:
    name = re.sub(r"\s+", " ", name.strip())
    name = name.replace("`", "")
    if not name:
        host = urlparse(url).netloc.replace("www.", "")
        name = host.split(".")[0].title()
    return name[:80]


def link(url: str, name: str, pricing: str = "free-tier") -> str:
    owner = github_owner(url)
    domain = urlparse(url).netloc.replace("www.", "")
    if owner:
        icon = fb = f"https://github.com/{owner}.png?size=64"
    else:
        icon = fb = f"https://icon.horse/icon/{domain}"
    safe = name.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return (
        f' <a href="{url}" target="_blank" rel="noopener noreferrer" class="tool-link" data-pricing="{pricing}">'
        f'<img src="{icon}" data-fallback="{fb}" alt="" class="tool-link-icon">'
        f'<span class="tool-link-name">{safe}</span></a>\n'
    )


def fetch_readme() -> str:
    req = urllib.request.Request(
        README_URL,
        headers={"User-Agent": "Mozilla/5.0 (compatible; FUTImporter/1.0)"},
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def parse_readme(text: str) -> dict[str, list[tuple[str, str]]]:
    additions: dict[str, list[tuple[str, str]]] = {}
    unmatched_sections: list[str] = []

    parts = re.split(r"^## ", text, flags=re.MULTILINE)
    for part in parts[1:]:
        title = part.splitlines()[0].strip()
        # Skip TOC-like / meta sections
        if title.lower() in {"table of contents", "contributing", "license"}:
            continue
        slug = SECTION_MAP.get(title)
        if not slug:
            unmatched_sections.append(title)
            slug = "utilities"

        for name, url, note in BULLET_RE.findall(part):
            if should_skip(url, name, note or ""):
                continue
            clean = clean_name(name, url)
            additions.setdefault(slug, []).append((url, clean))

    if unmatched_sections:
        print("Unmapped sections (fell back to utilities):", unmatched_sections)
    return additions


def existing_urls(html: str) -> set[str]:
    return {norm_url(h) for h in HREF_RE.findall(html) if h.startswith("http")}


def patch_keywords(js_text: str) -> str:
    for cat_id, words in KEYWORD_PATCHES.items():
        # Match both quoted and unquoted keys
        pattern = re.compile(
            rf"('{cat_id}'|\"{cat_id}\"|{cat_id})\s*:\s*\[([^\]]*)\]",
            re.DOTALL,
        )
        match = pattern.search(js_text)
        if not match:
            continue
        existing = match.group(2)
        additions = []
        for w in words:
            if w.lower() not in existing.lower():
                additions.append(f'"{w}"')
        if not additions:
            continue
        insert = (", ".join(additions) + ", ") if existing.strip() else ", ".join(additions)
        # put near front after opening bracket content start
        new_block = match.group(0).replace("[", "[" + insert, 1)
        js_text = js_text[: match.start()] + new_block + js_text[match.end() :]
        print(f"Patched keywords for {cat_id}")
    return js_text


def main() -> None:
    print("Fetching free-for-dev README…")
    readme = fetch_readme()
    by_category = parse_readme(readme)
    total_parsed = sum(len(v) for v in by_category.values())
    print(f"Parsed {total_parsed} tools across {len(by_category)} categories")

    html = HTML_PATH.read_text(encoding="utf-8")
    known = existing_urls(html)
    print(f"Existing tool URLs in student.html: {len(known)}")

    added_by_cat: Counter[str] = Counter()
    skipped_dup = 0
    new_rows: dict[str, list[str]] = {}

    for slug, entries in by_category.items():
        for url, name in entries:
            key = norm_url(url)
            if key in known:
                skipped_dup += 1
                continue
            known.add(key)
            new_rows.setdefault(slug, []).append(link(url, name))
            added_by_cat[slug] += 1

    missing_sections = [s for s in new_rows if f'data-category="{s}"' not in html]
    if missing_sections:
        raise SystemExit(f"Missing category sections in student.html: {missing_sections}")

    def replace_section(match: re.Match[str]) -> str:
        prefix, slug, tools_html, suffix = match.group(1), match.group(2), match.group(3), match.group(4)
        rows = new_rows.get(slug)
        if not rows:
            return match.group(0)
        return f"{prefix}{tools_html}{''.join(rows)}{suffix}"

    new_html, n = SECTION_RE.subn(replace_section, html)
    if n == 0:
        raise SystemExit("No sections matched — check SECTION_RE")

    HTML_PATH.write_text(new_html, encoding="utf-8", newline="\n")

    try:
        js = JS_PATH.read_text(encoding="utf-8")
        patched = patch_keywords(js)
        if patched != js:
            JS_PATH.write_text(patched, encoding="utf-8", newline="\n")
    except Exception as exc:
        print(f"Keyword patch skipped: {exc}")

    print("\nAdded by category:")
    for slug, count in sorted(added_by_cat.items(), key=lambda x: (-x[1], x[0])):
        print(f"  {count:4d}  {slug}")
    print(f"\nTotal added: {sum(added_by_cat.values())}")
    print(f"Duplicates skipped: {skipped_dup}")


if __name__ == "__main__":
    main()
