"""Import tools from user batch, OSINT4ALL Start.me export, and Free Stuff deep crawl."""
import json
import re
import time
import urllib.error
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse

ROOT = Path(__file__).resolve().parent.parent
HTML_PATH = ROOT / "student.html"
JS_PATH = ROOT / "js" / "student.js"
OSINT_HTML = Path(r"c:\Users\Massi\Downloads\OSINT4ALL - Start_me.html")
OUT_JSON = ROOT / "scripts" / "batch_import_candidates.json"

SECTION_RE = re.compile(
    r'(<section class="tool-category" data-category="([^"]+)">.*?<div class="category-tools">)(.*?)(</div>\s*</section>)',
    re.DOTALL,
)
HREF_RE = re.compile(r'href="([^"]+)"')

SKIP_HOSTS = {
    "start.me", "google.com", "gstatic.com", "googleapis.com", "facebook.com",
    "twitter.com", "x.com", "linkedin.com", "instagram.com", "youtube.com",
    "youtu.be", "reddit.com", "w3.org", "schema.org", "cloudflare.com",
    "googletagmanager.com", "google-analytics.com", "doubleclick.net",
    "freeuniversitytools.com", "www.freeuniversitytools.com",
}

FREE_STUFF_SEEDS = [
    "https://fmhy.net/",
    "https://champagne.pages.dev/",
    "https://alternativeto.net/",
    "https://opensource.builders/",
    "https://openalternative.co/",
    "https://oss.gallery/",
    "https://libreprojects.net/",
    "https://libreselfhosted.com/",
    "https://deepwebnest.com/",
    "https://free-for.dev/",
]

USER_BATCH = {
    "free-stuff": [
        ("https://free-for.dev/", "Free For Dev"),
        ("https://start.me/p/L1rEYQ/osint4all", "OSINT4ALL"),
    ],
    "osint-geolocation-tools-maps": [
        ("https://oceanir.ai/geospy-alternative", "Oceanir GeoSpy Alt"),
        ("https://github.com/Mahanaicoach/google-maps-scraper-kit", "Google Maps Scraper Kit"),
    ],
    "osint-cloud-infrastructure": [
        ("https://grayhatwarfare.com/", "GrayHat Warfare"),
    ],
    "osint-cyber-threat-intelligence": [
        ("https://cybermap.kaspersky.com/", "Kaspersky Cybermap"),
    ],
    "osint-email-address": [
        ("https://behindtheemail.com/", "Behind The Email"),
    ],
    "osint-ai-tools": [
        ("https://arena.ai/", "Arena AI"),
        ("https://github.com/RamsesAguirre777/facebook-ads-library-mcp", "Facebook Ads Library MCP"),
    ],
    "design": [
        ("https://styles.refero.design/", "Refero Styles"),
        ("https://font-tester.foxcraft.tech/", "Font Tester"),
        ("https://reactbits.dev/", "React Bits"),
    ],
    "free-movies": [
        ("https://cinevice.net/", "Cinevice"),
    ],
}

KEYWORD_PATCHES = {
    "free-stuff": ["free for dev", "osint4all", "start.me"],
    "design": ["refero", "react bits", "font tester", "design.md"],
    "osint-geolocation-tools-maps": ["oceanir", "geospy alternative", "maps scraper"],
    "osint-cloud-infrastructure": ["grayhat warfare"],
    "osint-cyber-threat-intelligence": ["kaspersky cybermap", "cybermap"],
    "osint-email-address": ["behind the email"],
    "osint-ai-tools": ["arena ai", "facebook ads library mcp"],
    "free-movies": ["cinevice"],
}


class LinkExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links: list[str] = []
        self._in_title = False
        self.titles: dict[str, str] = {}

    def handle_starttag(self, tag, attrs):
        attrs_d = dict(attrs)
        if tag == "a" and "href" in attrs_d:
            self.links.append(attrs_d["href"])
            self._pending_href = attrs_d["href"]
        if tag in ("title", "h1", "h2", "h3", "h4"):
            self._in_title = True
            self._title_buf = []

    def handle_endtag(self, tag):
        if tag in ("title", "h1", "h2", "h3", "h4") and getattr(self, "_in_title", False):
            self._in_title = False
            title = "".join(self._title_buf).strip()
            href = getattr(self, "_pending_href", None)
            if href and title and href.startswith("http"):
                self.titles[href.split("#")[0].rstrip("/")] = title[:80]

    def handle_data(self, data):
        if getattr(self, "_in_title", False):
            self._title_buf.append(data)


