"""Build compact tools index for the home search from data/student-directory.html."""
import json
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
HTML_PATH = ROOT / "data" / "student-directory.html"
OUT_PATH = ROOT / "data" / "scroll-tools.json"

LINK_RE = re.compile(
    r'<a\s+href="([^"]+)"[^>]*class="tool-link"[^>]*data-pricing="([^"]*)"[^>]*>'
    r'(?:.*?<img[^>]*src="([^"]*)"[^>]*data-fallback="([^"]*)"[^>]*)?'
    r'.*?<span class="tool-link-name">([^<]*)</span>',
    re.DOTALL | re.IGNORECASE,
)

SECTION_RE = re.compile(
    r'<section class="tool-category"[^>]*\bdata-category="([^"]+)"[^>]*>.*?'
    r'<h3 class="category-title">([^<]*)</h3>.*?'
    r'<div class="category-tools">(.*?)</div>\s*</section>',
    re.DOTALL,
)

CATEGORY_BLURBS = {
    "must-try": "Standout pick from the directory, worth trying first.",
    "github-powerhouses": "Popular open-source project on GitHub for learning and building.",
    "free-books": "Find free textbooks, PDFs, and ebooks for coursework and reading.",
    "courses": "Courses, tutorials, and learning platforms for self-paced study.",
    "study": "Study aids: flashcards, notes, quizzes, exam prep, and AI study helpers.",
    "ai": "AI assistant or chat tool for questions, writing, and productivity.",
    "research": "Research and lookup tools for papers, sources, and deep answers.",
    "writing": "Writing, grammar, citations, and essay workflow tools.",
    "free-movies": "Streaming and media sites for movies, shows, and entertainment.",
    "free-stuff": "Free resources, alternatives, and discovery hubs for students.",
    "design": "Design, UI, fonts, and creative tools for projects and portfolios.",
    "programming": "Coding references, docs, practice, and developer utilities.",
    "programming-ai": "AI coding assistants, completions, and dev-focused AI tools.",
    "pdf": "PDF viewing, editing, conversion, chat, and document utilities.",
    "image": "Edit, compress, and convert images — PNG, JPG, WebP, GIF, and more.",
    "video": "Video converters, compressors, editors, and download helpers.",
    "audio": "Audio converters, editors, and sound utilities.",
    "gif-converters": "Make and convert GIFs from images or video online.",
    "utilities": "Handy everyday utilities: converters, helpers, and small tools.",
    "productivity": "Productivity apps for focus, planning, and getting work done.",
    "security": "Security, privacy, and safety tools for your accounts and devices.",
    "open-source": "Open-source software discovery and FOSS community resources.",
    "chrome-extension": "Browser extensions that add features inside Chrome.",
    "browser-extensions": "Browser add-ons for privacy, media, and productivity.",
    "cloud": "Cloud storage, sync, and file backup for documents and media.",
    "notepad": "Notes, notebooks, and knowledge-base apps for writing and study.",
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

# Near-duplicate shelves → one category. AI* sources keep/get the AI kind tag.
# source_slug: (canonical_slug, canonical_title, force_kind|None)
CATEGORY_MERGE: dict[str, tuple[str, str, str | None]] = {
    # Study
    "ai-study": ("study", "Study", "ai"),
    "ai-homework": ("study", "Study", "ai"),
    "ai-study-tools": ("study", "Study", "ai"),
    "exam-prep": ("study", "Study", None),
    "test-prep": ("study", "Study", None),
    # Cloud storage (not providers / OSINT / IaC)
    "cloud-sync": ("cloud", "Cloud", None),
    # Notes
    "ai-notetakers": ("notepad", "Notepad", "ai"),
    "note-taking": ("notepad", "Notepad", None),
    "notebooks": ("notepad", "Notepad", None),
    # PDF
    "ai-pdf-chat": ("pdf", "PDF Tools", "ai"),
    # Writing
    "grammar-writing-ai": ("writing", "Writing", "ai"),
    "ai-writing-assistants": ("writing", "Writing", "ai"),
    "essay-tools": ("writing", "Writing", None),
    # Voice / audio generation
    "ai-audio": ("ai-voice", "AI Voice", "ai"),
    # Extensions
    "chrome-extension": ("browser-extensions", "Browser Extensions", "extension"),
    "firefox-extensions": ("browser-extensions", "Browser Extensions", "extension"),
    "extensions": ("browser-extensions", "Browser Extensions", "extension"),
    # Collaboration
    "collaboration": ("team-collaboration", "Team Collaboration", None),
    # Math / science
    "math-tools": ("mathematics", "Mathematics Tools", None),
    "math-docs": ("mathematics", "Mathematics Tools", None),
    "science-tools": ("science", "Science", None),
    # Generic converters / analytics odds and ends
    "converters": ("utilities", "Utilities", None),
    "analytical": ("analytics", "Analytics", None),
    # Git hosts
    "git-hosting": ("source-code-repos", "Source Code Repos", None),
    # Duplicate-named OSINT shelves → clearnet equivalents
    "osint-language-translation": ("translation", "Translation Tools", None),
    "osint-privacy-tools": ("privacy-tools", "Privacy Tools", None),
    # Tiny stock shelves
    "stock-audio": ("audio", "Audio Converters", None),
    "ebooks": ("free-books", "Free Books", None),
}


def resolve_category(slug: str, title: str) -> tuple[str, str, str | None]:
    """Return (canonical_slug, canonical_title, force_kind)."""
    hit = CATEGORY_MERGE.get((slug or "").strip())
    if not hit:
        return slug, (title or "").strip(), None
    return hit[0], hit[1], hit[2]

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
    r"perplexity|deepseek|groq|anthropic|openai|qwen|grok|mistral|ollama|"
    r"chatgpt|notebooklm|suno|udio|elevenlabs|runway|midjourney|cursor)(?![a-z0-9])",
    re.I,
)

