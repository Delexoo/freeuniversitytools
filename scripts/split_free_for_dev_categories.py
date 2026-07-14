"""Split free-for-dev tools into dedicated categories for easier browsing.

1. Fetch free-for-dev README
2. Map each section to its own student.html category (new when needed)
3. Move matching URLs out of overloaded buckets (utilities, etc.)
4. Insert new sections + CATEGORY_KEYWORDS
"""
from __future__ import annotations

import re
import urllib.request
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
HTML_PATH = ROOT / "student.html"
JS_PATH = ROOT / "js" / "student.js"
README_URL = "https://raw.githubusercontent.com/ripienaar/free-for-dev/master/README.md"

SECTION_RE = re.compile(
    r'(<section class="tool-category"[^>]*data-category="([^"]+)"[^>]*>)'
    r'(.*?)<div class="category-tools">(.*?)</div>(\s*</section>)',
    re.DOTALL,
)
LINK_BLOCK_RE = re.compile(
    r'(\s*<a\s+href="([^"]+)"[^>]*class="tool-link"[^>]*>.*?</a>)',
    re.DOTALL | re.IGNORECASE,
)
BULLET_RE = re.compile(
    r"^\s*\*\s+\[([^\]]+)\]\((https?://[^)\s]+)\)\s*(.*)?$",
    re.MULTILINE,
)

# One dedicated category per free-for-dev README section
SECTION_MAP: dict[str, tuple[str, str]] = {
    "Major Cloud Providers": ("cloud-providers", "Cloud Providers"),
    "Cloud management solutions": ("cloud-management", "Cloud Management"),
    "Source Code Repos": ("source-code-repos", "Source Code Repos"),
    "APIs, Data, and ML": ("api-data-ml", "APIs, Data & ML"),
    "Artifact Repos": ("artifact-repos", "Artifact Repos"),
    "Tools for Teams and Collaboration": ("team-collaboration", "Team Collaboration"),
    "CMS": ("cms", "CMS"),  # existing
    "Code Generation": ("code-generation", "Code Generation"),
    "Code Quality": ("code-quality", "Code Quality"),
    "Code Search and Browsing": ("code-search", "Code Search"),
    "CI and CD": ("ci-cd", "CI/CD"),
    "Testing": ("testing-tools", "Testing"),
    "Security and PKI": ("security-pki", "Security & PKI"),
    "Authentication, Authorization, and User Management": ("authentication", "Authentication"),
    "Mobile App Distribution and Feedback": ("mobile-distribution", "Mobile Distribution"),
    "Management System": ("management-systems", "Management Systems"),
    "Messaging and Streaming": ("messaging", "Messaging & Streaming"),
    "Log Management": ("log-management", "Log Management"),
    "Translation Management": ("translation-management", "Translation Management"),
    "Monitoring": ("monitoring", "Monitoring"),
    "Crash and Exception Handling": ("crash-reporting", "Crash Reporting"),
    "Search": ("search-tools", "Search Tools"),
    "Education and Career Development": ("dev-education", "Dev Education & Career"),
    "Email": ("email", "Email Tools"),  # existing
    "Feature Toggles Management Platforms": ("feature-flags", "Feature Flags"),
    "Font": ("fonts", "Fonts"),  # existing
    "Forms": ("forms", "Forms"),
    "Generative AI": ("generative-ai", "Generative AI"),  # existing
    "CDN and Protection": ("cdn", "CDN & Protection"),
    "PaaS": ("paas", "PaaS"),
    "BaaS": ("baas", "BaaS"),
    "Low-code Platform": ("low-code", "Low-Code Platforms"),
    "Web Hosting": ("web-hosting", "Web Hosting"),
    "DNS": ("dns", "DNS"),
    "Domain": ("domains", "Domains"),
    "IaaS": ("iaas", "IaaS"),
    "Managed Data Services": ("managed-data", "Managed Data Services"),
    "Tunneling, WebRTC, Web Socket Servers and Other Routers": ("tunneling", "Tunneling & WebRTC"),
    "Issue Tracking and Project Management": ("issue-tracking", "Issue Tracking"),
    "Storage and Media Processing": ("storage-media", "Storage & Media"),
    "Design and UI": ("design", "Design Tools"),  # existing
    "Data Visualization on Maps": ("maps", "Maps"),  # existing
    "Package Build System": ("package-build", "Package Build"),
    "IDE and Code Editing": ("code-editors", "Online Code Editors"),  # existing
    "Analytics, Events and Statistics": ("analytics", "Analytics"),
    "Visitor Session Recording": ("session-recording", "Session Recording"),
    "International Mobile Number Verification API and SDK": ("phone-apis", "Phone Number APIs"),
    "Payment and Billing Integration": ("payment-billing", "Payment & Billing"),
    "Docker Related": ("docker", "Docker"),
    "Dev Blogging Sites": ("dev-blogging", "Dev Blogging"),
    "Commenting Platforms": ("commenting", "Commenting Platforms"),
    "Screenshot APIs": ("screenshot-apis", "Screenshot APIs"),
    "Flutter Related and Building IOS Apps without Mac": ("flutter-tools", "Flutter Tools"),
    "Privacy Management": ("privacy-management", "Privacy Management"),
    "Miscellaneous": ("dev-misc", "Dev Misc Free Tiers"),
    "Remote Desktop Tools": ("remote-desktop", "Remote Desktop"),
    "Other Free Resources": ("dev-resources", "Dev Free Resources"),
}

