"""Second-pass deep crawl of Free Stuff hub pages for more tool links."""
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

SECTION_RE = re.compile(
    r'(<section class="tool-category" data-category="([^"]+)">.*?<div class="category-tools">)(.*?)(</div>\s*</section>)',
    re.DOTALL,
)
HREF_RE = re.compile(r'href="([^"]+)"')

DEEP_SEEDS = [
    "https://fmhy.net/internet-tools",
    "https://fmhy.net/artificial-intelligence",
    "https://fmhy.net/audio",
    "https://fmhy.net/video",
    "https://fmhy.net/gaming",
    "https://fmhy.net/reading",
    "https://fmhy.net/downloading",
    "https://fmhy.net/educational",
    "https://fmhy.net/android-ios",
    "https://fmhy.net/linux-macos",
    "https://fmhy.net/non-english",
    "https://fmhy.net/miscellaneous",
    "https://champagne.pages.dev/",
    "https://free-for.dev/",
    "https://oss.gallery/",
    "https://openalternative.co/",
    "https://libreprojects.net/",
    "https://deepwebnest.com/",
]

SKIP_HOSTS = {
    "start.me", "google.com", "gstatic.com", "googleapis.com", "facebook.com",
    "twitter.com", "x.com", "linkedin.com", "instagram.com", "youtube.com",
    "youtu.be", "w3.org", "schema.org", "cloudflare.com", "github.io",
    "freeuniversitytools.com", "www.freeuniversitytools.com", "fmhy.net",
    "reddit.com", "discord.com", "discord.gg", "t.me", "matrix.to",
}


class LinkExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for k, v in attrs:
                if k == "href" and v:
                    self.links.append(v)


def norm_url(url: str) -> str:
    p = urlparse(url.strip().rstrip("/"))
    return f"{p.netloc.lower().replace('www.', '')}{p.path.rstrip('/').lower()}"


def host_of(url: str) -> str:
    return urlparse(url).netloc.lower().replace("www.", "")


def should_skip(url: str) -> bool:
    if not url.startswith("http"):
        return True
    host = host_of(url)
    return any(host == s or host.endswith("." + s) for s in SKIP_HOSTS)


def clean_name(url: str) -> str:
    path = urlparse(url).path.strip("/")
    name = path.split("/")[-1] if path else host_of(url).split(".")[0]
    return re.sub(r"[-_]+", " ", name).title()[:80]


def github_owner(url: str) -> str | None:
    p = urlparse(url)
    if p.netloc.lower().replace("www.", "") != "github.com":
        return None
    parts = [p for p in p.path.split("/") if p]
    return parts[0] if parts else None


def link(url: str, name: str) -> str:
    owner = github_owner(url)
    domain = urlparse(url).netloc.replace("www.", "")
    icon = f"https://github.com/{owner}.png?size=64" if owner else f"https://icon.horse/icon/{domain}"
    safe = name.replace("&", "&amp;")
    return (
        f' <a href="{url}" target="_blank" rel="noopener noreferrer" class="tool-link" data-pricing="free">'
        f'<img src="{icon}" data-fallback="{icon}" alt="" class="tool-link-icon">'
        f'<span class="tool-link-name">{safe}</span></a>\n'
    )


def categorize(url: str, name: str) -> str:
    b = f"{url} {name}".lower()
    if "github.com" in b:
        return "github-powerhouses"
    if any(x in b for x in ["movie", "stream", "anime", "torrent", "cinema", "tv"]):
        return "free-movies"
    if any(x in b for x in ["book", "ebook", "pdf", "read", "library"]):
        return "free-books"
    if any(x in b for x in ["course", "learn", "edu", "academy", "tutorial"]):
        return "courses"
    if any(x in b for x in ["design", "ui", "font", "css", "figma", "component"]):
        return "design"
    if any(x in b for x in ["ai", "gpt", "llm", "chat"]):
        return "ai"
    if any(x in b for x in ["osint", "intel", "recon", "investigat", "breach", "whois"]):
        return "osint-tools"
    if any(x in b for x in ["free", "alternative", "open source", "wiki", "selfhost"]):
        return "free-stuff"
    return "utilities"


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; FUTDeepCrawl/1.0)"})
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.read().decode("utf-8", errors="ignore")


def extract(url: str) -> list[tuple[str, str]]:
    try:
        html = fetch(url)
    except (urllib.error.URLError, TimeoutError, OSError):
        return []
    p = LinkExtractor()
    p.feed(html)
    out = []
    seen = set()
    for href in p.links:
        full = urljoin(url, href).split("#")[0].rstrip("/")
        if should_skip(full):
            continue
        key = norm_url(full)
        if key in seen:
            continue
        seen.add(key)
        out.append((full, clean_name(full)))
    return out


def main():
    html = HTML_PATH.read_text(encoding="utf-8")
    known = {norm_url(u) for u in HREF_RE.findall(html)}
    additions: dict[str, list[tuple[str, str]]] = {}

    for seed in DEEP_SEEDS:
        links = extract(seed)
        print(f"{seed}: {len(links)} links")
        for url, name in links:
            cat = categorize(url, name)
            additions.setdefault(cat, []).append((url, name))
        time.sleep(0.4)

    added = skipped = 0
    by_cat = {}

    def replacer(match):
        nonlocal added, skipped
        cat = match.group(2)
        if cat not in additions:
            return match.group(0)
        inner = match.group(3)
        new = []
        seen = set()
        for url, name in additions[cat]:
            key = norm_url(url)
            if key in known or key in seen:
                skipped += 1
                continue
            seen.add(key)
            known.add(key)
            new.append(link(url, name))
            added += 1
            by_cat[cat] = by_cat.get(cat, 0) + 1
        if not new:
            return match.group(0)
        return match.group(1) + inner.rstrip() + "\n" + "".join(new) + " " + match.group(4)

    html = SECTION_RE.sub(replacer, html)
    HTML_PATH.write_text(html, encoding="utf-8", newline="\n")
    print(json.dumps({"added": added, "skipped": skipped, "by_cat": by_cat}, indent=2))


if __name__ == "__main__":
    main()
