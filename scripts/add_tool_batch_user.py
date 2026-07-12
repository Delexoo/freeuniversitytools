"""Add user-requested tools and OSINT4ALL directory tools."""
import json
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
HTML_PATH = ROOT / "student.html"
JS_PATH = ROOT / "js" / "student.js"
OSINT4ALL_JSON = ROOT / "scripts" / "osint4all_tools.json"

SECTION_RE = re.compile(
    r'(<section class="tool-category" data-category="([^"]+)">.*?<div class="category-tools">)(.*?)(</div>\s*</section>)',
    re.DOTALL,
)
HREF_RE = re.compile(r'href="([^"]+)"')

# (url, name, pricing)
PRIMARY = {
    "osint-geolocation-tools-maps": [
        ("https://oceanir.ai/", "Oceanir", "free-tier"),
        ("https://oceanir.ai/geospy-alternative", "Oceanir GeoSpy Alt", "free-tier"),
    ],
    "osint-cloud-infrastructure": [
        ("https://grayhatwarfare.com/", "Grayhat Warfare", "free-tier"),
        ("https://shorteners.grayhatwarfare.com/", "Grayhat Shorteners", "free-tier"),
    ],
    "security": [
        ("https://cybermap.kaspersky.com/", "Kaspersky Cybermap", "free"),
    ],
    "programming": [
        ("https://free-for.dev/", "Free for Dev", "free"),
        ("https://github.com/ripienaar/free-for-dev", "Free for Dev GitHub", "free"),
    ],
    "programming-ai": [
        (
            "https://github.com/Mahanaicoach/google-maps-scraper-kit",
            "Google Maps Scraper Kit",
            "free",
        ),
        ("https://github.com/gosom/google-maps-scraper", "gosom Google Maps Scraper", "free"),
    ],
    "design": [
        ("https://font-tester.foxcraft.tech/", "Font Tester", "free-tier"),
    ],
    "free-movies": [
        ("https://cinevice.net/", "CineVice", "free"),
    ],
    "osint-email-address": [
        ("https://behindtheemail.com/", "Behind the Email", "free-tier"),
    ],
    "ai": [
        ("https://arena.ai/", "Arena AI", "free-tier"),
        ("https://lmarena.ai/", "LMArena", "free-tier"),
    ],
    "osint-search-engines": [
        ("https://osint4all.com/", "OSINT4ALL", "free"),
        ("https://start.me/p/L1rEYQ/osint4all", "OSINT4ALL Start.me", "free"),
    ],
    "osint-compliance-risk-intelligence": [
        ("https://www.worldmonitor.app/", "World Monitor", "free"),
        ("https://tech.worldmonitor.app/", "Tech Monitor", "free"),
        ("https://finance.worldmonitor.app/", "Finance Monitor", "free"),
        ("https://commodity.worldmonitor.app/", "Commodity Monitor", "free"),
        ("https://energy.worldmonitor.app/", "Energy Monitor", "free"),
        ("https://github.com/koala73/worldmonitor", "World Monitor GitHub", "free"),
    ],
}

# Extra tools discovered while visiting the pages above
DISCOVERED = {
    "osint-geolocation-tools-maps": [
        ("https://mapchecking.com/", "MapChecking", "free"),
        ("https://www.globalforestwatch.org/", "Global Forest Watch", "free"),
        ("https://dataspace.copernicus.eu/", "Copernicus Data Space", "free"),
        ("https://worldview.earthdata.nasa.gov/", "NASA Worldview", "free"),
        ("https://www.geonames.org/", "GeoNames", "free"),
    ],
    "osint-transportation": [
        ("https://opensky-network.org/", "OpenSky Network", "free"),
    ],
    "osint-domain-name": [
        ("https://fullhunt.io/", "FullHunt", "free-tier"),
    ],
    "osint-blockchain-cryptocurrency": [
        ("https://www.chainabuse.com/", "Chainabuse", "free"),
    ],
    "osint-business-records": [
        ("https://search.gleif.org/", "GLEIF LEI Search", "free"),
        ("https://www.linkedin.com/ad-library/", "LinkedIn Ad Library", "free"),
        ("https://adstransparency.google.com/", "Google Ads Transparency", "free"),
        ("https://library.tiktok.com/ads/", "TikTok Ad Library", "free"),
    ],
    "osint-disinformation-media-verification": [
        ("https://acleddata.com/", "ACLED", "free-tier"),
    ],
    "github-powerhouses": [
        ("https://github.com/openrefine/openrefine", "OpenRefine", "free"),
        ("https://github.com/MISP/MISP", "MISP", "free"),
        ("https://github.com/sherlock-project/sherlock", "Sherlock", "free"),
        ("https://github.com/nmap/nmap", "Nmap", "free"),
    ],
}

