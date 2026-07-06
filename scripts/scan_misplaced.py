"""Report tools that look misplaced based on domain -> expected category rules."""
import re
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlparse

HTML = Path(__file__).resolve().parent.parent / "student.html"
SECTION_RE = re.compile(
    r'data-category="([^"]+)">.*?<div class="category-tools">(.*?)</div>\s*</section>',
    re.DOTALL,
)
LINK_RE = re.compile(r'href="([^"]+)".*?<span class="tool-link-name">([^<]+)</span>', re.DOTALL)

# domain fragment -> primary category (flag if in other category unless in ALLOW)
PRIMARY = {
    "supabase.com": "databases",
    "neon.tech": "databases",
    "postman.com": "api-testing",
    "unsplash.com": "stock-media",
    "pexels.com": "stock-media",
    "keepass": "security",
    "bitwarden": "security",
    "jdoodle.com": "code-editors",
    "codesandbox": "code-editors",
    "replit.com": "programming",
    "canva.com": "design",
    "notion.so": "ai-notetakers",
    "duolingo": "language-learning",
    "khanacademy": "courses",
    "ollama.com": "local-ai",
    "docker.com": "devops-containers",
    "figma.com": "design",
    "overleaf": "latex-docs",
    "zotero": "writing",
    "mint.com": "finance-budgeting",
    "spotify.com": "music-podcasts",
    "twitch.tv": "live-streaming",
    "obsproject": "screen-recording",
    "grammarly": "english",
    "quillbot": "essay-tools",
}

ALLOW_OTHER = {
    "khanacademy": {"courses", "study", "open-courseware", "math-science", "exam-test-prep", "science"},
    "canva.com": {"design", "creator-tools", "presentation", "social-media", "online-whiteboard"},
    "notion.so": {"ai-notetakers", "notepad", "productivity", "note-taking", "spreadsheets"},
    "replit.com": {"programming", "code-editors"},
    "ollama.com": {"local-ai", "github-powerhouses"},
    "claude.ai": {"research", "mathematics", "programming-ai", "analytical", "conversation", "ai", "english"},
    "fmhy.net": {"must-try", "free-stuff"},
    "wolframalpha": {"math-science", "mathematics", "spreadsheets"},
    "coursera.org": {"courses", "study", "open-courseware"},
    "w3schools": {"courses", "programming", "css-web-dev"},
    "developer.mozilla.org": {"courses", "programming", "css-web-dev"},
    "miro.com": {"mind-mapping", "collaboration", "online-whiteboard"},
    "app.diagrams.net": {"mind-mapping", "diagramming", "online-whiteboard"},
    "github.com/gorhill": {"must-try", "browser-extensions", "chrome-extension", "vpn-security"},
}


def main():
    html = HTML.read_text(encoding="utf-8")
    issues = []
    dupes = defaultdict(list)

    for m in SECTION_RE.finditer(html):
        cat = m.group(1)
        for lm in LINK_RE.finditer(m.group(2)):
            url, name = lm.group(1), lm.group(2).strip()
            host = urlparse(url).netloc.lower()
            dupes[url.lower()].append((cat, name))

            for frag, primary in PRIMARY.items():
                if frag in url.lower() or frag in host:
                    allowed = ALLOW_OTHER.get(frag, {primary})
                    if cat not in allowed:
                        issues.append((name, cat, primary, url))
                    break

    print("=== Likely misplaced (heuristic) ===")
    for row in issues:
        print(f"  {row[0]} in [{row[1]}] -> should be [{row[2]}]")

    print(f"\nTotal flagged: {len(issues)}")

    print("\n=== Cross-category duplicates (sample) ===")
    multi = [(u, locs) for u, locs in dupes.items() if len(locs) > 1]
    print(f"URLs in multiple categories: {len(multi)}")
    for u, locs in sorted(multi, key=lambda x: -len(x[1]))[:15]:
        print(f"  {locs[0][1]}: {[c for c, _ in locs]}")


if __name__ == "__main__":
    main()
