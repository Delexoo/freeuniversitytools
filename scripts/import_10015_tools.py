"""Crawl 10015.io free browser tools and import into the directory."""
from __future__ import annotations

import json
import re
import time
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
HTML_PATH = ROOT / "data" / "student-directory.html"
OUT_JSON = ROOT / "data" / "10015-tools.json"

UA = {"User-Agent": "Mozilla/5.0 (compatible; FreeUniversityToolsBot/1.0)"}

CATEGORY_PAGES = [
    ("https://10015.io/text-tools", "writing"),
    ("https://10015.io/image-tools", "design"),
    ("https://10015.io/css-tools", "css-generators"),
    ("https://10015.io/coding-tools", "programming"),
    ("https://10015.io/color-tools", "design"),
    ("https://10015.io/social-media-tools", "social-media"),
    ("https://10015.io/miscellaneous-tools", "utilities"),
    ("https://10015.io/", "utilities"),
]

SECTION_TITLES = {
    "writing": "Writing",
    "design": "Design Tools",
    "css-generators": "CSS Generators",
    "programming": "Code Learning",
    "social-media": "Social Media Tools",
    "utilities": "Utilities",
    "pdf": "PDF Tools",
    "converters": "Converters",
    "security": "Security",
}

SECTION_RE = re.compile(
    r'(<section class="tool-category"[^>]*data-category="([^"]+)"[^>]*>.*?<div class="category-tools">)(.*?)(</div>\s*</section>)',
    re.DOTALL,
)

SLUG_TO_CAT = [
    (["pdf"], "pdf"),
    (["password", "encrypt", "decrypt", "md5", "sha", "jwt", "iban"], "security"),
    (["instagram", "tweet", "twitter", "whatsapp", "imessage", "youtube", "vimeo", "open-graph"], "social-media"),
    (["css-", "gradient", "glassmorphism", "box-shadow", "border-radius", "clip-path"], "css-generators"),
    (["image", "svg", "photo", "png", "crop", "resizer", "filter", "caption"], "design"),
    (["color", "hex", "rgba", "palette", "shades", "mixer"], "design"),
    (["html", "javascript", "json", "base64", "url-", "code-to", "minifier", "formatter", "slug"], "programming"),
    (["text", "lorem", "letter", "whitespace", "handwriting", "bionic", "case-converter", "list-randomizer", "font"], "writing"),
    (["qr", "barcode", "password"], "utilities"),
]


class LinkCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str]] = []
        self._href = ""
        self._parts: list[str] = []

    def handle_starttag(self, tag, attrs):  # noqa: ANN001
        if tag == "a":
            self._href = dict(attrs).get("href") or ""
            self._parts = []

    def handle_data(self, data: str) -> None:
        if self._href:
            self._parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self._href:
            text = re.sub(r"\s+", " ", "".join(self._parts)).strip()
            self.links.append((self._href, text))
            self._href = ""
            self._parts = []


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=45) as resp:
        return resp.read().decode("utf-8", "replace")


def norm_url(url: str) -> str:
    p = urlparse(url.strip().rstrip("/"))
    host = (p.netloc or "").lower().replace("www.", "")
    path = p.path.rstrip("/")
    return f"{host}{path}".lower()


def host_of(url: str) -> str:
    return urlparse(url).netloc.lower().replace("www.", "")


def abs_url(href: str) -> str:
    href = href.strip()
    if href.startswith("/"):
        return "https://10015.io" + href
    return href


def title_from_slug(slug: str) -> str:
    words = slug.replace("-", " ").strip()
    return " ".join(w.capitalize() if w.lower() not in {"to", "of", "and"} else w.lower() for w in words.split())


def map_category(tool_path: str, page_default: str) -> str:
    blob = tool_path.lower()
    for keys, slug in SLUG_TO_CAT:
        if any(k in blob for k in keys):
            return slug
    return page_default


def extract_tools_from_html(html: str, page_default: str) -> list[dict]:
    parser = LinkCollector()
    parser.feed(html)
    out: list[dict] = []
    seen: set[str] = set()
    for href, text in parser.links:
        url = abs_url(href).split("?")[0].rstrip("/")
        if "/tools/" not in url:
            continue
        if not url.startswith("https://10015.io/tools/"):
            continue
        key = norm_url(url)
        if key in seen:
            continue
        seen.add(key)
        slug = url.rsplit("/", 1)[-1]
        name = text if text and len(text) > 2 and "http" not in text.lower() else title_from_slug(slug)
        # Prefer longer descriptive title if nearby in page
        out.append(
            {
                "name": name[:100],
                "url": url,
                "slug": slug,
                "category": map_category(slug, page_default),
                "description": "",
                "pricing": "free",
                "source": "10015.io",
            }
        )
    return out


