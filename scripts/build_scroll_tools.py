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

AI_NAME_RE = re.compile(
    r"(?<![a-z0-9])(ai|a\.i\.|gpt|llm|chatgpt|claude|gemini|ollama|midjourney|"
    r"stable[\s-]?diffusion|copilot|langchain|huggingface|hugging\s?face|"
    r"perplexity|deepseek|groq|anthropic|openai)(?![a-z0-9])",
    re.I,
)

KNOWN_AI_DOMAINS = {
    "openai.com",
    "chatgpt.com",
    "claude.ai",
    "anthropic.com",
    "gemini.google.com",
    "aistudio.google.com",
    "perplexity.ai",
    "mistral.ai",
    "cohere.com",
    "groq.com",
    "x.ai",
    "deepseek.com",
    "huggingface.co",
    "character.ai",
    "poe.com",
    "you.com",
    "phind.com",
    "chat.openai.com",
    "copilot.microsoft.com",
    "notebooklm.google.com",
    "bard.google.com",
    "pi.ai",
    "meta.ai",
    "together.ai",
    "replicate.com",
    "runwayml.com",
    "midjourney.com",
    "leonardo.ai",
    "firefly.adobe.com",
    "suno.com",
    "udio.com",
    "elevenlabs.io",
    "heygen.com",
    "synthesia.io",
    "jasper.ai",
    "writesonic.com",
    "copy.ai",
    "cursor.com",
    "cursor.sh",
    "tabnine.com",
    "codeium.com",
    "continue.dev",
    "lmstudio.ai",
    "ollama.com",
    "chatpdf.com",
    "consensus.app",
    "elicit.com",
    "scite.ai",
    "researchrabbit.ai",
    "uncensored.chat",
    "uncensored.ai",
    "eye2.ai",
    "cluely.com",
    "magichour.ai",
    "neevo.ai",
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


def is_ai_slug(slug: str) -> bool:
    return "ai" in slug.lower().split("-")


def is_ai_tool(name: str, url: str, domain: str, slug: str, title: str) -> bool:
    d = (domain or "").lower()
    u = (url or "").lower()
    n = name or ""
    t = title or ""

    if is_ai_slug(slug):
        return True
    if d in KNOWN_AI_DOMAINS:
        return True
    if d.endswith(".ai") or ".ai." in d:
        return True
    if AI_NAME_RE.search(n):
        return True
    title_l = t.lower()
    if "(ai)" in title_l or title_l.startswith("ai ") or " ai " in f" {title_l} ":
        return True
    if "/ai/" in u or u.rstrip("/").endswith("/ai"):
        return True
    return False


def classify_kind(name: str, url: str, domain: str, slug: str, title: str) -> str:
    """Return tool kind: ai | extension | app | github | website."""
    u = (url or "").lower()
    d = (domain or "").lower()
    s = (slug or "").lower()

    if (
        "chromewebstore.google.com" in u
        or "addons.mozilla.org" in u
        or "microsoftedge.microsoft.com/addons" in u
        or "addons.opera.com" in u
        or s in {"chrome-extension", "browser-extensions", "firefox-extensions", "extensions"}
        or "extension" in s
    ):
        return "extension"

    if (
        "play.google.com" in u
        or "apps.apple.com" in u
        or "apps.microsoft.com" in u
        or "microsoft.com/store" in u
        or "microsoft.com/en-us/p/" in u
        or s in {"android-apps", "ios-apps", "mobile-apps", "desktop-apps"}
    ):
        return "app"

    if is_ai_tool(name, url, domain, slug, title):
        return "ai"

    if d == "github.com" or d.endswith(".github.io") or s == "github-powerhouses":
        return "github"

    return "website"


KNOWN_BLURBS = {
    "eye2.ai": "Compare replies from multiple AI models side by side",
    "vocalremover.org": "Separate vocals and instrumentals from any song",
    "uncensored.chat": "Unfiltered AI chat with fewer content limits",
    "uncensored.ai": "Unfiltered AI chat with fewer content limits",
    "cluely.com": "Live AI helper that can see your screen and meetings",
    "freebuff.com": "Curated free tools and student-friendly resources",
    "app.emergent.sh": "Build apps faster with an AI coding workspace",
    "emergent.sh": "Build apps faster with an AI coding workspace",
    "chromewebstore.google.com/detail/egmgebeelgaakhaoodlmnimbfemfgdah": "Chrome extension that blocks sneaky page redirects",
    "mistral.ai": "Open-weight AI models and chat for writing and code",
    "cohere.com": "Enterprise AI chat, search, and language models",
    "ollama.com": "Run large language models locally on your machine",
    "chatgpt.com": "OpenAI chatbot for writing, coding, and questions",
    "openai.com": "OpenAI platform for GPT chat, APIs, and tools",
    "claude.ai": "Anthropic AI assistant for writing, analysis, and code",
    "perplexity.ai": "AI search engine that answers with cited sources",
    "gemini.google.com": "Google AI chat for multimodal Q&A and drafting",
    "huggingface.co": "Models, datasets, and demos for machine learning",
    "github.com": "Host and explore open-source code repositories",
}

SHORT_CAT = {
    "must-try": "featured student pick",
    "github-powerhouses": "popular open-source project",
    "free-books": "free books and textbooks",
    "courses": "courses and tutorials",
    "study": "study and exam prep",
    "ai": "AI chat and assistants",
    "ai-study-tools": "AI study help",
    "research": "research and lookup",
    "essay-tools": "writing and essays",
    "free-movies": "movies and streaming",
    "free-stuff": "free resources hub",
    "design": "design and creative work",
    "programming": "coding and development",
    "programming-ai": "AI coding help",
    "pdf": "PDF editing and conversion",
    "utilities": "everyday utility",
    "productivity": "productivity and focus",
    "security": "security and privacy",
    "browser-extensions": "browser extension",
    "chrome-extension": "Chrome extension",
    "generative-ai": "generative AI creation",
    "local-ai": "local AI models",
    "file-sharing": "file sharing",
    "music": "music streaming or download",
    "video": "video tools",
    "writing": "writing tools",
    "vpn": "VPN and private browsing",
    "privacy-tools": "privacy protection",
}


def brief(text: str, max_len: int = 78) -> str:
    text = re.sub(r"\s+", " ", (text or "").strip())
    text = text.strip(" .")
    if not text:
        return ""
    if len(text) <= max_len:
        return text
    cut = text[: max_len - 1].rsplit(" ", 1)[0].rstrip(".,;:")
    return (cut or text[: max_len - 1]) + "…"


def load_external_blurbs() -> dict[str, str]:
    out: dict[str, str] = {}
    path = ROOT / "data" / "nosignups-tools.json"
    if not path.exists():
        return out
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return out
    for tool in data.get("tools") or []:
        desc = (tool.get("description") or "").strip()
        url = (tool.get("url") or "").strip()
        if not desc or not url:
            continue
        short = brief(desc)
        out[norm_url(url)] = short
        d = domain_of(url)
        if d and d not in out:
            out[d] = short
    return out


def topic_phrase(cat_slug: str, cat_title: str) -> str:
    if cat_slug in SHORT_CAT:
        return SHORT_CAT[cat_slug]
    title = re.sub(r"\s*\([^)]*\)\s*", " ", cat_title or "")
    title = re.sub(r"[!]+$", "", title).strip().lower()
    title = re.sub(r"\s+", " ", title)
    return title or "student tools"


def blurb_from_name(name: str, kind: str, cat_slug: str, cat_title: str) -> str | None:
    n = (name or "").strip()
    nl = n.lower()
    topic = topic_phrase(cat_slug, cat_title)

    patterns = [
        (r"^(.+?)\s+remover$", lambda m: f"Remove {m.group(1)} from audio or files online"),
        (r"^(.+?)\s+converter$", lambda m: f"Convert {m.group(1)} files and formats online"),
        (r"^(.+?)\s+blocker$", lambda m: f"Block {m.group(1)} and unwanted redirects"),
        (r"^(.+?)\s+generator$", lambda m: f"Generate {m.group(1)} quickly in your browser"),
        (r"^(.+?)\s+editor$", lambda m: f"Edit {m.group(1)} online without installing software"),
        (r"^(.+?)\s+downloader$", lambda m: f"Download {m.group(1)} from the web"),
        (r"^(.+?)\s+compressor$", lambda m: f"Compress {m.group(1)} files to smaller sizes"),
        (r"^(.+?)\s+checker$", lambda m: f"Check {m.group(1)} quickly and clearly"),
        (r"^(.+?)\s+tracker$", lambda m: f"Track {m.group(1)} for school and projects"),
        (r"^(.+?)\s+calculator$", lambda m: f"Calculate {m.group(1)} with a simple online tool"),
        (r"^(.+?)\s+translator$", lambda m: f"Translate {m.group(1)} between languages"),
        (r"^compare\s+(.+)$", lambda m: f"Compare {m.group(1)} side by side"),
    ]
    for pat, fn in patterns:
        m = re.match(pat, nl, re.I)
        if m:
            return brief(fn(m))

    if "pdf" in nl:
        return brief(f"PDF tool for viewing, editing, or converting documents")
    if any(w in nl for w in ("vpn", "proxy")):
        return brief("Browse privately with VPN or proxy protection")
    if any(w in nl for w in ("note", "notepad", "notebook")):
        return brief("Take and organize notes for class and projects")
    if "flashcard" in nl or "anki" in nl:
        return brief("Study with flashcards and spaced repetition")
    if "grammar" in nl:
        return brief("Check grammar and polish writing before you submit")
    if "citation" in nl or "bibliograph" in nl:
        return brief("Build citations and bibliographies for papers")
    if kind == "extension":
        return brief(f"Browser extension for {topic}")
    if kind == "ai":
        return brief(f"AI tool for {topic}")
    if kind == "app":
        return brief(f"Installable app for {topic}")
    if kind == "github":
        return brief(f"Open-source {topic} on GitHub")
    return None


def make_blurb(
    name: str,
    cat_slug: str,
    cat_title: str,
    pricing: str,
    url: str,
    domain: str,
    kind: str,
    external: dict[str, str] | None = None,
) -> str:
    key = norm_url(url)
    external = external or {}

    if key in KNOWN_BLURBS:
        return brief(KNOWN_BLURBS[key])
    if domain in KNOWN_BLURBS:
        return brief(KNOWN_BLURBS[domain])
    if key in external:
        return external[key]
    if domain in external:
        return external[domain]

    from_name = blurb_from_name(name, kind, cat_slug, cat_title)
    if from_name:
        return from_name

    topic = topic_phrase(cat_slug, cat_title)
    if kind == "ai":
        return brief(f"AI-powered {topic}")
    if kind == "extension":
        return brief(f"Browser add-on for {topic}")
    if kind == "app":
        return brief(f"Mobile or desktop app for {topic}")
    if kind == "github":
        return brief(f"Open-source {topic} repository")
    return brief(f"Web tool for {topic}")


def main():
    html = HTML_PATH.read_text(encoding="utf-8")
    tools = []
    seen: set[str] = set()
    kind_counts: dict[str, int] = {}
    external = load_external_blurbs()

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
            kind = classify_kind(clean_name, href, domain, cat_slug, cat_title)
            kind_counts[kind] = kind_counts.get(kind, 0) + 1
            tools.append(
                {
                    "id": key,
                    "n": clean_name,
                    "u": href,
                    "i": icon or f"https://icon.horse/icon/{domain}",
                    "f": fallback or f"https://icon.horse/icon/{domain}",
                    "p": pricing or "free",
                    "t": kind,
                    "c": cat_title.strip(),
                    "s": cat_slug,
                    "d": domain,
                    "x": make_blurb(
                        clean_name,
                        cat_slug,
                        cat_title,
                        pricing or "free",
                        href,
                        domain,
                        kind,
                        external,
                    ),
                }
            )

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(tools, separators=(",", ":")), encoding="utf-8")
    print(f"Wrote {len(tools)} tools to {OUT_PATH}")
    print("Kinds:", ", ".join(f"{k}={v}" for k, v in sorted(kind_counts.items())))
    print("External blurbs loaded:", len(external))
    print("Sample must-try:")
    for t in tools:
        if t["s"] == "must-try":
            print(f"  {t['n']}: {t['x']}")


if __name__ == "__main__":
    main()