# Categories that are dedicated AI product shelves (tools there are usually AI).
# Note: bare "ai" (All-IN-One) is excluded — that shelf mixes many non-AI utilities.
PURE_AI_SLUGS = {
    "generative-ai",
    "local-ai",
    "ai-notetakers",
    "ai-browser",
    "ai-video",
    "ai-voice",
    "ai-audio",
    "ai-study",
    "ai-homework",
    "ai-image-editing",
    "ai-pdf-chat",
    "ai-agents",
    "ai-flows",
    "programming-ai",
    "osint-ai-tools",
    "grammar-writing-ai",
    "ai-writing-assistants",
    "ai-research-tools",
    "ai-study-tools",
}

# Domains that look like AI (.ai TLD / name) but are not AI products.
NON_AI_DOMAINS = {
    "beacons.ai",
    "linktree.ai",
    "carrd.ai",
}

# Course / badge platforms — “AI” in the title means a course about AI, not an AI app.
LEARNING_DOMAINS = {
    "coursera.org",
    "linkedin.com",
    "skillsbuild.org",
    "skills.google",
    "udemy.com",
    "edx.org",
    "udacity.com",
    "khanacademy.org",
    "skillshare.com",
    "pluralsight.com",
    "freecodecamp.org",
}

# Multi-tenant hosts must never share one blurb.
SHARED_HOST_DOMAINS = {
    "github.com",
    "huggingface.co",
    "chromewebstore.google.com",
    "addons.mozilla.org",
    "microsoftedge.microsoft.com",
    "play.google.com",
    "apps.apple.com",
    "apps.microsoft.com",
}

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
    "grok.com",
    "deepseek.com",
    "chat.deepseek.com",
    "chat.qwen.ai",
    "qwen.ai",
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
    "deepai.org",
    "mathgptpro.com",
    "math.bot",
    "chatcsv.com",
    "replika.com",
    "hume.ai",
    "venice.ai",
    "lobechat.com",
    "mem.ai",
    "granola.ai",
    "anara.ai",
    "dyad.sh",
    "designarena.ai",
    "emergent.sh",
    "app.emergent.sh",
}


def is_bad_name(name: str) -> bool:
    value = name.strip()
    if not value or value in BAD_TOOL_NAMES:
        return True
    stripped = value.replace(" ", "")
    if stripped and all(c in BAD_TOOL_NAMES or c.isspace() for c in value):
        return True
    return False


def is_junk_utility(name: str, url: str, domain: str) -> bool:
    """Drop invite links, CDN files, and other non-tool Utilities junk."""
    n = (name or "").strip()
    u = (url or "").lower()
    d = (domain or "").lower()

    if any(
        x in d
        for x in (
            "telegram.me",
            "telegram.dog",
            "t.me",
            "i.imgur.com",
            "imgur.com",
            "i.ibb.co",
            "files.catbox.moe",
            "redd.it",
            "vk.com",
            "vkvideo.ru",
        )
    ):
        return True
    if re.search(r"(telegram\.(me|dog)|t\.me)/", u):
        return True
    if re.search(r"\.(png|jpe?g|gif|webp|bmp|svg)(\?|$)", u):
        return True
    if re.search(r"\.(png|jpe?g|gif|webp)$", n, re.I):
        return True
    # Invite / channel handles (not real product names)
    if re.match(r"^(\+|@|~)", n):
        return True
    if re.search(r"/invite|/joinchat", u):
        return True
    if "rentry.co" in d or "rentry.org" in d:
        return True
    # Generic path junk titles
    nl = n.lower().strip()
    if nl in {
        "index",
        "home",
        "main",
        "page",
        "forum",
        "forums",
        "community",
        "communities",
        "search",
        "login",
        "signup",
        "about",
        "contact",
        "download",
        "docs",
        "wiki",
    }:
        return True
    if re.match(r"^(index|home|main|default)\.(php|html?|aspx?|jsp)$", nl):
        return True
    if re.search(r"/(index|home|main|default)\.(php|html?|aspx?|jsp)(\?|$)", u):
        return True
    return False