def enrich_from_home_sections(html: str, tools: list[dict]) -> None:
    """Pull short blurbs under tool names from homepage markdown-ish sections."""
    by_slug = {t["slug"]: t for t in tools}
    # Pattern: tool title heading then description paragraph near /tools/slug links
    for m in re.finditer(
        r'href="(/tools/([a-z0-9\-]+))"[^>]*>\s*([^<]{3,80})\s*</a>',
        html,
        re.I,
    ):
        slug = m.group(2)
        name = re.sub(r"\s+", " ", m.group(3)).strip()
        if slug in by_slug and name:
            by_slug[slug]["name"] = name[:100]


def ensure_section(html: str, slug: str) -> str:
    if f'data-category="{slug}"' in html:
        return html
    title = SECTION_TITLES.get(slug, slug.replace("-", " ").title())
    block = (
        f'\n <section class="tool-category" data-category="{slug}">\n'
        f' <h3 class="category-title">{title}</h3>\n'
        f' <div class="category-tools">\n'
        f" </div>\n"
        f" </section>\n"
    )
    m = re.search(r"</div>\s*</div>\s*</main>", html)
    if m:
        return html[: m.start()] + block + html[m.start() :]
    return html + block


def link_html(url: str, name: str) -> str:
    domain = host_of(url)
    icon = fb = f"https://icon.horse/icon/{domain}"
    safe = name.replace("&", "&amp;").replace("<", "&lt;")
    return (
        f' <a href="{url}" target="_blank" rel="noopener noreferrer" class="tool-link" data-pricing="free">'
        f'<img src="{icon}" data-fallback="{fb}" alt="" class="tool-link-icon">'
        f'<span class="tool-link-name">{safe}</span></a>\n'
    )


def crawl() -> list[dict]:
    all_tools: dict[str, dict] = {}
    for page_url, default_cat in CATEGORY_PAGES:
        print(f"Fetching {page_url} ...")
        try:
            html = fetch(page_url)
        except Exception as exc:  # noqa: BLE001
            print(f"  skip: {exc}")
            continue
        tools = extract_tools_from_html(html, default_cat)
        if page_url.rstrip("/").endswith("10015.io"):
            enrich_from_home_sections(html, tools)
        print(f"  found {len(tools)} tool links")
        for t in tools:
            key = norm_url(t["url"])
            prev = all_tools.get(key)
            if not prev or (len(t["name"]) > len(prev["name"])):
                all_tools[key] = t
        time.sleep(0.35)
    return sorted(all_tools.values(), key=lambda t: t["name"].lower())


def import_into_directory(tools: list[dict]) -> int:
    html = HTML_PATH.read_text(encoding="utf-8")
    existing = {norm_url(u) for u in re.findall(r'href="(https?://[^"]+)"', html)}
    by_cat: dict[str, list[dict]] = {}
    for t in tools:
        if norm_url(t["url"]) in existing:
            continue
        by_cat.setdefault(t["category"], []).append(t)

    added = 0
    for slug, items in sorted(by_cat.items(), key=lambda x: -len(x[1])):
        html = ensure_section(html, slug)
        m = re.search(
            rf'(<section class="tool-category"[^>]*data-category="{re.escape(slug)}"[^>]*>.*?<div class="category-tools">)(.*?)(</div>\s*</section>)',
            html,
            re.DOTALL,
        )
        if not m:
            print(f"WARN missing section {slug}")
            continue
        block = m.group(2)
        new_links = ""
        count = 0
        for t in items:
            key = norm_url(t["url"])
            if key in existing:
                continue
            new_links += link_html(t["url"], t["name"])
            existing.add(key)
            count += 1
            added += 1
        html = html[: m.start(2)] + block + new_links + html[m.end(2) :]
        print(f"+{count:3d} -> {slug}")

    HTML_PATH.write_text(html, encoding="utf-8")
    return added


def main() -> None:
    tools = crawl()
    OUT_JSON.write_text(json.dumps(tools, indent=2), encoding="utf-8")
    print(f"Saved {len(tools)} tools to {OUT_JSON}")
    added = import_into_directory(tools)
    print(f"Imported {added} new 10015.io tools into directory")


if __name__ == "__main__":
    main()
