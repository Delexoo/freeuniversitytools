"""Build compact tools index for scroll.html from student.html."""
import json
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
HTML_PATH = ROOT / "student.html"
OUT_PATH = ROOT / "data" / "scroll-tools.json"

LINK_RE = re.compile(
    r'<a\s+href="([^"]+)"[^>]*class="tool-link"[^>]*data-pricing="([^"]*)"[^>]*>'
    r'(?:.*?<img[^>]*src="([^"]*)"[^>]*data-fallback="([^"]*)"[^>]*)?'
    r'.*?<span class="tool-link-name">([^<]*)</span>',
    re.DOTALL | re.IGNORECASE,
)

SECTION_RE = re.compile(
    r'<section class="tool-category" data-category="([^"]+)">.*?'
    r'<h3 class="category-title">([^<]*)</h3>.*?'
    r'<div class="category-tools">(.*?)</div>\s*</section>',
    re.DOTALL,
)

CATEGORY_BLURBS = {
    "must-try": "Standout pick from the directory, worth trying first.",
    "github-powerhouses": "Popular open-source project on GitHub for learning and building.",
    "free-books": "Find free textbooks, PDFs, and ebooks for coursework and reading.",
    "courses": "Courses, tutorials, and learning platforms for self-paced study.",
    "study": "Study aids: flashcards, notes, quizzes, and exam prep.",
    "ai": "AI assistant or chat tool for questions, writing, and productivity.",
    "ai-study-tools": "AI-powered homework help, quizzes, and study workflows.",
    "research": "Research and lookup tools for papers, sources, and deep answers.",
    "essay-tools": "Writing, citations, grammar, and essay workflow tools.",
    "free-movies": "Streaming and media sites for movies, shows, and entertainment.",
    "free-stuff": "Free resources, alternatives, and discovery hubs for students.",
    "design": "Design, UI, fonts, and creative tools for projects and portfolios.",
    "programming": "Coding references, docs, practice, and developer utilities.",
    "programming-ai": "AI coding assistants, completions, and dev-focused AI tools.",
    "pdf": "PDF viewing, editing, conversion, and document utilities.",
    "utilities": "Handy everyday utilities: converters, helpers, and small tools.",
    "productivity": "Productivity apps for focus, planning, and getting work done.",
    "security": "Security, privacy, and safety tools for your accounts and devices.",
    "open-source": "Open-source software discovery and FOSS community resources.",
    "chrome-extension": "Browser extensions that add features inside Chrome.",
    "browser-extensions": "Browser add-ons for privacy, media, and productivity.",
    "cloud": "File sharing, storage, and sync for documents and media.",
    "generative-ai": "Generative AI for images, audio, video, and creative output.",
    "local-ai": "Run or chat with AI models locally on your own machine.",
    "osint-tools": "Open-source intelligence and online research utilities.",
    "osint-geolocation-tools-maps": "Maps, geolocation, and place-based research tools.",
    "osint-email-address": "Email lookup, verification, and breach-check tools.",
    "osint-username": "Username and account search across websites and platforms.",
    "osint-domain-name": "Domain, DNS, and website investigation tools.",
    "osint-cyber-threat-intelligence": "Threat feeds, malware intel, and security monitoring.",
    "osint-ai-tools": "AI tools built for investigation, ads, and OSINT workflows.",
}

PRICING_INTRO = {
    "free": "Free to use",
    "free-tier": "Free tier available",
    "limited": "Limited free access",
    "paid": "Paid service",
}

BAD_TOOL_NAMES = {
    "\u2014",
    "\u2013",
    "-",
    "\u2013",
    "–",
    "—",
    "",
}


def is_bad_name(name: str) -> bool:
    value = name.strip()
    if not value or value in BAD_TOOL_NAMES:
        return True
    stripped = value.replace(" ", "")
    if stripped and all(c in BAD_TOOL_NAMES or c.isspace() for c in value):
        return True
    return False


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


def make_blurb(name: str, cat_slug: str, cat_title: str, pricing: str, url: str, domain: str) -> str:
    if cat_slug in CATEGORY_BLURBS:
        return CATEGORY_BLURBS[cat_slug]

    intro = PRICING_INTRO.get(pricing, "Free to use")
    title = cat_title.strip().lower() or "student tools"

    if "github.com" in url.lower():
        return f"{intro}, open-source project under {cat_title}. Explore repos, docs, and releases on GitHub."

    if cat_slug.startswith("osint-"):
        return f"{intro}, research tool for {title}. Useful for online lookup and investigation."

    return f"{intro} for {title}. Core functions live at {domain}."


def main():
    html = HTML_PATH.read_text(encoding="utf-8")
    tools = []
    seen: set[str] = set()

    for cat_slug, cat_title, block in SECTION_RE.findall(html):
        for href, pricing, icon, fallback, name in LINK_RE.findall(block):
            href = href.strip()
            if not href.startswith("http"):
                continue
            key = norm_url(href)
            if key in seen:
                continue
            seen.add(key)
            clean_name = name.strip() or domain_of(href)
            if is_bad_name(clean_name):
                continue
            domain = domain_of(href)
            tools.append(
                {
                    "id": key,
                    "n": clean_name,
                    "u": href,
                    "i": icon or f"https://icon.horse/icon/{domain}",
                    "f": fallback or f"https://icon.horse/icon/{domain}",
                    "p": pricing or "free",
                    "c": cat_title.strip(),
                    "s": cat_slug,
                    "d": domain,
                    "x": make_blurb(clean_name, cat_slug, cat_title, pricing or "free", href, domain),
                }
            )

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(tools, separators=(",", ":")), encoding="utf-8")
    print(f"Wrote {len(tools)} tools to {OUT_PATH}")


if __name__ == "__main__":
    main()