# (pattern, short action label, description)
UTILITY_ACTIONS: list[tuple[re.Pattern[str], str, str]] = [
    (
        re.compile(r"url\s*short|shorten|tinyurl|bitly|shorturl|is\.gd|t\.ly|cutt\.ly"),
        "Shorten",
        "Shorten long links into compact shareable URLs",
    ),
    (
        re.compile(r"password\s*gen|passwordgenerator|strong\s*password|password\s*generator"),
        "Passwords",
        "Generate strong random passwords you can copy instantly",
    ),
    (
        re.compile(r"qr[\s.-]?code|qr\s*gen"),
        "QR",
        "Create QR codes from text, links, or contact info",
    ),
    (
        re.compile(r"bar[\s-]?code|barcode"),
        "Barcode",
        "Generate barcodes for products, inventory, or labels",
    ),
    (
        re.compile(r"unit\s*convert|convertunits|unitconverters|measurement"),
        "Units",
        "Convert between common units of measurement",
    ),
    (
        re.compile(r"epoch|unix\s*time|timestamp\s*convert|epochconverter"),
        "Epoch",
        "Convert Unix timestamps to readable dates and back",
    ),
    (
        re.compile(r"world\s*clock|timeanddate|timezone|time\s*zone"),
        "Clock",
        "Check world clocks, time zones, and calendars",
    ),
    (
        re.compile(r"random\.org|random org|list\s*random|randomiz|random\s*number|dice\s*roll"),
        "Random",
        "Generate random numbers, picks, lists, or dice rolls",
    ),
    (
        re.compile(r"calculat|calculator\.net|calculator"),
        "Calculate",
        "Run everyday and specialty calculators in your browser",
    ),
    (
        re.compile(r"ifixit|repair\s*guide"),
        "Repair",
        "Follow step-by-step device repair guides and parts info",
    ),
    (
        re.compile(r"cheat\s*sheet"),
        "Cheatsheet",
        "Quick reference cheat sheets for common skills and tools",
    ),
    (
        re.compile(r"color\s*pick|eyedrop|hex\s*color|color\s*convert"),
        "Colors",
        "Pick colors and convert between HEX, RGB, and more",
    ),
    (
        re.compile(r"json\s*(format|beaut|valid|lint)|jsonlint"),
        "JSON",
        "Format, validate, or inspect JSON data",
    ),
    (
        re.compile(r"base64|hash\s*(gen|tool)|md5|sha ?256|uuid\s*gen"),
        "Encode",
        "Encode, decode, or hash text and identifiers",
    ),
    (
        re.compile(r"regex|regexp|regular\s*expression"),
        "Regex",
        "Test and build regular expressions interactively",
    ),
    (
        re.compile(r"\bdiff\b|compare\s*text|text\s*compare|csvdiff"),
        "Diff",
        "Compare two texts or files and highlight differences",
    ),
    (
        re.compile(r"word\s*count|character\s*count|lorem"),
        "Count",
        "Count words and characters or generate placeholder text",
    ),
    (
        re.compile(r"markdown|md\s*edit|md\s*preview"),
        "Markdown",
        "Write and preview Markdown in the browser",
    ),
    (
        re.compile(r"\bpdf\b"),
        "PDF",
        "View, edit, compress, or convert PDF documents",
    ),
    (
        re.compile(r"image\s*(compress|resize|convert|crop|edit)|photo\s*edit|img\s*2"),
        "Images",
        "Resize, compress, convert, or edit images online",
    ),
    (
        re.compile(r"video\s*(convert|compress|download|edit)|youtube\s*download"),
        "Video",
        "Convert, compress, or download video files",
    ),
    (
        re.compile(r"audio\s*(convert|compress|edit|cut)|mp3\s*convert"),
        "Audio",
        "Convert, trim, or compress audio files",
    ),
    (
        re.compile(r"\bzip\b|unzip|\brar\b|extract\s*archive|file\s*compress"),
        "Archive",
        "Compress or extract ZIP and other archive files",
    ),
    (
        re.compile(r"temp\s*mail|disposable|10\s*min.*mail|guerrilla\s*mail"),
        "Tempmail",
        "Get a disposable email inbox without signing up",
    ),
    (
        re.compile(r"\bvpn\b|\bproxy\b|\btor\b"),
        "Privacy",
        "Browse more privately with VPN, proxy, or Tor helpers",
    ),
    (
        re.compile(r"speed\s*test|bandwidth\s*test|fast\.com"),
        "Speed",
        "Measure your internet download and upload speed",
    ),
    (
        re.compile(r"whois|dns\s*lookup|ip\s*lookup|my\s*ip|whatismyip"),
        "Network",
        "Look up IPs, DNS records, or your public network info",
    ),
    (
        re.compile(r"translate|dictionary|thesaurus"),
        "Translate",
        "Translate text or look up words and synonyms",
    ),
    (
        re.compile(r"habit|todo|task\s*list|checklist"),
        "Habits",
        "Track habits, tasks, or daily checklists",
    ),
    (
        re.compile(r"\bnote\b|notepad|sticky\s*note|\bmemo\b"),
        "Notes",
        "Jot quick notes in the browser without setup",
    ),
    (
        re.compile(r"pastebin|hastebin|\bpaste\b|\bgist\b"),
        "Paste",
        "Share text snippets with a quick paste link",
    ),
    (
        re.compile(r"screenshot|screen\s*capture|\bsnip\b"),
        "Capture",
        "Capture screenshots or snip parts of your screen",
    ),
    (
        re.compile(r"wifi|wi-fi"),
        "WiFi",
        "Find or share Wi-Fi passwords and network details",
    ),
    (
        re.compile(r"\bcsv\b|spreadsheet|\bexcel\b|\bxsv\b"),
        "CSV",
        "Inspect, convert, or diff CSV and spreadsheet data",
    ),
    (
        re.compile(r"cron|crontab"),
        "Cron",
        "Build and explain cron schedules for automation",
    ),
    (
        re.compile(r"\bjwt\b|token\s*decod"),
        "Tokens",
        "Decode and inspect JWT or auth tokens safely",
    ),
    (
        re.compile(r"httpie|http\s*prompt|api\s*client|rest\s*client"),
        "HTTP",
        "Send and explore HTTP/API requests from your machine",
    ),
    (
        re.compile(r"benchmark|hyperfine|\bperf\b"),
        "Benchmark",
        "Benchmark commands or measure performance",
    ),
    (
        re.compile(r"\bssh\b|tunnel|port\s*forward|sshuttle"),
        "SSH",
        "SSH, tunnel, or forward ports for remote access",
    ),
    (
        re.compile(r"monitor|watch\s*file|watchexec|bandwhich"),
        "Monitor",
        "Watch files, processes, or network activity live",
    ),
    (
        re.compile(r"coolmath|browser\s*game|\bgames?\b"),
        "Play",
        "Play a quick browser game or interactive toy",
    ),
    (
        re.compile(r"compress|optimizer|minify"),
        "Compress",
        "Compress or minify files to save space",
    ),
    (
        re.compile(r"convert|converter|transcode"),
        "Convert",
        "Convert files between formats online",
    ),
    (
        re.compile(r"download|downloader"),
        "Download",
        "Download files or media from the web",
    ),
    (
        re.compile(r"generator|generate"),
        "Generate",
        "Generate text, codes, or assets instantly",
    ),
    (
        re.compile(r"editor|\bedit\b"),
        "Edit",
        "Edit files or text quickly in your browser",
    ),
    (
        re.compile(r"weather|forecast"),
        "Weather",
        "Check weather conditions and forecasts",
    ),
    (
        re.compile(r"calendar|\bdate\b|countdown"),
        "Dates",
        "Work with dates, calendars, or countdowns",
    ),
    (
        re.compile(r"map\b|geo|coordinate"),
        "Maps",
        "Explore maps, places, or coordinates",
    ),
    (
        re.compile(r"toolfk|10015|all-?in-?one\s*tool|online\s*tools?\s*box"),
        "Toolkit",
        "Browse a suite of small everyday browser utilities",
    ),
]


