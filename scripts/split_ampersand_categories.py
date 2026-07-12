"""Split combined 'X & Y' (and similar) categories into dedicated categories."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HTML_PATH = ROOT / "student.html"

SECTION_RE = re.compile(
    r'(<section class="tool-category"[^>]*data-category="([^"]+)"[^>]*>)'
    r'.*?<h3 class="category-title">([^<]*)</h3>.*?'
    r'(<div class="category-tools">)(.*?)(</div>\s*</section>)',
    re.DOTALL,
)
LINK_RE = re.compile(
    r'(<a\s+href="[^"]+"[^>]*>.*?<span class="tool-link-name">[^<]*</span></a>)',
    re.DOTALL,
)
LINK_META_RE = re.compile(
    r'href="([^"]+)".*?<span class="tool-link-name">([^<]*)</span>',
    re.DOTALL,
)

# old_slug -> list of (new_slug, new_title, keyword hints for bucket 1; empty = default bucket)
SPLITS: dict[str, list[tuple[str, str, list[str]]]] = {
    "stock-video-audio": [
        ("stock-video", "Stock Video", ["video", "coverr", "mixkit", "videvo", "videezy", "storyblocks"]),
        ("stock-audio", "Stock Audio", ["audio", "sound", "freesound"]),
    ],
    "osint-images-videos-docs": [
        (
            "osint-image-search",
            "Image Search",
            ["image", "photo", "face", "pic", "flickr", "imgur", "reverse", "saucenao", "pimeyes", "lenso", "camfind"],
        ),
        (
            "osint-video-search",
            "Video Search",
            ["video", "youtube", "vimeo", "tiktok", "reel", "clip", "footage"],
        ),
        (
            "osint-document-search",
            "Document Search",
            ["doc", "pdf", "slide", "archive", "scribd", "issuu", "paper", "text", "book"],
        ),
    ],
    "osint-compliance-risk-intelligence": [
        ("osint-compliance", "Compliance Search", ["compliance", "sanction", "ofac", "pep", "aml", "kyc", "regulat"]),
        ("osint-risk-intelligence", "Risk Intelligence", ["risk", "threat", "fraud", "watchlist", "adverse", "intel"]),
    ],
    "osint-transportation": [
        ("osint-vehicle-search", "Vehicle Search", ["vehicle", "car", "vin", "plate", "auto", "motor"]),
        ("osint-transport-search", "Transport Search", ["transport", "flight", "ship", "rail", "maritime", "aviation", "train"]),
    ],
    "osint-geolocation-tools-maps": [
        ("osint-maps-search", "Maps Search", ["map", "street", "satellite", "openstreetmap", "google.com/maps"]),
        ("osint-location-search", "Location Search", ["location", "geo", "gps", "coordinate", "geolocation", "ip"]),
    ],
    "osint-online-communities": [
        ("osint-forum-search", "Forum Search", ["forum", "board", "thread", "reddit", "4chan", "discourse"]),
        ("osint-community-search", "Community Search", ["community", "group", "discord", "slack", "telegram"]),
    ],
    "osint-disinformation-media-verification": [
        ("osint-fact-check", "Fact-Check Tools", ["fact", "verify", "misinfo", "disinfo", "hoax", "snopes", "politifact"]),
        ("osint-media-verification", "Media Verification", ["media", "image", "video", "reverse", "metadata", "forensic"]),
    ],
    "osint-encoding-decoding": [
        ("osint-encoding", "Encoding Tools", ["encode", "encoder", "base64", "hash", "cipher"]),
        ("osint-decoding", "Decoding Tools", ["decode", "decoder", "decrypt", "dehash"]),
    ],
    "osint-malicious-file-analysis": [
        ("osint-malware-analysis", "Malware Analysis", ["malware", "virus", "sandbox", "hybrid", "any.run", "virustotal"]),
        ("osint-file-analysis", "File Analysis", ["file", "hash", "metadata", "forensic", "pdf", "pe ", "elf"]),
    ],
    "osint-opsec": [
        ("osint-privacy-tools", "Privacy Tools", ["privacy", "vpn", "tor", "anonymous", "encrypt", "signal"]),
        ("osint-safety-tools", "Safety Tools", ["safety", "secure", "protect", "breach", "password", "2fa", "monitor"]),
    ],
}


def score_bucket(text: str, patterns: list[str]) -> int:
    t = text.lower()
    return sum(1 for p in patterns if p in t)


def assign_bucket(url: str, name: str, buckets: list[tuple[str, str, list[str]]]) -> tuple[str, str]:
    text = f"{url} {name}"
    best = buckets[0]
    best_score = -1
    for bucket in buckets:
        slug, title, patterns = bucket
        s = score_bucket(text, patterns)
        if s > best_score:
            best_score = s
            best = bucket
    return best[0], best[1]


def section_block(slug: str, title: str, links: list[str]) -> str:
    body = "".join(links)
    return (
        f' <section class="tool-category" data-category="{slug}">\n'
        f' <h3 class="category-title">{title}</h3>\n'
        f' <div class="category-tools">\n'
        f"{body}"
        f" </div>\n"
        f" </section>\n"
    )


def main() -> None:
    html = HTML_PATH.read_text(encoding="utf-8")
    changes = 0

    for old_slug, buckets in SPLITS.items():
        pattern = re.compile(
            r'(<section class="tool-category"[^>]*data-category="'
            + re.escape(old_slug)
            + r'"[^>]*>)'
            r'.*?<h3 class="category-title">([^<]*)</h3>.*?'
            r'(<div class="category-tools">)(.*?)(</div>\s*</section>)',
            re.DOTALL,
        )
        m = pattern.search(html)
        if not m:
            print(f"SKIP (not found): {old_slug}")
            continue

        title = m.group(2)
        if "&" not in title and old_slug != "stock-video-audio":
            print(f"SKIP (already split): {old_slug}")
            continue

        links = LINK_RE.findall(m.group(4))
        grouped: dict[str, list[str]] = {}
        titles: dict[str, str] = {}
        for link_html in links:
            meta = LINK_META_RE.search(link_html)
            if not meta:
                continue
            slug, t = assign_bucket(meta.group(1), meta.group(2), buckets)
            grouped.setdefault(slug, []).append(link_html)
            titles[slug] = t

        replacement = ""
        for slug, t, _ in buckets:
            if grouped.get(slug):
                replacement += section_block(slug, t, grouped[slug])

        html = html[: m.start()] + replacement + html[m.end() :]
        changes += 1
        print(f"SPLIT '{old_slug}' -> {[b[0] for b in buckets if grouped.get(b[0])]}")

    if changes:
        HTML_PATH.write_text(html, encoding="utf-8")
        print(f"\nDone. Applied {changes} ampersand splits.")
    else:
        print("No changes made.")


if __name__ == "__main__":
    main()
