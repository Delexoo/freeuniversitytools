"""Import tools from FMHY (fmhy.net) single-page markdown into student.html."""
from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
HTML_PATH = ROOT / "data" / "student-directory.html"
FMHY_PATH = ROOT / "data" / "fmhy-single-page.md"

SECTION_RE = re.compile(
    r'(<section class="tool-category"[^>]*data-category="([^"]+)"[^>]*>.*?<div class="category-tools">)(.*?)(</div>\s*</section>)',
    re.DOTALL,
)

# Markdown link: optional bold/star wrappers
LINK_RE = re.compile(
    r"(?:\*\*)?\[([^\]]{1,120})\]\((https?://[^)\s]+)\)(?:\*\*)?",
)

HEADER_RE = re.compile(r"^#{1,3}\s+(.+)$", re.M)

SKIP_HOSTS = {
    "reddit.com",
    "www.reddit.com",
    "old.reddit.com",
    "discord.com",
    "discord.gg",
    "t.me",
    "telegram.me",
    "x.com",
    "twitter.com",
    "facebook.com",
    "instagram.com",
    "tiktok.com",
    "youtu.be",
    "matrix.to",
    "rentry.co",
    "rentry.org",
    "fmhy.net",
    "www.fmhy.net",
    "api.fmhy.net",
    "github.com/fmhy",
    "freeuniversitytools.com",
    "www.freeuniversitytools.com",
}

SKIP_NAME_BITS = {
    "note",
    "notes",
    "guide",
    "wiki",
    "subreddit",
    "discord",
    "telegram",
    "x",
    "2",
    "3",
    "4",
    "mirror",
    "mirrors",
    "backup",
    "backups",
    "source",
    "github",
    "gitlab",
    "codeberg",
}

# FMHY section keyword → our category slug
SECTION_MAP = [
    (["adblock", "privacy", "dns", "tracker", "antivirus", "password", "vpn", "tor"], "privacy-tools"),
    (["artificial intelligence", "ai ", " llm", "chatgpt", "image gen", "ai tools"], "ai"),
    (["educational", "course", "learn", "university", "study", "school", "mooc"], "courses"),
    (["reading", "book", "ebook", "textbook", "comic", "manga", "light novel"], "free-books"),
    (["streaming", "movie", "tv", "anime", "drama", "live tv"], "free-movies"),
    (["listening", "music", "podcast", "radio", "audio"], "music"),
    (["gaming", "emulator", "rom", "game"], "browser-games"),
    (["android", "ios", "mobile", "apk"], "utilities"),
    (["linux", "macos", "unix", "homebrew"], "utilities"),
    (["downloading", "software", "freeware", "warez", "cracked"], "free-stuff"),
    (["torrent"], "free-movies"),
    (["design", "photo", "image", "font", "svg"], "design"),
    (["developer", "coding", "programming", "devtools", "github"], "programming"),
    (["internet tools", "browser", "extension", "userscript"], "browser-extensions"),
    (["system tools", "windows", "utilities"], "utilities"),
    (["storage", "file", "cloud", "transfer"], "file-sharing"),
    (["social media", "social"], "social-media"),
    (["writing", "text", "document", "office"], "writing"),
    (["video tools", "video editing"], "video"),
    (["non-english", "non english"], "free-stuff"),
    (["misc", "miscellaneous", "fun", "food", "travel", "shopping"], "free-stuff"),
]

SECTION_TITLES = {
    "privacy-tools": "Privacy Tools",
    "ai": "All-IN-One (AI)",
    "courses": "Course",
    "free-books": "Free Books",
    "free-movies": "Free Movies",
    "music": "Music",
    "browser-games": "Browser Games",
    "utilities": "Utilities",
    "free-stuff": "Free Stuff",
    "design": "Design Tools",
    "programming": "Code Learning",
    "browser-extensions": "Browser Extensions",
    "file-sharing": "File Sharing",
    "social-media": "Social Media Tools",
    "writing": "Writing",
    "video": "Video Converters",
    "github-powerhouses": "GitHub Powerhouses",
    "security": "Security",
    "vpn": "VPN",
}

# Per-category soft cap for this import (avoid blowing up huge sections)
CAPS = {
    "utilities": 400,
    "free-movies": 250,
    "free-stuff": 250,
    "ai": 200,
    "github-powerhouses": 200,
    "courses": 150,
    "free-books": 120,
    "music": 120,
    "design": 100,
    "browser-extensions": 100,
    "privacy-tools": 100,
    "browser-games": 80,
    "programming": 80,
    "file-sharing": 60,
    "video": 60,
    "writing": 60,
    "social-media": 40,
    "security": 40,
    "vpn": 30,
}


def norm_url(url: str) -> str:
    p = urlparse(url.strip().rstrip("/"))
    host = (p.netloc or "").lower().replace("www.", "")
    path = p.path.rstrip("/")
    return f"{host}{path}".lower()


def host_of(url: str) -> str:
    return urlparse(url).netloc.lower().replace("www.", "")