# Prefer inserting new sections before this anchor if present
INSERT_BEFORE = "utilities"


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


def link_html(url: str, name: str, pricing: str = "free-tier") -> str:
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


def parse_readme(text: str) -> tuple[dict[str, list[tuple[str, str]]], dict[str, str]]:
    """Return (slug -> [(url, name)], slug -> title)."""
    by_slug: dict[str, list[tuple[str, str]]] = defaultdict(list)
    slug_titles: dict[str, str] = {}
    seen: set[str] = set()

    parts = re.split(r"^## ", text, flags=re.MULTILINE)
    for part in parts[1:]:
        title = part.splitlines()[0].strip()
        if title.lower() in {"table of contents", "contributing", "license"}:
            continue
        mapped = SECTION_MAP.get(title)
        if not mapped:
            continue
        slug, display = mapped
        slug_titles[slug] = display
        for name, url, note in BULLET_RE.findall(part):
            note = note or ""
            if "taken down" in note.lower():
                continue
            key = norm_url(url)
            if not key or key in seen:
                continue
            if key.startswith("github.com/ripienaar/free-for-dev"):
                continue
            host = urlparse(url).netloc.lower().replace("www.", "")
            if host in {"free-for.dev"}:
                continue
            clean = re.sub(r"\s+", " ", name.strip().replace("`", ""))[:80]
            if not clean:
                continue
            seen.add(key)
            by_slug[slug].append((url, clean))
    return by_slug, slug_titles


def extract_existing_links(html: str) -> dict[str, str]:
    """norm_url -> full <a>...</a> block"""
    out: dict[str, str] = {}
    for block, href in LINK_BLOCK_RE.findall(html):
        if not href.startswith("http"):
            continue
        key = norm_url(href)
        out.setdefault(key, block if block.startswith("\n") or block.startswith(" ") else " " + block)
    return out


def strip_urls_from_sections(html: str, urls: set[str]) -> str:
    def drop_in_section(match: re.Match[str]) -> str:
        prefix, slug, mid, tools_html, suffix = (
            match.group(1),
            match.group(2),
            match.group(3),
            match.group(4),
            match.group(5),
        )
        kept = []
        for block, href in LINK_BLOCK_RE.findall(tools_html):
            if norm_url(href) in urls:
                continue
            kept.append(block if block.startswith((" ", "\n")) else " " + block)
        return f"{prefix}{mid}<div class=\"category-tools\">{''.join(kept)}</div>{suffix}"

    return SECTION_RE.sub(drop_in_section, html)


def section_exists(html: str, slug: str) -> bool:
    return f'data-category="{slug}"' in html


def build_section(slug: str, title: str, links: list[str]) -> str:
    body = "".join(links)
    return (
        f'\n <section class="tool-category" data-category="{slug}">\n'
        f' <h3 class="category-title">{title}</h3>\n'
        f' <div class="category-tools">\n'
        f"{body}"
        f" </div>\n"
        f" </section>\n"
    )


def append_to_section(html: str, slug: str, links: list[str]) -> str:
    pattern = re.compile(
        rf'(<section class="tool-category"[^>]*data-category="{re.escape(slug)}"'
        rf'[^>]*>.*?<div class="category-tools">)(.*?)(</div>\s*</section>)',
        re.DOTALL,
    )

    def repl(m: re.Match[str]) -> str:
        return f"{m.group(1)}{m.group(2)}{''.join(links)}{m.group(3)}"

    new_html, n = pattern.subn(repl, html, count=1)
    if not n:
        raise SystemExit(f"Could not append to section {slug}")
    return new_html


def insert_sections(html: str, sections_html: str) -> str:
    marker = f'data-category="{INSERT_BEFORE}"'
    idx = html.find(marker)
    if idx == -1:
        # append before OSINT or at end of directory
        idx = html.find('data-category="osint-tools"')
    if idx == -1:
        raise SystemExit("Could not find insertion point")
    start = html.rfind("<section", 0, idx)
    return html[:start] + sections_html + html[start:]


