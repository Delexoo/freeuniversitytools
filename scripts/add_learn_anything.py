"""Add Learn Anything and its curated open-source tools to student.html."""
import json
import re
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
HTML_PATH = ROOT / "student.html"
JS_PATH = ROOT / "js" / "student.js"
SCRAPE_OUT = ROOT / "scripts" / "learn_anything_os_tools.json"

SECTION_RE = re.compile(
    r'(<section class="tool-category" data-category="([^"]+)">.*?<div class="category-tools">)(.*?)(</div>\s*</section>)',
    re.DOTALL,
)
HREF_RE = re.compile(r'href="([^"]+)"')
GITHUB_RE = re.compile(r"https?://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)")
MD_LINK_RE = re.compile(
    r"\[([^\]]+)\]\((https?://github\.com/[^)\s]+)\)", re.IGNORECASE
)

CURATED_TOOL_LISTS = {
    "chrome-extension": "learn-anything/chrome-extensions",
    "browser-extensions": "learn-anything/firefox-extensions",
    "utilities": "learn-anything/command-line-tools",
    "open-source": "learn-anything/macos-apps",
}

OSS_LIST_REPOS = [
    ("https://github.com/unicodeveloper/awesome-opensource-apps", "Awesome OSS Apps"),
    ("https://github.com/jwaterfaucett/awesome-foss-apps", "Awesome FOSS Apps"),
    ("https://github.com/MunGell/awesome-for-beginners", "Awesome for Beginners"),
    ("https://github.com/ossfriendly/open-source-supporters", "OSS Supporters"),
]

LEARN_ANYTHING = ("https://learn-anything.xyz/", "Learn Anything")

KEYWORD_PATCHES = {
    "courses": ["learn anything", "learning paths", "knowledge maps", "mind maps"],
    "open-source": ["learn anything", "awesome oss apps", "awesome foss apps"],
    "study": ["learn anything", "learning paths"],
}


def norm_url(url: str) -> str:
    p = urlparse(url.strip().rstrip("/"))
    host = (p.netloc or "").lower().replace("www.", "")
    path = p.path.rstrip("/")
    return f"{host}{path}".lower()


def clean_github(url: str) -> str | None:
    m = GITHUB_RE.search(url)
    if not m:
        return None
    return f"https://github.com/{m.group(1)}/{m.group(2)}"


def github_owner(url: str) -> str | None:
    p = urlparse(url)
    if p.netloc.lower().replace("www.", "") != "github.com":
        return None
    parts = [part for part in p.path.split("/") if part]
    return parts[0] if parts else None


def link(url: str, name: str, pricing: str = "free") -> str:
    owner = github_owner(url)
    domain = urlparse(url).netloc.replace("www.", "")
    if owner:
        icon = fb = f"https://github.com/{owner}.png?size=64"
    else:
        icon = f"https://icon.horse/icon/{domain}"
        fb = f"https://icon.horse/icon/{domain}"
    safe = name.replace("&", "&amp;")
    return (
        f' <a href="{url}" target="_blank" rel="noopener noreferrer" class="tool-link" data-pricing="{pricing}">'
        f'<img src="{icon}" data-fallback="{fb}" alt="" class="tool-link-icon">'
        f'<span class="tool-link-name">{safe}</span></a>\n'
    )


def fetch_text(url: str) -> str | None:
    try:
        with urllib.request.urlopen(url, timeout=45) as resp:
            return resp.read().decode("utf-8", errors="ignore")
    except Exception:
        return None


def fetch_readme(repo: str) -> str | None:
    for branch in ("main", "master"):
        text = fetch_text(f"https://raw.githubusercontent.com/{repo}/{branch}/readme.md")
        if text:
            return text
    return None


def parse_github_entries(text: str) -> list[tuple[str, str]]:
    entries: list[tuple[str, str]] = []
    seen: set[str] = set()
    for name, url in MD_LINK_RE.findall(text):
        gh = clean_github(url)
        if not gh or gh.lower() in seen:
            continue
        seen.add(gh.lower())
        clean_name = re.sub(r"\s+", " ", name.strip())
        if not clean_name:
            clean_name = gh.rsplit("/", 1)[-1]
        entries.append((gh, clean_name[:80]))
    return entries


def collect_tools() -> dict[str, list[tuple[str, str]]]:
    by_category: dict[str, list[tuple[str, str]]] = {
        "courses": [LEARN_ANYTHING],
        "open-source": [LEARN_ANYTHING] + list(OSS_LIST_REPOS),
        "study": [LEARN_ANYTHING],
    }

    for category, repo in CURATED_TOOL_LISTS.items():
        text = fetch_readme(repo)
        if not text:
            print(f"skip unreadable list: {repo}")
            continue
        entries = parse_github_entries(text)
        by_category.setdefault(category, []).extend(entries)
        print(f"{repo}: {len(entries)} github entries -> {category}")

    for repo_url, list_name in OSS_LIST_REPOS:
        repo = repo_url.replace("https://github.com/", "")
        text = fetch_readme(repo)
        if not text:
            continue
        entries = parse_github_entries(text)
        by_category.setdefault("github-powerhouses", []).extend(entries[:120])
        print(f"{list_name}: {len(entries)} apps parsed")

    return by_category


def patch_keywords(js_text: str) -> str:
    for cat_id, words in KEYWORD_PATCHES.items():
        pattern = rf"('{cat_id}': \[)([^\]]*)(\],)"
        match = re.search(pattern, js_text)
        if not match:
            continue
        existing = match.group(2)
        additions = []
        for word in words:
            token = f"'{word}'"
            if token not in existing:
                additions.append(token)
        if additions:
            suffix = ", " if existing.strip() else " "
            js_text = (
                js_text[: match.start(2)]
                + existing
                + suffix
                + ", ".join(additions)
                + js_text[match.end(2) :]
            )
    return js_text


def main() -> None:
    additions = collect_tools()
    html = HTML_PATH.read_text(encoding="utf-8")
    known = {norm_url(u) for u in HREF_RE.findall(html)}
    added = 0
    skipped = 0
    added_by_cat: dict[str, int] = {}

    def replacer(match):
        nonlocal added, skipped
        cat = match.group(2)
        if cat not in additions:
            return match.group(0)
        inner = match.group(3)
        new_links = []
        for url, name in additions[cat]:
            key = norm_url(url)
            if key in known:
                skipped += 1
                continue
            known.add(key)
            new_links.append(link(url, name))
            added += 1
            added_by_cat[cat] = added_by_cat.get(cat, 0) + 1
        if not new_links:
            return match.group(0)
        inner_clean = inner.rstrip() + "\n"
        return match.group(1) + inner_clean + "".join(new_links) + " " + match.group(4)

    html = SECTION_RE.sub(replacer, html)
    HTML_PATH.write_text(html, encoding="utf-8", newline="\n")

    js_text = JS_PATH.read_text(encoding="utf-8")
    JS_PATH.write_text(patch_keywords(js_text), encoding="utf-8", newline="\n")

    summary = {
        "added_total": added,
        "skipped_duplicates": skipped,
        "added_by_category": added_by_cat,
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