def should_skip(url: str, name: str) -> bool:
    if not url.startswith("http"):
        return True
    host = host_of(url)
    if any(host == s or host.endswith("." + s) for s in SKIP_HOSTS):
        return True
    # Skip pure FMHY internal reddit wiki deep-links already covered
    if "reddit.com/r/freemediaheckyeah" in url.lower():
        return True
    n = name.strip().lower()
    if n in SKIP_NAME_BITS:
        return True
    if len(n) <= 1:
        return True
    # NSFW / adult markers in URL or name
    blob = f"{url} {name}".lower()
    if any(x in blob for x in ["nsfw", "porn", "xxx", "onlyfans", "hentai-hub"]):
        return True
    return False


def clean_name(name: str) -> str:
    name = re.sub(r"\s+", " ", name).strip()
    name = name.replace("**", "").strip(" \t*-•")
    # Drop trailing descriptions after em dash sometimes baked in
    if " - " in name and len(name) > 60:
        name = name.split(" - ", 1)[0].strip()
    return name[:100]


def map_category(section: str, url: str, name: str) -> str:
    blob = f"{section} {url} {name}".lower()
    if "github.com" in blob and any(x in section.lower() for x in ["ai", "devtools", "linux", "privacy", "tools"]):
        # keep software github in topic cats when possible
        pass
    for keys, slug in SECTION_MAP:
        if any(k in section.lower() for k in keys):
            return slug
    # URL heuristics fallback
    if "github.com" in blob:
        return "github-powerhouses"
    if any(x in blob for x in ["vpn", "mullvad", "protonvpn"]):
        return "vpn"
    if any(x in blob for x in ["password", "bitwarden", "keepass", "2fa"]):
        return "security"
    if any(x in blob for x in ["ai", "gpt", "llm", "chatgpt", "claude"]):
        return "ai"
    if any(x in blob for x in ["course", "khan", "coursera", "edx"]):
        return "courses"
    return "free-stuff"


def link_html(url: str, name: str) -> str:
    domain = host_of(url)
    if domain == "github.com":
        parts = [p for p in urlparse(url).path.split("/") if p]
        owner = parts[0] if parts else "github"
        icon = fb = f"https://github.com/{owner}.png?size=64"
    else:
        icon = fb = f"https://icon.horse/icon/{domain}"
    safe = name.replace("&", "&amp;").replace("<", "&lt;")
    return (
        f' <a href="{url}" target="_blank" rel="noopener noreferrer" class="tool-link" data-pricing="free">'
        f'<img src="{icon}" data-fallback="{fb}" alt="" class="tool-link-icon">'
        f'<span class="tool-link-name">{safe}</span></a>\n'
    )


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
    marker = 'data-category="osint-username"'
    idx = html.find(marker)
    if idx != -1:
        sec = html.rfind("<section", 0, idx)
        return html[:sec] + block + html[sec:]
    m = re.search(r"</div>\s*</div>\s*</main>", html)
    if m:
        return html[: m.start()] + block + html[m.start() :]
    return html + block


def parse_fmhy(md: str) -> list[tuple[str, str, str]]:
    """Return list of (section, name, url)."""
    current = "Miscellaneous"
    out: list[tuple[str, str, str]] = []
    seen_local: set[str] = set()

    for line in md.splitlines():
        h = re.match(r"^#{1,3}\s+(.+)$", line.strip())
        if h:
            # strip decorative glyphs
            title = re.sub(r"^[^A-Za-z0-9]+", "", h.group(1)).strip()
            title = re.sub(r"\s+", " ", title)
            if title:
                current = title
            continue

        for name, url in LINK_RE.findall(line):
            name = clean_name(name)
            url = url.strip().rstrip(").,;")
            if should_skip(url, name):
                continue
            key = norm_url(url)
            if key in seen_local:
                continue
            seen_local.add(key)
            out.append((current, name, url))
    return out


def main() -> None:
    if not FMHY_PATH.exists():
        raise SystemExit(f"Missing {FMHY_PATH}. Download https://api.fmhy.net/single-page first.")

    md = FMHY_PATH.read_text(encoding="utf-8", errors="replace")
    entries = parse_fmhy(md)
    print(f"Parsed {len(entries)} FMHY links")

    html = HTML_PATH.read_text(encoding="utf-8")
    existing = {norm_url(u) for u in re.findall(r'href="(https?://[^"]+)"', html)}

    by_cat: dict[str, list[tuple[str, str]]] = {}
    skipped = 0
    for section, name, url in entries:
        if norm_url(url) in existing:
            skipped += 1
            continue
        slug = map_category(section, url, name)
        by_cat.setdefault(slug, []).append((url, name))

    added = 0
    for slug, items in sorted(by_cat.items(), key=lambda x: -len(x[1])):
        cap = CAPS.get(slug, 80)
        take = items[:cap]
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
        for url, name in take:
            if norm_url(url) in existing:
                continue
            new_links += link_html(url, name)
            existing.add(norm_url(url))
            count += 1
            added += 1
        html = html[: m.start(2)] + block + new_links + html[m.end(2) :]
        print(f"+{count:4d}/{len(items):4d} -> {slug} (cap {cap})")

    HTML_PATH.write_text(html, encoding="utf-8")
    print(f"\nAdded {added} new tools from FMHY (skipped {skipped} already present)")


if __name__ == "__main__":
    main()