def norm_url(url: str) -> str:
    p = urlparse(url.strip().rstrip("/"))
    host = (p.netloc or "").lower().replace("www.", "")
    path = p.path.rstrip("/")
    return f"{host}{path}".lower()


def host_of(url: str) -> str:
    return urlparse(url).netloc.lower().replace("www.", "")


def should_skip(url: str) -> bool:
    if not url.startswith("http"):
        return True
    host = host_of(url)
    if any(host == s or host.endswith("." + s) for s in SKIP_HOSTS):
        return True
    if "start.me" in host:
        return True
    return False


def clean_name(url: str, fallback: str = "") -> str:
    if fallback:
        name = fallback.strip()
    else:
        path = urlparse(url).path.strip("/")
        name = path.split("/")[-1] if path else host_of(url).split(".")[0]
    name = re.sub(r"\s+", " ", name)
    name = name.replace("-", " ").replace("_", " ")
    if name.islower() or name.isupper():
        name = name.title()
    return name[:80] or "Tool"


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


def fetch_html(url: str) -> str:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (compatible; FUTImporter/1.0)"},
    )
    with urllib.request.urlopen(req, timeout=25) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def extract_links_from_html(html: str, base_url: str) -> list[tuple[str, str]]:
    parser = LinkExtractor()
    parser.feed(html)
    out: list[tuple[str, str]] = []
    seen: set[str] = set()
    for href in parser.links:
        full = urljoin(base_url, href).split("#")[0].rstrip("/")
        if should_skip(full):
            continue
        key = norm_url(full)
        if key in seen:
            continue
        seen.add(key)
        title = parser.titles.get(full, "")
        out.append((full, clean_name(full, title)))
    return out


def parse_startme_export(path: Path) -> list[tuple[str, str]]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    # Start.me exports embed bookmark data in JSON-ish structures and hrefs
    entries: list[tuple[str, str]] = []
    seen: set[str] = set()

    # Named links: title near url in bookmark widgets
    for m in re.finditer(
        r'"title"\s*:\s*"([^"]+)"[^}]{0,400}?"url"\s*:\s*"(https?://[^"]+)"',
        text,
        re.DOTALL,
    ):
        title, url = m.group(1), m.group(2).replace("\\/", "/")
        url = url.split("#")[0].rstrip("/")
        if should_skip(url):
            continue
        key = norm_url(url)
        if key in seen:
            continue
        seen.add(key)
        entries.append((url, clean_name(url, title)))

    # Fallback: all hrefs
    for href in re.findall(r'href="(https?://[^"]+)"', text, re.I):
        url = href.split("#")[0].rstrip("/")
        if should_skip(url):
            continue
        key = norm_url(url)
        if key in seen:
            continue
        seen.add(key)
        entries.append((url, clean_name(url)))

    return entries


def categorize_osint(url: str, name: str) -> str:
    host = host_of(url)
    blob = f"{host} {name} {url}".lower()
    rules = [
        ("osint-email-address", ["email", "mail", "smtp", "breach", "hibp"]),
        ("osint-username", ["username", "user search", "namechk", "sherlock"]),
        ("osint-domain-name", ["domain", "dns", "whois", "subdomain", "crt.sh"]),
        ("osint-ip-mac-address", ["ip ", "ip-", "mac address", "shodan", "censys"]),
        ("osint-geolocation-tools-maps", ["map", "geo", "location", "coordinates", "satellite"]),
        ("osint-images-videos-docs", ["image", "video", "exif", "reverse image", "ocr"]),
        ("osint-social-networks", ["social", "instagram", "twitter", "tiktok", "facebook", "linkedin"]),
        ("osint-instant-messaging", ["telegram", "discord", "whatsapp", "signal", "messaging"]),
        ("osint-dark-web", ["dark web", "tor", "onion"]),
        ("osint-blockchain-cryptocurrency", ["blockchain", "crypto", "bitcoin", "ethereum", "wallet"]),
        ("osint-cyber-threat-intelligence", ["threat", "malware", "virustotal", "cyber", "kaspersky", "attack"]),
        ("osint-cloud-infrastructure", ["bucket", "s3", "azure", "gcp", "cloud", "grayhat"]),
        ("osint-search-engines", ["search engine", "metasearch", "dork"]),
        ("osint-archives", ["archive", "wayback", "cached"]),
        ("osint-telephone-numbers", ["phone", "telephone", "caller"]),
        ("osint-ai-tools", ["ai ", "gpt", "llm", "mcp"]),
        ("osint-tools", ["osint", "investigat", "recon"]),
    ]
    for cat, keys in rules:
        if any(k in blob for k in keys):
            return cat
    return "osint-tools"