def keyword_list(title: str, slug: str) -> list[str]:
    words = [slug.replace("-", " "), title.lower()]
    extras = {
        "ci-cd": ["ci", "cd", "continuous integration", "github actions", "circleci"],
        "monitoring": ["uptime", "apm", "observability", "status page"],
        "paas": ["heroku", "render", "paas", "platform as a service"],
        "baas": ["firebase", "supabase", "backend as a service", "baas"],
        "forms": ["form builder", "typeform", "google forms alternative"],
        "authentication": ["oauth", "sso", "auth0", "login", "identity"],
        "analytics": ["analytics", "telemetry", "events", "metrics"],
        "dns": ["dns", "nameserver", "cloudflare dns"],
        "cdn": ["cdn", "cloudflare", "fastly"],
        "docker": ["docker", "container registry"],
        "api-data-ml": ["api", "machine learning", "ml api", "free api"],
        "cloud-providers": ["aws", "azure", "gcp", "oracle cloud", "free tier"],
    }
    words.extend(extras.get(slug, []))
    # uniq preserve order
    seen = set()
    out = []
    for w in words:
        w = w.strip()
        if w and w not in seen:
            seen.add(w)
            out.append(w)
    return out[:12]


def patch_keywords(js: str, slug_titles: dict[str, str], new_slugs: list[str]) -> str:
    # Find CATEGORY_KEYWORDS opening
    start = js.find("const CATEGORY_KEYWORDS = {")
    if start == -1:
        raise SystemExit("CATEGORY_KEYWORDS not found")
    # Insert after opening brace
    insert_at = js.find("{", start) + 1
    blocks = []
    for slug in sorted(new_slugs):
        if f"{slug}:" in js or f'"{slug}"' in js or f"'{slug}'" in js:
            # already has key — skip adding full block
            continue
        title = slug_titles[slug]
        kws = keyword_list(title, slug)
        inner = ",\n    ".join(f'"{w}"' for w in kws)
        blocks.append(f'\n  "{slug}": [\n    {inner},\n  ],')
    if not blocks:
        return js
    return js[:insert_at] + "".join(blocks) + js[insert_at:]


def fix_cloud_title(html: str) -> str:
    """cloud section was titled File Sharing — rename to Cloud."""
    pattern = re.compile(
        r'(data-category="cloud"[^>]*>\s*<h3 class="category-title">)[^<]*(</h3>)',
        re.DOTALL,
    )
    return pattern.sub(r"\1Cloud\2", html, count=1)


def main() -> None:
    print("Fetching free-for-dev README…")
    readme = fetch_readme()
    by_slug, slug_titles = parse_readme(readme)
    print(f"Parsed tools into {len(by_slug)} dedicated categories")

    html = HTML_PATH.read_text(encoding="utf-8")
    existing_links = extract_existing_links(html)
    print(f"Existing link blocks indexed: {len(existing_links)}")

    # Collect all URLs that belong in dedicated free-for-dev categories
    move_urls: set[str] = set()
    planned: dict[str, list[tuple[str, str]]] = {}
    for slug, entries in by_slug.items():
        planned[slug] = entries
        for url, _name in entries:
            move_urls.add(norm_url(url))

    print(f"URLs to place into dedicated categories: {len(move_urls)}")

    # Strip those URLs from wherever they currently sit (avoid duplicates)
    html = strip_urls_from_sections(html, move_urls)

    new_section_html = []
    appends: dict[str, list[str]] = defaultdict(list)
    created = 0
    reused = 0
    built = 0

    for slug, entries in sorted(planned.items(), key=lambda x: slug_titles.get(x[0], x[0])):
        title = slug_titles[slug]
        links = []
        for url, name in entries:
            key = norm_url(url)
            block = existing_links.get(key)
            if block:
                # normalize leading whitespace
                block = block if block.startswith((" ", "\n")) else " " + block
                # ensure pricing free-tier for free-for-dev if missing — leave as-is
                links.append(block.rstrip("\n") + "\n")
            else:
                links.append(link_html(url, name))
            built += 1

        if not links:
            continue

        if section_exists(html, slug):
            appends[slug].extend(links)
            reused += 1
            continue

        new_section_html.append(build_section(slug, title, links))
        created += 1

    # Append into existing sections first
    for slug, links in appends.items():
        html = append_to_section(html, slug, links)

    if new_section_html:
        html = insert_sections(html, "".join(new_section_html))

    html = fix_cloud_title(html)
    HTML_PATH.write_text(html, encoding="utf-8", newline="\n")

    # Keywords for newly created slugs
    new_slugs = [s for s, _ in SECTION_MAP.values() if f'"{s}"' not in JS_PATH.read_text(encoding="utf-8") and f"{s}:" not in JS_PATH.read_text(encoding="utf-8")]
    # simpler: all slugs from SECTION_MAP that need keywords
    js = JS_PATH.read_text(encoding="utf-8")
    need = []
    for slug, title in SECTION_MAP.values():
        # detect existing key loosely
        if re.search(rf'["\']?{re.escape(slug)}["\']?\s*:', js):
            continue
        need.append(slug)
        slug_titles.setdefault(slug, title)
    if need:
        js = patch_keywords(js, {s: slug_titles[s] for s in need}, need)
        JS_PATH.write_text(js, encoding="utf-8", newline="\n")
        print(f"Added keywords for {len(need)} new categories")

    print(f"Tools placed: {built}")
    print(f"New sections created: {created}")
    print(f"Existing sections reused: {reused}")
    print("Done.")


if __name__ == "__main__":
    main()