OSINT_ROUTE = {
    "email": "osint-email-address",
    "domain": "osint-domain-name",
    "dns": "osint-domain-name",
    "ip": "osint-ip-mac-address",
    "geolocation": "osint-geolocation-tools-maps",
    "map": "osint-geolocation-tools-maps",
    "satellite": "osint-geolocation-tools-maps",
    "social": "osint-social-networks",
    "people": "osint-people-search-engines",
    "phone": "osint-telephone-numbers",
    "archive": "osint-archives",
    "threat": "osint-compliance-risk-intelligence",
    "crypto": "osint-blockchain-cryptocurrency",
    "company": "osint-business-records",
    "transport": "osint-transportation",
    "image": "osint-images-videos-docs",
    "search": "osint-search-engines",
}

KEYWORD_PATCHES = {
    "osint-geolocation-tools-maps": ["oceanir", "geospy", "mapchecking", "global forest watch"],
    "osint-cloud-infrastructure": ["grayhat", "grayhatwarfare", "public buckets"],
    "security": ["kaspersky", "cybermap", "cyberthreat"],
    "programming": ["free for dev", "free-for.dev", "developer tiers"],
    "design": ["font tester", "typography", "google fonts preview"],
    "free-movies": ["cinevice", "streaming"],
    "osint-email-address": ["behind the email", "email osint"],
    "ai": ["arena ai", "lmarena", "llm leaderboard"],
    "osint-search-engines": ["osint4all", "osint directory"],
    "osint-compliance-risk-intelligence": ["world monitor", "global intelligence"],
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


def route_osint_tool(name: str, url: str) -> str:
    blob = f"{name} {url}".lower()
    for key, cat in OSINT_ROUTE.items():
        if key in blob:
            return cat
    return "osint-search-engines"


def load_osint4all() -> dict[str, list[tuple[str, str, str]]]:
    if not OSINT4ALL_JSON.exists():
        return {}
    data = json.loads(OSINT4ALL_JSON.read_text(encoding="utf-8"))
    by_cat: dict[str, list[tuple[str, str, str]]] = {}
    for item in data:
        url = item.get("url", "")
        name = item.get("name", "OSINT Tool")
        if not url:
            continue
        cat = item.get("category") or route_osint_tool(name, url)
        by_cat.setdefault(cat, []).append((url, name, "free"))
    return by_cat


def merge_additions() -> dict[str, list[tuple[str, str, str]]]:
    merged: dict[str, list[tuple[str, str, str]]] = {}
    for source in (PRIMARY, DISCOVERED, load_osint4all()):
        for cat, items in source.items():
            merged.setdefault(cat, []).extend(items)
    return merged


def patch_keywords(js_text: str) -> str:
    for cat_id, words in KEYWORD_PATCHES.items():
        key = f'"{cat_id}"' if f'"{cat_id}"' in js_text else f"'{cat_id}'"
        pattern = rf"({re.escape(key)}:\s*\[)([^\]]*)(\],)"
        match = re.search(pattern, js_text)
        if not match:
            continue
        existing = match.group(2)
        additions = []
        for word in words:
            if f'"{word}"' in existing or f"'{word}'" in existing:
                continue
            additions.append(f'"{word}"')
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
    additions = merge_additions()
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
        for url, name, pricing in additions[cat]:
            key = norm_url(url)
            if key in known:
                skipped += 1
                continue
            known.add(key)
            new_links.append(link(url, name, pricing))
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

    print(json.dumps({"added": added, "skipped": skipped, "by_category": added_by_cat}, indent=2))


if __name__ == "__main__":
    main()
