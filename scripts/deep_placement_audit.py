"""Deep audit: flag tools whose domain strongly conflicts with their section."""
import re
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlparse

HTML = Path(__file__).resolve().parent.parent / "student.html"
SECTION_RE = re.compile(
 r'data-category="([^"]+)">.*?<h3[^>]*>([^<]+)</h3>.*?<div class="category-tools">(.*?)</div>\s*</section>',
 re.DOTALL,
)
LINK_RE = re.compile(r'href="([^"]+)".*?<span class="tool-link-name">([^<]+)</span>', re.DOTALL)

# domain fragment -> set of acceptable categories
DOMAIN_HOME = {
 "supabase.com": {"databases"},
 "neon.tech": {"databases"},
 "planetscale.com": {"databases"},
 "turso.tech": {"databases"},
 "mongodb.com": {"databases"},
 "dbdiagram.io": {"databases"},
 "sqliteonline.com": {"databases"},
 "drawsql.app": {"databases"},
 "postman.com": {"api-testing"},
 "hoppscotch.io": {"api-testing"},
 "insomnia.rest": {"api-testing"},
 "reqbin.com": {"api-testing"},
 "editor.swagger.io": {"api-testing"},
 "unsplash.com": {"stock-media"},
 "pexels.com": {"stock-media"},
 "pixabay.com": {"stock-media"},
 "coverr.co": {"stock-media"},
 "mixkit.co": {"stock-media"},
 "videvo.net": {"stock-media"},
 "freesound.org": {"stock-media", "music-podcasts"},
 "keepassxc.org": {"security"},
 "keepass.info": {"security"},
 "bitwarden.com": {"security"},
 "passwords.google.com": {"security"},
 "jdoodle.com": {"code-editors"},
 "codesandbox.io": {"code-editors"},
 "replit.com": {"programming", "code-editors"},
 "leetcode.com": {"programming"},
 "exercism.org": {"programming"},
 "codewars.com": {"programming"},
 "scratch.mit.edu": {"programming"},
 "canva.com": {"design", "creator-tools", "presentation", "social-media"},
 "figma.com": {"design"},
 "notion.so": {"ai-notetakers", "notepad", "productivity", "note-taking"},
 "duolingo.com": {"language-learning"},
 "khanacademy.org": {"courses", "study", "math-science", "open-courseware", "exam-test-prep"},
 "ollama.com": {"local-ai", "github-powerhouses"},
 "docker.com": {"devops-containers"},
 "overleaf.com": {"latex-docs"},
 "zotero.org": {"writing", "essay-tools"},
 "mendeley.com": {"writing", "essay-tools"},
 "open.spotify.com": {"music-podcasts"},
 "music.youtube.com": {"music-podcasts"},
 "soundcloud.com": {"music-podcasts"},
 "bandcamp.com": {"music-podcasts"},
 "twitch.tv": {"live-streaming"},
 "obsproject.com": {"screen-recording"},
 "desmos.com": {"math-science", "mathematics"},
 "geogebra.org": {"math-science", "mathematics"},
 "phet.colorado.edu": {"math-science", "science"},
 "wolframalpha.com": {"math-science", "mathematics", "spreadsheets"},
 "mail.google.com": {"email"},
 "proton.me": {"email"},
 "calendar.google.com": {"scheduling"},
 "calendly.com": {"scheduling"},
 "cal.com": {"scheduling"},
 "fonts.google.com": {"fonts-typography"},
 "dafont.com": {"fonts-typography"},
 "pages.github.com": {"website-builders"},
 "vercel.com": {"website-builders", "devops-containers"},
 "netlify.com": {"website-builders", "devops-containers"},
 "carrd.co": {"website-builders"},
 "wordpress.com": {"website-builders"},
 "tools.pdf24.org": {"all-in-one-tools", "pdf"},
 "convertio.co": {"all-in-one-tools", "converters"},
 "goblin.tools": {"study", "productivity"},
 "brainscape.com": {"study", "flashcards"},
 "alternativeto.net": {"free-stuff", "must-try"},
 "producthunt.com": {"free-stuff"},
 "fmhy.net": {"free-stuff", "must-try"},
 "grammarly.com": {"english", "essay-tools", "chrome-extension", "grammar-writing-ai"},
 "deepl.com/write": {"grammar-writing-ai"},
 "deepl.com/translator": {"translation"},
 "chat.openai.com": {"research", "ai", "conversation", "english", "mathematics"},
 "claude.ai": {"research", "ai", "conversation", "english", "mathematics", "programming-ai", "analytical"},
 "perplexity.ai": {"research", "ai", "analytical", "ai-study-tools"},
 "miro.com": {"mind-mapping", "collaboration", "online-whiteboard"},
 "app.diagrams.net": {"mind-mapping", "diagramming", "online-whiteboard"},
 "github.com/gorhill": {"browser-extensions", "chrome-extension", "must-try", "vpn-security"},
 "wetransfer.com": {"file-sharing"},
 "pixeldrain.com": {"file-sharing"},
 "bing.com/images/create": {"generative-ai", "image"},
 "ideogram.ai": {"generative-ai", "image"},
 "playground.com": {"generative-ai", "image"},
 "leonardo.ai": {"generative-ai", "image"},
 "huggingface.co": {"generative-ai", "github-powerhouses", "local-ai"},
 "slack.com": {"collaboration"},
 "discord.com": {"collaboration"},
 "zoom.us": {"collaboration", "screen-recording"},
 "buffer.com": {"social-media"},
 "linktr.ee": {"social-media"},
 "capcut.com": {"creator-tools", "video"},
 "invideo.io": {"creator-tools", "video"},
}

# categories that should NOT contain programming hosts
NON_CODE = {
 "stock-media", "fonts-typography", "color-tools", "health-wellness",
 "finance-budgeting", "music-podcasts", "language-learning", "translation",
 "scheduling", "email", "file-sharing", "stock-media", "vpn-security",
}
CODE_FRAGS = [
 "replit.com", "leetcode.com", "exercism.org", "codewars.com", "scratch.mit.edu",
 "jdoodle.com", "codesandbox", "supabase.com", "neon.tech", "postman.com",
]


def host_key(url):
 return urlparse(url).netloc.lower().replace("www.", "")


def main():
 html = HTML.read_text(encoding="utf-8")
 wrong = []
 by_cat = defaultdict(list)

 for m in SECTION_RE.finditer(html):
 cat, title, body = m.group(1), m.group(2).strip(), m.group(3)
 for lm in LINK_RE.finditer(body):
 url, name = lm.group(1), lm.group(2).strip()
 host = host_key(url)
 path = urlparse(url).path.lower()

 for frag, homes in DOMAIN_HOME.items():
 if frag in url.lower() or frag in host or frag in path:
 if cat not in homes:
 wrong.append((name, cat, title, sorted(homes), url))
 break

 if cat in NON_CODE:
 for cf in CODE_FRAGS:
 if cf in url.lower() or cf in host:
 if not any((name, cat) == (w[0], w[1]) for w in wrong):
 wrong.append((name, cat, title, ["(code/dev tool)"], url))
 break

 by_cat[cat].append(name)

 print("=== Domain conflicts (should fix) ===")
 for row in sorted(wrong, key=lambda r: (r[1], r[0])):
 print(f" [{row[1]}] {row[0]} (section: {row[2]}) -> belongs in {row[3]}")

 print(f"\nTotal conflicts: {len(wrong)}")
 print(f"Categories: {len(by_cat)}, Tools: {sum(len(v) for v in by_cat.values())}")


if __name__ == "__main__":
 main()