def utility_label_and_blurb(
    name: str, domain: str, url: str, kind: str
) -> tuple[str, str]:
    """Utilities-only: short action label + purpose description."""
    n = (name or "").strip()
    d = (domain or "").lower()
    u = (url or "").lower()
    path = urlparse(url or "").path.lower()
    # Keep dots for domain matches (random.org); also use spaced form for tokens
    raw = f"{n} {d} {u} {path}".lower()
    spaced = raw.replace("-", " ").replace("_", " ").replace(".", " ")

    for pat, label, desc in UTILITY_ACTIONS:
        if pat.search(raw) or pat.search(spaced):
            return label, brief(desc)

    # GitHub / CLI: derive from repo tokens
    if d == "github.com" or d.endswith(".github.io"):
        repo = urlparse(url or "").path.strip("/").split("/")[-1]
        token_blob = f"{n} {repo}".lower().replace("-", " ").replace("_", " ")
        for pat, label, desc in UTILITY_ACTIONS:
            if pat.search(token_blob):
                return label, brief(desc)
        nice = re.sub(r"[-_]+", " ", repo or n).strip()
        if nice:
            label = nice.replace(" ", "-")
            label = (label[:1].upper() + label[1:])[:16]
            return label, brief(f"Open-source utility: {nice}")

    # Readable product names → short verb/noun from last word
    words = re.findall(r"[A-Za-z][A-Za-z0-9+]{1,}", n)
    suffix_map = {
        "generator": ("Generate", "Generate {what} quickly in your browser"),
        "converter": ("Convert", "Convert {what} between formats"),
        "calculator": ("Calculate", "Calculate {what} with a simple online tool"),
        "checker": ("Check", "Check {what} quickly and clearly"),
        "editor": ("Edit", "Edit {what} online without installing software"),
        "downloader": ("Download", "Download {what} from the web"),
        "compressor": ("Compress", "Compress {what} to smaller sizes"),
        "tracker": ("Track", "Track {what} for school and daily use"),
        "remover": ("Remove", "Remove {what} from files or media"),
        "viewer": ("View", "View {what} in your browser"),
        "maker": ("Make", "Make {what} in a few clicks"),
        "builder": ("Build", "Build {what} with a simple online tool"),
        "tester": ("Test", "Test {what} interactively"),
        "finder": ("Find", "Find {what} fast"),
        "manager": ("Manage", "Manage {what} from one place"),
        "randomizer": ("Random", "Randomize lists, picks, or order instantly"),
    }
    if words:
        last = words[-1].lower()
        if last in suffix_map:
            label, tmpl = suffix_map[last]
            what = " ".join(words[:-1]).lower() or "items"
            return label, brief(tmpl.format(what=what))
        if len(words) >= 2 and 2 < len(words[0]) <= 12:
            label = words[0][:1].upper() + words[0][1:]
            purpose = " ".join(w.lower() for w in words[1:])
            return label, brief(f"{n} — {purpose} utility for everyday tasks")
        if 3 <= len(n) <= 22 and re.search(r"[a-zA-Z]{3}", n) and " " in n:
            label = words[0][:1].upper() + words[0][1:]
            return label, brief(f"{n} — everyday utility for quick tasks")

    # Domain brand fallback — skip marketplace hosts
    if d in {
        "greasyfork.org",
        "openuserjs.org",
        "addons.mozilla.org",
        "chromewebstore.google.com",
        "apps.apple.com",
        "play.google.com",
        "flathub.org",
        "f-droid.org",
        "oss.gallery",
        "sourceforge.net",
        "gitlab.com",
        "codeberg.org",
    }:
        label = (words[0][:1].upper() + words[0][1:]) if words else "Utility"
        return brief(label, 14), brief(f"{n or label} — installable everyday utility")

    brand = (d.split(".")[0] if d else "Tool").replace("-", " ")
    brand = brand[:1].upper() + brand[1:] if brand else "Tool"
    if kind == "extension":
        return brief(brand, 14), brief(f"{n or brand} — browser extension for everyday tasks")
    if kind == "app":
        return brief(brand, 14), brief(f"{n or brand} — installable app for everyday tasks")
    return brief(brand, 14), brief(f"{n or brand} — everyday web utility")


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


def root_domain(domain: str) -> str:
    parts = (domain or "").lower().split(".")
    if len(parts) >= 2:
        return ".".join(parts[-2:])
    return domain or ""


def domain_is_ai(domain: str) -> bool:
    d = (domain or "").lower()
    if not d or d in NON_AI_DOMAINS:
        return False
    if d in KNOWN_AI_DOMAINS:
        return True
    # Subdomains of known AI hosts (chat.openai.com already listed; catch others)
    for known in KNOWN_AI_DOMAINS:
        if d == known or d.endswith("." + known):
            return True
    if d.endswith(".ai") or ".ai." in d:
        return True
    # Domains with strong AI product tokens (mathgptpro.com, etc.)
    compact = d.replace(".", " ").replace("-", " ")
    if AI_NAME_RE.search(compact):
        return True
    return False


