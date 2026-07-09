"""Audit pricing + placement; apply fix_pricing rules to student.html."""
import re
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
HTML_PATH = ROOT / "student.html"

SECTION_RE = re.compile(
    r'<section class="tool-category"[^>]*data-category="([^"]+)">.*?'
    r'<h3 class="category-title">([^<]+)</h3>.*?'
    r'<div class="category-tools">(.*?)</div>\s*</section>',
    re.DOTALL,
)
LINK_RE = re.compile(
    r'(<a\s+href="([^"]+)"[^>]*data-pricing=")([^"]+)("([^>]*)>.*?'
    r'<span class="tool-link-name">([^<]+)</span></a>)',
    re.DOTALL,
)

VALID = {"free", "free-tier", "limited", "paid"}


def host_key(url: str) -> str:
    return urlparse(url.strip()).netloc.lower().replace("www.", "")


def path_key(url: str) -> str:
    p = urlparse(url.strip().rstrip("/"))
    h = p.netloc.lower().replace("www.", "")
    return f"{h}{p.path.rstrip('/').lower()}"


def norm_url(url: str) -> str:
    return path_key(url)


EXACT = {
    "quillbot.com/word-counter": "free-tier",
    "github.com/features/copilot": "free-tier",
    "langflow.org": "free",
    "flowiseai.com": "free",
    "ollama.com": "free",
    "linkedin.com/learning": "paid",
    "lynda.com": "paid",
    "penpot.app": "free",
}

HOST = {
    "chegg.com": "paid",
    "coursehero.com": "paid",
    "studocu.com": "paid",
    "bartleby.com": "paid",
    "lynda.com": "paid",
    "pluralsight.com": "paid",
    "youlearn.ai": "paid",
    "babbel.com": "paid",
    "1password.com": "paid",
    "tresorit.com": "paid",
    "roamresearch.com": "paid",
    "notion.so": "free-tier",
    "canva.com": "free-tier",
    "figma.com": "free-tier",
    "slack.com": "free-tier",
    "zoom.us": "free-tier",
    "dropbox.com": "free-tier",
    "spotify.com": "free-tier",
    "grammarly.com": "limited",
    "quillbot.com": "limited",
    "chatgpt.com": "free-tier",
    "chat.openai.com": "free-tier",
    "claude.ai": "free-tier",
    "perplexity.ai": "free-tier",
    "gemini.google.com": "free-tier",
    "copilot.microsoft.com": "free-tier",
    "replit.com": "free-tier",
    "leetcode.com": "free-tier",
    "postman.com": "free-tier",
    "supabase.com": "free-tier",
    "neon.tech": "free-tier",
    "vercel.com": "free-tier",
    "netlify.com": "free-tier",
    "calendly.com": "free-tier",
    "cal.com": "free-tier",
    "miro.com": "free-tier",
    "evernote.com": "free-tier",
    "todoist.com": "free-tier",
    "bitwarden.com": "free-tier",
    "coursera.org": "free-tier",
    "udemy.com": "free-tier",
    "skillshare.com": "limited",
    "linkedin.com": "free-tier",
    "zapier.com": "free-tier",
    "make.com": "free-tier",
    "ifttt.com": "free-tier",
    "n8n.io": "free-tier",
    "loom.com": "free-tier",
    "descript.com": "free-tier",
    "veed.io": "free-tier",
    "capcut.com": "free-tier",
    "invideo.io": "free-tier",
    "dify.ai": "free-tier",
    "geoguessr.com": "free-tier",
    "duolingo.com": "free-tier",
    "wolframalpha.com": "limited",
    "cluely.com": "limited",
    "uncensored.chat": "limited",
    "codecademy.com": "limited",
    "datacamp.com": "limited",
    "dataquest.io": "limited",
    "emergent.sh": "free-tier",
    "manus.im": "free-tier",
    "plausible.io": "free-tier",
    "penpot.app": "free",
    "animejs.com": "free",
    "motion.dev": "free",
    "kokonutui.com": "free",
    "bklit.com": "free",
    "khanacademy.org": "free",
    "openstax.org": "free",
    "freecodecamp.org": "free",
    "edx.org": "free-tier",
    "futurelearn.com": "free-tier",
    "udacity.com": "free-tier",
    "obsidian.md": "free",
    "joplinapp.org": "free",
    "zotero.org": "free",
    "fmhy.net": "free",
    "github.com": "free",
    "render.com": "free-tier",
    "railway.app": "free-tier",
    "docker.com": "free-tier",
    "codesandbox.io": "free-tier",
    "stackblitz.com": "free-tier",
    "kaggle.com": "free-tier",
    "colab.research.google.com": "free",
    "proton.me": "free-tier",
    "protonvpn.com": "free-tier",
}

FREE_HOSTS = {
    "gutenberg.org",
    "openstax.org",
    "archive.org",
    "wikipedia.org",
    "mdn.mozilla.org",
    "developer.mozilla.org",
    "w3schools.com",
}

