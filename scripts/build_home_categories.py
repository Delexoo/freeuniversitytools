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
    "ai-voice",
    "ai-video",
    "ai-browser",
    "ai-agents",
    "ai-flows",
    "study",
    "courses",
    "open-courseware",
    "language-learning",
    "english",
    "science",
    "mathematics",
    "research",
    "writing",
    "citations",
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
    "image",
    "video",
    "audio",
    "gif-converters",
    "compressors",
    "security",
    "vpn",
    "privacy-tools",
    "cybersecurity",
    "productivity",
    "focus",
    "time-tracking",
    "todo-list",
    "notepad",
    "bookmarks",
    "rss",
    "calendars",
    "scheduling",
    "presentation",
    "spreadsheets",
    "data-tools",
    "data-science",
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
    "backup",
    "music",
    "podcasts",
    "music-production",
    "screen-recording",
    "browser-extensions",
    "api-clients",
    "api-platforms",
    "api-mocking",
    "databases",
    "deployment",
    "devops",
    "containers",
    "source-code-repos",
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
    "osint-safety-tools",
]


def main() -> None:
    cats = OrderedDict()
    top_by_cat: dict[str, list[dict]] = {}
    for t in TOOLS:
        slug = t.get("s") or "utilities"
        if slug not in cats:
            cats[slug] = {
                "slug": slug,
                "name": t.get("c") or slug,
                "count": 0,
                "icon": t.get("i") or t.get("f") or "",
                "domain": t.get("d") or "",
                "top3": [],
            }
        cats[slug]["count"] += 1
        rank = t.get("r")
        if rank in (1, 2, 3):
            top_by_cat.setdefault(slug, []).append(t)
        icon = t.get("i") or ""
        if icon and "FreeUniversityTools.png" not in icon:
            if (
                not cats[slug]["icon"]
                or "FreeUniversityTools.png" in (cats[slug]["icon"] or "")
            ):
                cats[slug]["icon"] = icon

    for slug, ranked in top_by_cat.items():
        ranked.sort(key=lambda t: t.get("r") or 99)
        cats[slug]["top3"] = [
            {
                "n": t.get("n") or "",
                "u": t.get("u") or "",
                "i": t.get("i") or t.get("f") or "",
                "r": t.get("r"),
                "d": t.get("d") or "",
            }
            for t in ranked[:3]
        ]

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
    with_top = sum(1 for c in ordered if c.get("top3"))
    print(f"Categories with Top 3: {with_top}")


if __name__ == "__main__":
    main()