def is_learning_domain(domain: str) -> bool:
    d = (domain or "").lower()
    if d in LEARNING_DOMAINS:
        return True
    return any(d == x or d.endswith("." + x) for x in LEARNING_DOMAINS)


# Clear non-AI utilities often dumped into All-IN-One (AI) / similar shelves.
NON_AI_PURPOSE_RE = re.compile(
    r"(temp\s*-?\s*mail|temporary\s*(e-?mail|mail)|disposable\s*(e-?mail|mail)?|"
    r"guerrilla\s*mail|10\s*-?\s*min(ute)?s?\s*(e-?mail|mail)|minute\s*(e-?mail|mail)|"
    r"fake\s*(e-?mail|mail)|trash\s*(e-?mail|mail)|burner\s*(e-?mail|mail)|"
    r"yopmail|mailinator|tempmail|tempr\.?email|emailnator|mail\.tm|"
    r"(?<![a-z])(vpn|proxy|torrent|pastebin|password\s*manager|file\s*converter|"
    r"pdf\s*(merge|split|compress|convert)|zip\s*extractor)(?![a-z])|"
    r"webmail|outlook|boomerang\s*gmail)",
    re.I,
)


def clearly_non_ai(name: str, domain: str) -> bool:
    blob = f"{name or ''} {domain or ''}".lower().replace("-", " ").replace("_", " ")
    compact = (domain or "").lower().replace(".", " ").replace("-", " ")
    if NON_AI_PURPOSE_RE.search(blob) or NON_AI_PURPOSE_RE.search(compact):
        # Don't veto real AI products that happen to mention mail (rare)
        if AI_NAME_RE.search(name or "") and not re.search(
            r"temp|temporary|disposable|guerrilla|10\s*min|fakemail|trashmail",
            name or "",
            re.I,
        ):
            return False
        return True
    return False


def is_ai_tool(name: str, url: str, domain: str, slug: str, title: str) -> bool:
    """Tag AI only for actual AI products — not every tool in an 'AI Tools' shelf."""
    d = (domain or "").lower()
    n = name or ""
    s = (slug or "").lower()

    # Courses/badges about AI are websites, not AI apps
    if is_learning_domain(d):
        return False
    if d in NON_AI_DOMAINS:
        return False
    if clearly_non_ai(n, d):
        return False

    if domain_is_ai(d):
        return True
    if AI_NAME_RE.search(n):
        return True

    # Dedicated AI shelves — but only when the tool itself isn't clearly something else
    if s in PURE_AI_SLUGS:
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

    if d == "github.com" or d.endswith(".github.io") or s == "github-powerhouses":
        return "github"

    if is_ai_tool(name, url, domain, slug, title):
        return "ai"

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
    "chat.deepseek.com": "DeepSeek AI chat for reasoning, coding, and study help",
    "deepseek.com": "DeepSeek AI models and chat for coding and reasoning",
    "chat.qwen.ai": "Qwen AI chat for writing, translation, and coding",
    "grok.com": "xAI’s Grok chatbot for real-time answers and humor",
    "copilot.microsoft.com": "Microsoft Copilot AI for chat, Office, and the web",
    "scholar.google.com": "Search scholarly papers, citations, and academic authors",
    "semanticscholar.org": "AI-assisted academic search across research papers",
    "researchgate.net": "Network for researchers to share papers and questions",
    "arxiv.org": "Open-access preprints in STEM and related fields",
    "base-search.net": "Academic search engine across research repositories",
    "connectedpapers.com": "Explore related papers through citation graphs",
    "litmaps.com": "Map and track research papers for literature reviews",
    "symbolab.com": "Step-by-step math solver for algebra, calculus, and more",
    "mathway.com": "Solve math problems with worked explanations",
    "cymath.com": "Free step-by-step math problem solver",
    "photomath.com": "Scan handwritten or printed math and get solutions",
    "wolframalpha.com": "Compute answers across math, science, and data",
    "math.bot": "Chat-style AI helper for math questions",
    "mathgptpro.com": "AI math tutor for homework and step-by-step help",
    "tableau.com": "Build interactive charts and public data visualizations",
    "public.tableau.com": "Browse and publish interactive Tableau visualizations",
    "character.ai": "Chat with character-based AI personalities",
    "poe.com": "One app to chat with many AI models",
    "replika.com": "Personal AI companion for conversation and reflection",
    "phind.com": "AI search tuned for developers and technical answers",
    "codeium.com": "Free AI code completion and chat for developers",
    "tabnine.com": "AI code completions that learn from your codebase",
    "continue.dev": "Open-source AI coding assistant for your IDE",
    "cursor.com": "AI-first code editor for writing and refactoring",
    "github.com/features/copilot": "GitHub’s AI pair programmer for code suggestions",
    "10minemail.com": "Disposable inbox that expires in about 10 minutes",
    "10minutemail.com": "Disposable inbox that expires in about 10 minutes",
    "temp-mail.org": "Temporary email address to avoid spam and signups",
    "temp-mail.io": "Temporary email address to avoid spam and signups",
    "tempmail.com": "Temporary email address to avoid spam and signups",
    "guerrillamail.com": "Disposable guerrilla inbox for quick signups",
    "mail.tm": "Temporary email API and disposable inbox",
    "yopmail.com": "Disposable YOPmail inbox without registration",
    "mailnesia.com": "Temporary email inbox for anonymous signups",
    "smailpro.com": "Temporary email inbox without creating an account",
    "tempr.email": "Temporary email address for short-term use",
}

