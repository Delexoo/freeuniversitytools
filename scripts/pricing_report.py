"""Full pricing audit report using fix_pricing rules."""
import importlib.util
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HTML = ROOT / "student.html"

spec = importlib.util.spec_from_file_location(
    "fix_pricing", ROOT / "scripts" / "fix_pricing.py"
)
fp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fp)

SECTION_RE = re.compile(
    r'data-category="([^"]+)".*?<h3 class="category-title">([^<]+)</h3>.*?'
    r'<div class="category-tools">(.*?)</div>\s*</section>',
    re.DOTALL,
)
LINK_RE = re.compile(
    r'href="([^"]+)"[^>]*data-pricing="([^"]+)"[^>]*>.*?'
    r'<span class="tool-link-name">([^<]+)</span>',
    re.DOTALL,
)


def main():
    html = HTML.read_text(encoding="utf-8")
    rows = []
    by_url = {}
    conflicts = []
    mismatches = []

    for sec in SECTION_RE.finditer(html):
        cat, title, body = sec.group(1), sec.group(2), sec.group(3)
        for m in LINK_RE.finditer(body):
            url, pricing, name = m.group(1), m.group(2), m.group(3).strip()
            rows.append((cat, name, pricing, url))
            key = fp.path_key(url)
            if key in by_url:
                prev = by_url[key]
                if prev[2] != pricing:
                    conflicts.append((name, prev[1], prev[2], pricing, url))
            else:
                by_url[key] = (cat, name, pricing)

            exp = fp.expected_pricing(url)
            if exp and exp != pricing:
                mismatches.append((name, cat, pricing, exp, url))

    print(f"Tools: {len(rows)}")
    print(f"Pricing distribution: {dict(Counter(r[2] for r in rows))}")
    print(f"\nSame URL, different pricing: {len(conflicts)}")
    for c in conflicts[:40]:
        print(f"  {c[0]}: {c[2]} vs {c[3]} | {c[4][:70]}")

    print(f"\nRule mismatches (still wrong): {len(mismatches)}")
    for m in sorted(mismatches, key=lambda x: (x[3], x[0]))[:60]:
        print(f"  [{m[1]}] {m[0]}: {m[2]} -> should be {m[3]}")

    # Freemium tagged free (no rule but suspicious hosts)
    SUSPECT = [
        "notion", "canva", "figma", "slack", "zoom", "dropbox", "spotify",
        "mailchimp", "buffer", "miro", "todoist", "trello", "asana",
        "remove.bg", "smallpdf", "ilovepdf", "deepl", "elevenlabs",
        "runway", "midjourney", "wix", "wordpress", "ynab", "headspace",
        "strava", "quizlet", "zapier", "make.com", "ifttt", "loom",
        "descript", "veed", "capcut", "invideo", "lastpass", "feedly",
        "character.ai", "poe.com", "humata", "chatpdf", "symbolab",
        "mathway", "memrise", "ticktick", "wetransfer", "box.com",
        "later.com", "hootsuite", "mailerlite", "medium.com", "substack",
        "ghost.org", "magoosh", "speechify", "naturalreaders", "suno.com",
        "udio.com", "freepik", "flaticon", "icons8", "pipedream",
        "whimsical", "lucidchart", "splitwise", "myfitnesspal", "doodle",
        "befunky", "fotor", "pixlr", "photoroom", "connectedpapers",
        "elicit", "julius.ai", "penzu", "getform", "formspree",
        "convertio", "sketchup", "spline.design", "gitkraken", "emergent",
        "cursor.com", "cloudconvert", "codesandbox", "stackblitz",
        "docker.com", "render.com", "railway", "supabase", "neon.tech",
        "planetscale", "mongodb", "insomnia", "postman", "replit",
        "leetcode", "codecademy", "datacamp", "skillshare", "udemy",
        "coursera", "edx", "futurelearn", "udacity", "kaggle", "tableau",
        "vercel", "netlify", "heroku", "fly.io", "cloudflare",
    ]
    untagged = []
    for cat, name, pricing, url in rows:
        if pricing != "free":
            continue
        low = url.lower()
        for frag in SUSPECT:
            if frag in low:
                if not fp.expected_pricing(url):
                    untagged.append((name, cat, url, frag))
                break

    print(f"\nFreemium-looking 'free' with no pricing rule: {len(untagged)}")
    for u in untagged[:40]:
        print(f"  [{u[1]}] {u[0]} ({u[3]})")


if __name__ == "__main__":
    main()