def categorize_general(url: str, name: str) -> str:
    host = host_of(url)
    blob = f"{host} {name} {url}".lower()
    if "github.com" in host:
        return "github-powerhouses"
    if any(k in blob for k in ["movie", "stream", "torrent", "anime", "tv ", "cinema", "cine"]):
        return "free-movies"
    if any(k in blob for k in ["design", "ui", "font", "css", "react", "figma", "component"]):
        return "design"
    if any(k in blob for k in ["course", "learn", "tutorial", "education", "academy"]):
        return "courses"
    if any(k in blob for k in ["book", "ebook", "pdf", "library", "archive.org"]):
        return "free-books"
    if any(k in blob for k in ["ai", "gpt", "llm", "chatbot", "claude", "openai"]):
        return "ai"
    if any(k in blob for k in ["free", "alternative", "open source", "selfhost", "fmhy", "wiki"]):
        return "free-stuff"
    if any(k in blob for k in ["osint", "intel", "recon", "investigat"]):
        return categorize_osint(url, name)
    return "utilities"


def patch_keywords(js_text: str) -> str:
    for cat_id, words in KEYWORD_PATCHES.items():
        pattern = rf"('{cat_id}'|{cat_id}): \[([^\]]*)\]"
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


def main():
    html = HTML_PATH.read_text(encoding="utf-8")
    known = {norm_url(u) for u in HREF_RE.findall(html)}
    additions: dict[str, list[tuple[str, str]]] = {k: list(v) for k, v in USER_BATCH.items()}

    # OSINT4ALL Start.me export
    if OSINT_HTML.exists():
        osint_entries = parse_startme_export(OSINT_HTML)
        print(f"OSINT4ALL export: {len(osint_entries)} unique links")
        for url, name in osint_entries:
            cat = categorize_osint(url, name)
            additions.setdefault(cat, []).append((url, name))
    else:
        print("OSINT4ALL HTML not found, skipping")

    # Deep crawl Free Stuff seeds (light pass)
    crawled = 0
    for seed in FREE_STUFF_SEEDS:
        try:
            page = fetch_html(seed)
            links = extract_links_from_html(page, seed)
            crawled += len(links)
            for url, name in links[:80]:
                cat = categorize_general(url, name)
                additions.setdefault(cat, []).append((url, name))
            time.sleep(0.5)
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            print(f"crawl skip {seed}: {e}")

    print(f"Free Stuff crawl extracted ~{crawled} links from seeds")

    # Dedupe and apply
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
        seen_local: set[str] = set()
        for url, name in additions[cat]:
            key = norm_url(url)
            if key in known or key in seen_local:
                skipped += 1
                continue
            seen_local.add(key)
            known.add(key)
            new_links.append(link(url, name))
            added += 1
            added_by_cat[cat] = added_by_cat.get(cat, 0) + 1
        if not new_links:
            return match.group(0)
        return match.group(1) + inner.rstrip() + "\n" + "".join(new_links) + " " + match.group(4)

    html = SECTION_RE.sub(replacer, html)
    HTML_PATH.write_text(html, encoding="utf-8", newline="\n")

    js_text = JS_PATH.read_text(encoding="utf-8")
    JS_PATH.write_text(patch_keywords(js_text), encoding="utf-8", newline="\n")

    summary = {"added_total": added, "skipped_duplicates": skipped, "added_by_category": added_by_cat}
    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