SHORT_CAT = {
    "must-try": "featured student pick",
    "github-powerhouses": "popular open-source project",
    "free-books": "free books and textbooks",
    "courses": "courses and tutorials",
    "study": "study and exam prep",
    "ai": "AI chat and assistants",
    "research": "research and lookup",
    "writing": "writing and essays",
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
    "generative-ai": "generative AI creation",
    "local-ai": "local AI models",
    "file-sharing": "file sharing",
    "music": "music streaming or download",
    "video": "video tools",
    "vpn": "VPN and private browsing",
    "privacy-tools": "privacy protection",
    "cloud": "cloud storage and sync",
    "notepad": "notes and notebooks",
    "ai-voice": "AI voice and audio",
    "mathematics": "math tools",
    "science": "science learning",
    "translation": "translation",
    "analytics": "analytics",
    "team-collaboration": "team collaboration",
    "source-code-repos": "source code hosting",
    "audio": "audio tools",
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
    # Drop redundant "AI" wording from mixed shelves so blurbs stay tool-specific
    title = re.sub(r"\bai\b", "", title, flags=re.I)
    title = re.sub(r"[!]+$", "", title).strip().lower()
    title = re.sub(r"\s+", " ", title).strip(" -")
    return title or "student tools"


def github_repo_blurb(name: str, url: str, cat_slug: str, cat_title: str) -> str:
    path = urlparse(url).path.strip("/")
    parts = [p for p in path.split("/") if p and p not in {"features"}]
    repo = parts[1] if len(parts) >= 2 else ""
    label = (name or repo or "project").strip()
    if cat_slug == "ai":
        if repo and repo.lower() not in label.lower():
            return brief(f"{label} — open-source project on GitHub ({repo})")
        return brief(f"{label} — open-source project on GitHub")
    topic = topic_phrase(cat_slug, cat_title)
    if repo and repo.lower() not in label.lower():
        return brief(f"{label} — open-source {topic} ({repo})")
    return brief(f"{label} — open-source {topic} on GitHub")


def purpose_blurb(name: str, domain: str) -> str | None:
    """Describe the tool from its name/domain — never from a mismatched shelf."""
    n = (name or "").strip() or (domain or "Tool")
    blob = f"{n} {domain or ''}".lower()
    blob = blob.replace("-", " ").replace("_", " ").replace(".", " ")

    rules: list[tuple[re.Pattern[str], str]] = [
        (
            re.compile(
                r"temp\s*mail|temporary\s*(e?\s*mail|mail)|disposable|"
                r"guerrilla\s*mail|10\s*min(ute)?s?\s*(e?\s*mail|mail)|"
                r"minute\s*(e?\s*mail|mail)|fake\s*(e?\s*mail|mail)|"
                r"trash\s*(e?\s*mail|mail)|burner|yopmail|mailinator|"
                r"tempmail|tempr\s*email|emailnator|mail\s*tm|"
                r"mtempmail|etempmail|tempmailo|urtempmail|emailtemp|"
                r"tempemail|temporarymail|mail\s*temp|48\s*hour\s*email|"
                r"ghostinbox|smailpro|mailnesia|disposablemail"
            ),
            f"{n} — disposable temporary email inbox, no signup needed",
        ),
        (
            re.compile(r"webmail|outlook|boomerang\s*gmail|canary\s*mail|mailspring"),
            f"{n} — email client or webmail helper",
        ),
        (
            re.compile(r"(?<![a-z])(e?\s*mail|inbox)(?![a-z])"),
            f"{n} — email inbox or mail utility",
        ),
        (
            re.compile(r"(?<![a-z])(vpn|proxy)(?![a-z])"),
            f"{n} — browse privately with VPN or proxy protection",
        ),
        (
            re.compile(r"password|passkey|authenticator|2fa|totp"),
            f"{n} — password or account security helper",
        ),
        (
            re.compile(r"pdf"),
            f"{n} — PDF tool for viewing, editing, or converting documents",
        ),
        (
            re.compile(r"convert|converter|transcode"),
            f"{n} — convert files or formats online",
        ),
        (
            re.compile(r"compress|compressor|optimizer"),
            f"{n} — compress files to smaller sizes",
        ),
        (
            re.compile(r"download|downloader"),
            f"{n} — download media or files from the web",
        ),
        (
            re.compile(r"torrent|magnet"),
            f"{n} — torrent search or download helper",
        ),
        (
            re.compile(r"note|notepad|notebook|memo"),
            f"{n} — take and organize notes for class and projects",
        ),
        (
            re.compile(r"flashcard|anki|quizlet"),
            f"{n} — study with flashcards and spaced repetition",
        ),
        (
            re.compile(r"grammar|spell\s*check|proofread"),
            f"{n} — check grammar and polish writing",
        ),
        (
            re.compile(r"citation|bibliograph|cite"),
            f"{n} — build citations and bibliographies for papers",
        ),
        (
            re.compile(r"scholar|arxiv|research\s*gate"),
            f"{n} — search academic papers and research sources",
        ),
        (
            re.compile(r"ocr|speech\s*to\s*text|transcri"),
            f"{n} — extract text from images, audio, or documents",
        ),
        (
            re.compile(r"image\s*edit|photo\s*edit|background\s*remov"),
            f"{n} — edit images or remove backgrounds online",
        ),
        (
            re.compile(r"video\s*edit|screen\s*record"),
            f"{n} — record or edit video in the browser",
        ),
        (
            re.compile(r"chat\s*gpt|chatgpt|claude|gemini|perplexity|copilot|"
                       r"llm|chatbot|ai\s*chat|ai\s*assistant"),
            f"{n} — AI chat assistant for writing, coding, and questions",
        ),
    ]

    for pat, text in rules:
        if pat.search(blob):
            return brief(text)
    return None


def blurb_from_name(
    name: str, kind: str, cat_slug: str, cat_title: str, domain: str = ""
) -> str | None:
    n = (name or "").strip()
    nl = n.lower()
    topic = topic_phrase(cat_slug, cat_title)

    purpose = purpose_blurb(n, domain)
    if purpose:
        return purpose

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

    # All-IN-One (AI) is a mixed dump — never invent "AI chat" blurbs from it
    if cat_slug == "ai":
        return None

    if kind == "extension":
        return brief(f"{n} — browser extension for {topic}")
    if kind == "ai":
        return brief(f"{n} — AI assistant for {topic}")
    if kind == "app":
        return brief(f"{n} — installable app for {topic}")
    if kind == "github":
        return brief(f"{n} — open-source {topic} on GitHub")
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
    d = (domain or "").lower()

    if key in KNOWN_BLURBS:
        return brief(KNOWN_BLURBS[key])
    # Never apply one blurb to every GitHub/HF/store listing
    if d in KNOWN_BLURBS and d not in SHARED_HOST_DOMAINS:
        return brief(KNOWN_BLURBS[d])
    if key in external:
        return external[key]
    if d in external and d not in SHARED_HOST_DOMAINS:
        return external[d]

    # Purpose from name/domain always beats shelf-based AI filler
    purpose = purpose_blurb(name, d)
    if purpose:
        return purpose

    if d == "github.com" or d.endswith(".github.io"):
        return github_repo_blurb(name, url, cat_slug, cat_title)

    if d == "huggingface.co":
        path = urlparse(url).path.strip("/")
        label = (name or path.split("/")[-1] or "Hugging Face resource").strip()
        return brief(f"{label} — models, demos, or datasets on Hugging Face")

    from_name = blurb_from_name(name, kind, cat_slug, cat_title, d)
    if from_name:
        return from_name

    topic = topic_phrase(cat_slug, cat_title)
    label = (name or d or "Tool").strip()
    # Prefer a unique, tool-specific line over shelf filler like "AI chat and assistants"
    if d and d not in label.lower():
        host_bit = d
    else:
        host_bit = ""

    if kind == "ai":
        if host_bit:
            return brief(f"{label} — AI-powered tool ({host_bit})")
        return brief(f"{label} — AI-powered tool")
    if kind == "extension":
        if host_bit:
            return brief(f"{label} — browser add-on ({host_bit})")
        return brief(f"{label} — browser add-on for {topic}")
    if kind == "app":
        if host_bit:
            return brief(f"{label} — mobile or desktop app ({host_bit})")
        return brief(f"{label} — mobile or desktop app for {topic}")
    if kind == "github":
        return brief(f"{label} — open-source {topic} repository")
    if host_bit:
        if cat_slug == "utilities":
            return brief(f"{label} — everyday utility for quick browser tasks")
        return brief(f"{label} — online tool at {host_bit}")
    if cat_slug == "ai":
        return brief(f"{label} — online tool")
    if cat_slug == "utilities":
        return brief(f"{label} — everyday utility for quick browser tasks")
    return brief(f"{label} — web tool for {topic}")


# Preferred Top 3 per category (match against name or domain, case-insensitive).
CATEGORY_TOP3: dict[str, list[str]] = {
    "3d": ["blender", "chili3d", "freecad"],
    "must-try": ["eye2.ai", "redirect blocker", "vocal remover"],
    "ai": ["chatgpt", "claude", "perplexity"],
    "research": ["perplexity", "claude", "chatgpt"],
    "mathematics": ["wolfram", "symbolab", "photomath"],
    "programming-ai": ["cursor", "github copilot", "phind"],
    "local-ai": ["lm studio", "ollama", "gpt4all"],
    "generative-ai": ["midjourney", "leonardo", "huggingface"],
    "pdf": ["ilovepdf", "lightpdf", "10015.io"],
    "vpn": ["protonvpn", "mullvad", "windscribe"],
    "writing": ["quillbot", "grammarly", "hemingway"],
    "design": ["figma", "canva", "21st.dev"],
    "productivity": ["notion", "todoist", "obsidian"],
    "notepad": ["notion", "obsidian", "standard notes"],
    "courses": ["coursera", "khanacademy", "edx"],
    "free-books": ["annas-archive.is", "oceanofpdf.com", "z-lib.gd"],
    "gif-converters": ["ezgif.com", "cloudconvert.com/gif-converter", "freeconvert.com"],
    "study": ["youlearn", "anki", "quizlet"],
    "free-movies": ["flixer.su", "movy.sx", "stellar.gdn"],
    "immersive-reader": ["elevenreader", "readaloud.net", "speechify"],
    "payment-billing": ["stripe.com", "gumroad", "payhip"],
    "authentication": ["google authenticator", "microsoft authenticator", "duo.com"],
    "osint-people-search-engines": [
        "fastpeoplesearch",
        "peoplefinders",
        "whitepages.com/people-search",
    ],
    "web-hosting": ["porkbun", "vercel.com", "squarespace"],
    "browser-games": ["fancypants", "minecraft", "kizi"],
    "ai-voice": ["elevenlabs", "murf", "lovo"],
    "osint-search-engines": ["opera gx", "brave", "duckduckgo"],
    "osint-username": ["whatsmyname.app", "sherlock-project/sherlock", "webbreacher/whatsmyname"],
    "cloud": ["mega", "google drive", "syncthing"],
    "screen-recording": ["obs studio", "sharex", "screenity"],
    "website-builders": ["webild", "carrd", "wix"],
    "api-data-ml": ["openrouter", "developer.deepar.ai", "hoppscotch.io"],
    "osint-community-search": [
        "disboard.org",
        "top.gg/discord/servers/tag/community",
        "discord.bots.gg",
    ],
    "osint-dark-web": ["ahmia.fi", "torbot", "onionsearch"],
    "email": ["temp-mail", "10minutemail", "guerrillamail"],
    "security": ["bitwarden", "haveibeenpwned", "virustotal"],
    "privacy-tools": ["privacyguides", "proton", "tor"],
    "video": ["capcut", "shotcut", "openshot"],
    "music": ["spotify", "soundcloud", "bandcamp"],
    "github-powerhouses": ["ollama", "langchain", "huggingface"],
}


def _top3_match_key(tool: dict) -> str:
    return f"{tool.get('n', '')} {tool.get('d', '')} {tool.get('u', '')} {tool.get('id', '')}".lower()


def _pick_top3_tool(group: list[dict], needle: str, used_ids: set[str]):
    """Prefer exact name, then domain/URL, then substring — shortest name wins ties."""
    needle_l = needle.lower().strip()
    best = None
    best_score = -1
    for tool in group:
        tid = tool.get("id") or ""
        if tid in used_ids:
            continue
        name = (tool.get("n") or "").strip().lower()
        domain = (tool.get("d") or "").strip().lower()
        url = (tool.get("u") or "").strip().lower()
        key = _top3_match_key(tool)
        score = -1
        if name == needle_l:
            score = 100
        elif domain == needle_l or domain == needle_l.removeprefix("www."):
            score = 90
        elif needle_l in url:
            score = 80
        elif needle_l in name:
            score = 50 - min(len(name), 30)
        elif needle_l in key:
            score = 10
        if score > best_score:
            best_score = score
            best = tool
    return best if best_score >= 0 else None


def _quality_score(tool: dict) -> tuple:
    """Heuristic fallback when a category has no curated Top 3."""
    pricing = {"free": 40, "free-tier": 24, "limited": 10, "paid": 0}.get(
        tool.get("p") or "free", 0
    )
    kind_boost = {"ai": 8, "website": 6, "app": 5, "extension": 4, "github": 2}.get(
        tool.get("t") or "website", 0
    )
    name = (tool.get("n") or "").strip()
    # Prefer real product names over path junk / index pages
    junk = 0
    if re.match(r"^(index|home|main page|wiki|forum|search|play)\b", name, re.I):
        junk -= 50
    if (tool.get("d") or "") == "github.com":
        kind_boost -= 4
    # Stable tie-breakers: shorter clear names first, then A–Z
    return (pricing + kind_boost + junk, -len(name), name.lower())


def assign_category_ranks(tools: list[dict]) -> None:
    """Stamp r=1..3 on the best tools in each category."""
    by_cat: dict[str, list[dict]] = {}
    for tool in tools:
        tool.pop("r", None)
        slug = tool.get("s") or ""
        by_cat.setdefault(slug, []).append(tool)

    ranked_cats = 0
    for slug, group in by_cat.items():
        if len(group) < 1:
            continue
        picks: list[dict] = []
        preferred = CATEGORY_TOP3.get(slug) or []
        used_ids: set[str] = set()

        for needle in preferred:
            tool = _pick_top3_tool(group, needle, used_ids)
            if tool:
                picks.append(tool)
                used_ids.add(tool.get("id") or "")
            if len(picks) >= 3:
                break

        if len(picks) < 3:
            rest = sorted(
                (t for t in group if (t.get("id") or "") not in used_ids),
                key=_quality_score,
                reverse=True,
            )
            for tool in rest:
                picks.append(tool)
                if len(picks) >= 3:
                    break

        for i, tool in enumerate(picks[:3], start=1):
            tool["r"] = i
        if picks:
            ranked_cats += 1

    print(f"Top 3 assigned in {ranked_cats} categories")


def main():
    html = HTML_PATH.read_text(encoding="utf-8")
    tools = []
    seen: set[str] = set()
    kind_counts: dict[str, int] = {}
    external = load_external_blurbs()

    for cat_slug, cat_title, block in SECTION_RE.findall(html):
        orig_slug = cat_slug
        orig_title = cat_title.strip()
        canon_slug, canon_title, force_kind = resolve_category(orig_slug, orig_title)
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
            if canon_slug == "utilities" and is_junk_utility(clean_name, href, domain):
                continue
            # Classify against the original shelf so AI*/extension shelves still tag correctly
            kind = classify_kind(clean_name, href, domain, orig_slug, orig_title)
            if force_kind == "ai" and kind == "website":
                kind = "ai"
            elif force_kind == "extension" and kind == "website":
                kind = "extension"

            display_name = clean_name
            blurb = None
            if canon_slug == "utilities":
                display_name, blurb = utility_label_and_blurb(
                    clean_name, domain, href, kind
                )

            kind_counts[kind] = kind_counts.get(kind, 0) + 1
            tools.append(
                {
                    "id": key,
                    "n": display_name,
                    "u": href,
                    "i": icon or f"https://icon.horse/icon/{domain}",
                    "f": fallback or f"https://icon.horse/icon/{domain}",
                    "p": pricing or "free",
                    "t": kind,
                    "c": canon_title,
                    "s": canon_slug,
                    "d": domain,
                    "x": blurb
                    or make_blurb(
                        clean_name,
                        canon_slug,
                        canon_title,
                        pricing or "free",
                        href,
                        domain,
                        kind,
                        external,
                    ),
                }
            )

    assign_category_ranks(tools)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(tools, separators=(",", ":")), encoding="utf-8")
    print(f"Wrote {len(tools)} tools to {OUT_PATH}")
    print("Kinds:", ", ".join(f"{k}={v}" for k, v in sorted(kind_counts.items())))
    print("External blurbs loaded:", len(external))
    print("Sample must-try:")
    for t in tools:
        if t["s"] == "must-try":
            print(f"  {t['n']}: {t['x']}")
    print("Sample 3D Top 3:")
    for t in tools:
        if t.get("s") == "3d" and t.get("r"):
            print(f"  #{t['r']} {t['n']}")


if __name__ == "__main__":
    main()