# domain fragment -> acceptable categories (first is preferred)
DOMAIN_HOME = {
    "yt-dlp": {"video", "utilities", "github-powerhouses"},
    "bitwarden": {"security", "vpn-security", "github-powerhouses"},
    "appflowy": {"note-taking", "notepad", "productivity", "github-powerhouses"},
    "penpot": {"design", "github-powerhouses"},
    "plausible": {"open-source", "github-powerhouses", "utilities"},
    "whisper": {"ai-voice", "audio", "local-ai", "github-powerhouses"},
    "cal.com": {"scheduling", "github-powerhouses", "deployment"},
    "n8n": {"automation", "ai-agents", "github-powerhouses"},
    "ollama": {"local-ai", "github-powerhouses", "generative-ai"},
    "fooocus": {"generative-ai", "local-ai", "github-powerhouses"},
    "manus.im": {"ai-browser", "ai-agents", "programming-ai"},
    "animejs.com": {"css-web-dev", "3d-animation"},
    "motion.dev": {"css-web-dev", "3d-animation"},
    "kokonutui.com": {"design", "css-web-dev", "open-source"},
    "bklit.com": {"design", "css-web-dev", "data-science"},
    "maigret": {"osint-username", "osint-tools", "github-powerhouses"},
    "firecrawl": {"programming-ai", "ai-agents", "github-powerhouses"},
    "browser-use": {"ai-agents", "programming-ai", "github-powerhouses"},
    "crewai": {"ai-agents", "github-powerhouses"},
    "langchain": {"ai-agents", "programming-ai", "github-powerhouses"},
}


def expected_pricing(url: str) -> str | None:
    pk = path_key(url)
    if pk in EXACT:
        return EXACT[pk]

    host = host_key(url)
    if host in FREE_HOSTS:
        return "free"
    if host in HOST:
        return HOST[host]
    if host == "github.com":
        return "free"

    parts = host.split(".")
    for i in range(len(parts) - 1):
        parent = ".".join(parts[i:])
        if parent in HOST:
            return HOST[parent]

    return None


def audit(html: str):
    by_url: dict[str, tuple] = {}
    conflicts = []
    invalid = []
    freemium_as_free = []
    all_rows = []

    for sec in SECTION_RE.finditer(html):
        cat, title, body = sec.group(1), sec.group(2).strip(), sec.group(3)
        for m in LINK_RE.finditer(body):
            url, pricing, name = m.group(2), m.group(3), m.group(5).strip()
            all_rows.append((cat, title, name, pricing, url))
            if pricing not in VALID:
                invalid.append((name, pricing, url))
            key = norm_url(url)
            if key in by_url:
                prev = by_url[key]
                if prev[3] != pricing:
                    conflicts.append((name, prev[3], pricing, url, cat, prev[0]))
            else:
                by_url[key] = (cat, title, name, pricing)

    placement_issues = []
    for cat, title, name, pricing, url in all_rows:
        low = url.lower()
        for frag, homes in DOMAIN_HOME.items():
            if frag in low or frag in name.lower():
                if cat not in homes:
                    placement_issues.append((name, cat, title, sorted(homes), url))
                break

    suspicious_free = []
    for _, _, name, pricing, url in all_rows:
        exp = expected_pricing(url)
        if exp and exp != pricing:
            suspicious_free.append((name, pricing, exp, url))

    return {
        "total": len(all_rows),
        "distribution": dict(Counter(r[3] for r in all_rows)),
        "invalid": invalid,
        "conflicts": conflicts,
        "pricing_mismatch": suspicious_free,
        "placement": placement_issues,
    }


def apply_pricing_fixes(html: str) -> tuple[str, list]:
    changes = []

    def replacer(m):
        prefix, url, current, suffix, _, name = m.groups()
        expected = expected_pricing(url)
        if expected and expected != current:
            changes.append((name.strip(), current, expected, url))
            return f"{prefix}{expected}{suffix}"
        return m.group(0)

    new_html = LINK_RE.sub(replacer, html)
    return new_html, changes


def main():
    html = HTML_PATH.read_text(encoding="utf-8")
    before = audit(html)
    print("=== BEFORE ===")
    print(f"Tools: {before['total']}")
    print(f"Pricing: {before['distribution']}")
    print(f"Invalid tags: {len(before['invalid'])}")
    print(f"Same-URL conflicts: {len(before['conflicts'])}")
    print(f"Rule mismatches: {len(before['pricing_mismatch'])}")
    print(f"Placement flags: {len(before['placement'])}")

    new_html, changes = apply_pricing_fixes(html)
    if changes:
        HTML_PATH.write_text(new_html, encoding="utf-8", newline="\n")
        print(f"\n=== APPLIED {len(changes)} PRICING FIXES ===")
        for name, old, new, url in sorted(changes, key=lambda x: x[0].lower())[:80]:
            print(f"  {name}: {old} -> {new}")
        if len(changes) > 80:
            print(f"  ... and {len(changes) - 80} more")

    after = audit(HTML_PATH.read_text(encoding="utf-8"))
    print("\n=== AFTER ===")
    print(f"Pricing: {after['distribution']}")
    print(f"Rule mismatches remaining: {len(after['pricing_mismatch'])}")
    if after["pricing_mismatch"][:25]:
        print("Remaining mismatches (no rule):")
        for row in after["pricing_mismatch"][:25]:
            print(f"  {row[0]}: {row[1]} (rule would be {row[2]})")

    if after["conflicts"]:
        print("\nSame-URL pricing conflicts:")
        for row in after["conflicts"][:20]:
            print(f"  {row[0]}: {row[1]} vs {row[2]} in {row[4]}/{row[5]}")

    if after["placement"]:
        print("\nPlacement notes (may be intentional duplicates):")
        for row in after["placement"][:30]:
            print(f"  [{row[1]}] {row[0]} -> also fits {row[3]}")


if __name__ == "__main__":
    main()
