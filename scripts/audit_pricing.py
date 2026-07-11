"""Audit and report pricing tag distribution + conflicts in student.html."""
import re
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

HTML = Path(__file__).resolve().parent.parent / "student.html"
LINK_RE = re.compile(
    r'<a\s+href="([^"]+)"[^>]*data-pricing="([^"]+)"[^>]*>.*?<span class="tool-link-name">([^<]+)</span></a>',
    re.DOTALL,
)

VALID = {"free", "free-tier", "limited", "paid"}

FREEMIUM = [
    "notion.so", "canva.com", "figma.com", "slack.com", "zoom.us", "dropbox.com",
    "spotify.com", "grammarly.com", "quillbot.com", "chatgpt.com", "claude.ai",
    "perplexity.ai", "gemini.google", "copilot.microsoft", "replit.com",
    "leetcode.com", "postman.com", "supabase.com", "neon.tech", "vercel.com",
    "netlify.com", "mailchimp.com", "buffer.com", "calendly.com", "miro.com",
    "evernote.com", "todoist.com", "trello.com", "asana.com",
    "remove.bg", "smallpdf.com", "ilovepdf.com", "deepl.com", "overleaf.com",
    "elevenlabs.io", "runway.com", "midjourney.com",
    "github.com/features/copilot", "tabnine.com", "codeium.com",
    "wix.com", "squarespace.com", "wordpress.com", "carrd.co",
    "ynab.com", "headspace.com", "calm.com", "strava.com",
    "brainscape.com", "quizlet.com", "chegg.com", "coursera.org",
    "udemy.com", "skillshare.com", "linkedin.com/learning",
    "zapier.com", "make.com", "ifttt.com", "n8n.io",
    "storyblocks.com", "adobe.com", "sketch.com", "framer.com",
    "loom.com", "descript.com", "veed.io", "capcut.com",
    "invideo.io", "animaker.com", "bitwarden.com",
    "1password.com", "lastpass.com", "dashlane.com",
    "mongodb.com", "planetscale.com", "turso.tech",
    "feedly.com", "raindrop.io", "instapaper.com",
    "character.ai", "poe.com", "you.com", "pi.ai",
    "mem.ai", "reflect.app", "craft.do", "capacities.io",
    "humata.ai", "chatpdf.com", "pdf.ai", "lightpdf.com",
    "symbolab.com", "mathway.com", "wolframalpha.com",
    "geoguessr.com", "duolingo.com", "memrise.com", "babbel.com",
    "proton.me", "ticktick.com", "any.do",
    "wetransfer.com", "box.com", "icedrive.net",
    "backblaze.com", "idrive.com", "pcloud.com",
    "later.com", "metricool.com", "hootsuite.com",
    "mailerlite.com", "brevo.com", "sendpulse.com", "mailjet.com",
    "ghost.org", "substack.com", "medium.com",
    "dify.ai", "flowiseai.com", "langflow.org",
    "gradescope.com", "magoosh.com", "photomath.com",
    "naturalreaders.com", "speechify.com", "murf.ai",
    "suno.com", "udio.com", "lovo.ai", "play.ht",
    "freepik.com", "flaticon.com", "icons8.com", "iconscout.com",
    "placeit.net", "smartmockups.com", "looka.com",
    "soundtrap.com", "soundation.com", "bandlab.com",
    "scholarshipowl.com", "cappex.com",
    "pipedream.com", "activepieces.com",
    "whimsical.com", "mindmeister.com", "coggle.it", "mindomo.com",
    "lucidchart.com", "smartdraw.com", "eraser.io",
    "splitwise.com", "waveapps.com", "goodbudget.com",
    "myfitnesspal.com",
    "teams.microsoft.com", "whereby.com",
    "doodle.com", "cal.com",
    "4shared.com", "mediafire.com",
    "befunky.com", "fotor.com", "pixlr.com", "photoroom.com",
    "stylar.ai", "cleanup.pictures", "upscale.media",
    "connectedpapers.com", "litmaps.com", "scite.ai", "elicit.org",
    "julius.ai", "chatcsv.com", "phind.com",
    "replika.com", "journey.cloud", "penzu.com", "dayoneapp.com",
    "zoho.com", "getform.io", "formspree.io",
    "convertio.co", "aspose.app", "pdf2go.com",
    "sketchup.com", "spline.design",
    "drawsql.app", "dbdiagram.io",
    "sophia.org", "britannica.com",
    "debuggex.com", "accessibilitychecker.org",
    "gitkraken.com", "gitlab.com",
    "sumopaint.com", "emergent.sh",
]

PAID_ONLY = [
    "chegg.com", "coursehero.com", "studocu.com", "bartleby.com",
    "adobe.com/acrobat", "microsoft.com/microsoft-365/buy",
]


def norm_url(url: str) -> str:
    p = urlparse(url.strip().rstrip("/"))
    return f"{(p.netloc or '').lower().replace('www.', '')}{p.path.rstrip('/').lower()}"


def main() -> None:
    html = HTML.read_text(encoding="utf-8")
    by_url: dict[str, tuple[str, str, str]] = {}
    conflicts = []
    invalid = []
    all_links = []

    for m in LINK_RE.finditer(html):
        url, pricing, name = m.group(1), m.group(2), m.group(3).strip()
        all_links.append((url, pricing, name))
        if pricing not in VALID:
            invalid.append((name, pricing, url))
        key = norm_url(url)
        if key in by_url:
            prev = by_url[key]
            if prev[1] != pricing:
                conflicts.append((name, prev[2], prev[1], pricing, url))
        else:
            by_url[key] = (url, pricing, name)

    print(f"Total links: {len(all_links)}")
    print(f"Unique URLs: {len(by_url)}")
    print(f"Pricing distribution: {dict(Counter(p for _, p, _ in all_links))}")
    print(f"Invalid tags: {len(invalid)}")
    for row in invalid[:20]:
        print(f"  {row}")
    print(f"URL conflicts (same URL, different pricing): {len(conflicts)}")
    for row in conflicts:
        print(f"  {row[0]}: {row[2]} vs {row[3]} ({row[4]})")

    suspicious_free = []
    for url, pricing, name in all_links:
        if pricing != "free":
            continue
        low = url.lower()
        for frag in FREEMIUM:
            if frag in low:
                suspicious_free.append((name, url, frag))
                break

    print(f"\nWell-known freemium tagged as 'free' (sample): {len(suspicious_free)}")
    for row in suspicious_free[:40]:
        print(f"  {row[0]} -> {row[1]} (match: {row[2]})")
    if len(suspicious_free) > 40:
        print(f"  ... and {len(suspicious_free) - 40} more")

    suspicious_paid_wrong = []
    for url, pricing, name in all_links:
        if pricing in ("free", "free-tier"):
            low = url.lower()
            for frag in PAID_ONLY:
                if frag in low:
                    suspicious_paid_wrong.append((name, pricing, url))

    print(f"\nLikely paid-only tagged free/free-tier: {len(suspicious_paid_wrong)}")
    for row in suspicious_paid_wrong:
        print(f"  {row}")


if __name__ == "__main__":
    main()
