"""Build lightweight category index for the home search page."""
import json
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS = json.loads((ROOT / "data" / "scroll-tools.json").read_text(encoding="utf-8"))
OUT = ROOT / "data" / "home-categories.json"

# Student-facing categories first, then the rest by size.
PRIORITY = [
    "must-try",
    "ai",
    "generative-ai",
    "local-ai",
    "ai-study",
    "ai-homework",
    "ai-voice",
    "ai-audio",
    "ai-video",
    "ai-browser",
    "ai-agents",
    "ai-flows",
    "ai-notetakers",
    "study",
    "courses",
    "open-courseware",
    "exam-prep",
    "test-prep",
    "language-learning",
    "english",
    "math-tools",
    "science-tools",
    "science",
    "mathematics",
    "research",
    "essay-tools",
    "writing",
    "citations",
    "grammar-writing-ai",
    "programming",
    "programming-ai",
    "code-editors",
    "css",
    "web-dev",
    "design",
    "drawing",
    "digital-art",
    "logo-makers",
    "branding",
    "fonts",
    "typography",
    "icons",
    "illustrations",
    "mockups",
    "templates",
    "gradients",
    "css-generators",
    "pdf",
    "ai-pdf-chat",
    "image",
    "video",
    "audio",
    "gif-converters",
    "converters",
    "compressors",
    "security",
    "vpn",
    "privacy-tools",
    "cybersecurity",
    "productivity",
    "focus",
    "time-tracking",
    "todo-list",
    "note-taking",
    "notepad",
    "bookmarks",
    "rss",
    "calendars",
    "scheduling",
    "presentation",
    "spreadsheets",
    "data-tools",
    "data-science",
    "notebooks",
    "diagrams",
    "flowcharts",
    "mind-mapping",
    "online-whiteboard",
    "resume",
    "career",
    "remote-jobs",
    "internships",
    "scholarships",
    "financial-aid",
    "student-discounts",
    "email",
    "email-marketing",
    "file-sharing",
    "cloud",
    "cloud-sync",
    "backup",
    "music",
    "podcasts",
    "music-production",
    "screen-recording",
    "browser-extensions",
    "chrome-extension",
    "api-clients",
    "api-platforms",
    "api-mocking",
    "databases",
    "deployment",
    "devops",
    "containers",
    "git-hosting",
    "git-tools",
    "regex",
    "dev-tools",
    "encode",
    "hash-tools",
    "diff-tools",
    "format-tools",
    "latex",
    "math-docs",
    "cheat-sheets",
    "dev-docs",
    "markdown-tools",
    "translation",
    "accessibility",
    "typing-practice",
    "3d",
    "animation",
    "maps",
    "gis",
    "speed-test",
    "network-tools",
    "cms",
    "blogging",
    "website-builders",
    "social-media",
    "creator-tools",
    "browser-games",
    "finance",
    "budgeting",
    "wellness",
    "health-fitness",
    "collaboration",
    "automation",
    "hackathons",
    "events",
    "tech-communities",
    "open-source",
    "free-books",
    "ebooks",
    "textbooks",
    "immersive-reader",
    "free-movies",
    "live-streaming",
    "free-stuff",
    "stock-photos",
    "stock-video",
    "stock-audio",
    "placeholders",
    "lorem-ipsum",
    "geography",
    "history",
    "journaling",
    "all-in-one-tools",
    "utilities",
    "github-powerhouses",
    "osint-tools",
    "osint-ai-tools",
    "osint-username",
    "osint-email-address",
    "osint-domain-name",
    "osint-image-search",
    "osint-video-search",
    "osint-document-search",
    "osint-maps-search",
    "osint-location-search",
    "osint-privacy-tools",
    "osint-safety-tools",
]


def main() -> None:
    cats = OrderedDict()
    for t in TOOLS:
        slug = t.get("s") or "utilities"
        if slug not in cats:
            cats[slug] = {
                "slug": slug,
                "name": t.get("c") or slug,
                "count": 0,
                "icon": t.get("i") or t.get("f") or "",
                "domain": t.get("d") or "",
            }
        cats[slug]["count"] += 1
        icon = t.get("i") or ""
        if icon and "FreeUniversityTools.png" not in icon:
            if (
                not cats[slug]["icon"]
                or "FreeUniversityTools.png" in (cats[slug]["icon"] or "")
            ):
                cats[slug]["icon"] = icon

    ordered = []
    seen = set()
    for slug in PRIORITY:
        if slug in cats and slug not in seen:
            ordered.append(cats[slug])
            seen.add(slug)

    rest = sorted(
        (c for s, c in cats.items() if s not in seen),
        key=lambda c: (-c["count"], c["name"].lower()),
    )
    ordered.extend(rest)

    OUT.write_text(json.dumps(ordered, separators=(",", ":")), encoding="utf-8")
    print(f"Wrote {len(ordered)} categories to {OUT}")


if __name__ == "__main__":
    main()
