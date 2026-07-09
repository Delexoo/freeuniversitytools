"""Conservative placement fix: remove from wrong categories, add to correct ones. No global dedupe."""
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
HTML_PATH = ROOT / "student.html"

SECTION_RE = re.compile(
 r'(<section class="tool-category"[^>]*data-category="([^"]+)">.*?<div class="category-tools">)(.*?)(</div>\s*</section>)',
 re.DOTALL,
)
LINK_RE = re.compile(
 r'<a\s+href="([^"]+)"[^>]*data-pricing="([^"]+)"[^>]*>.*?<span class="tool-link-name">([^<]+)</span></a>',
 re.DOTALL,
)


def norm_url(url):
 p = urlparse(url.strip().rstrip("/"))
 return f"{(p.netloc or '').lower().replace('www.', '')}{p.path.rstrip('/').lower()}"


def link(url, name, pricing="free", github=None):
 domain = urlparse(url).netloc.replace("www.", "")
 if github:
 icon = fb = f"https://github.com/{github}.png?size=64"
 else:
 icon = f"https://www.google.com/s2/favicons?domain={domain}&amp;sz=128"
 fb = f"https://www.google.com/s2/favicons?domain={domain}&sz=128"
 return (
 f' <a href="{url}" target="_blank" rel="noopener noreferrer" class="tool-link" data-pricing="{pricing}">'
 f'<img src="{icon}" data-fallback="{fb}" alt="" class="tool-link-icon">'
 f'<span class="tool-link-name">{name}</span></a>\n'
 )


# Remove URL fragments from these categories only
REMOVE_FROM = {
 "databases": ["keepassxc.org", "keepass.info", "passwords.google.com"],
 "api-testing": ["tools.pdf24.org", "convertio.co", "onlinetools.com", "products.aspose.app"],
 "social-media": ["canva.com", "capcut.com", "invideo.io"],
 "finance-budgeting": ["bing.com/images/create", "ideogram.ai", "playground.com", "huggingface.co", "leonardo.ai"],
 "health-wellness": ["goblin.tools", "brainscape.com", "cram.com", "sophia.org"],
 "collaboration": ["replit.com", "leetcode.com", "exercism.org", "codewars.com", "scratch.mit.edu"],
 "scheduling": ["mail.google.com", "proton.me/mail", "web3forms.com", "getform.io", "jdoodle.com"],
 "mind-mapping": ["alternativeto.net", "producthunt.com", "fmhy.net/internet-tools", "fmhy.net/system-tools"],
 "file-sharing": ["open.spotify.com", "music.youtube.com", "soundcloud.com", "bandcamp.com"],
 "fonts-typography": ["desmos.com", "geogebra.org", "phet.colorado.edu", "wolframalpha.com"],
 "color-tools": ["pages.github.com", "vercel.com", "netlify.com", "carrd.co", "wordpress.com"],
 "stock-media": [
 "supabase.com", "neon.tech", "dbdiagram.io", "sqliteonline.com", "drawsql.app",
 "planetscale.com", "turso.tech", "mongodb.com",
 ],
 "browser-extensions": ["postman.com", "hoppscotch.io", "insomnia.rest", "reqbin.com", "editor.swagger.io"],
 "writing": ["chat.qwen.ai"],
 "study": ["desmos.com"], # belongs in math-science
 "translation": ["deepl.com/write"], # belongs in grammar-writing-ai
 "open-source": ["alternativeto.net"],
 "vpn-security": ["github.com/gorhill/ublock"], # keep in browser-extensions + must-try
}

# Add to category if missing (after removals)
ADD = {
 "security": [
 ("https://keepassxc.org/", "KeePassXC"),
 ("https://keepass.info/", "KeePass"),
 ("https://passwords.google.com/", "Google Passwords", "free-tier"),
 ("https://bitwarden.com/", "Bitwarden", "free-tier"),
 ],
 "all-in-one-tools": [
 ("https://tools.pdf24.org/en/", "PDF24 Tools"),
 ("https://www.convertio.co/", "Convertio", "free-tier"),
 ("https://onlinetools.com/", "OnlineTools"),
 ("https://products.aspose.app/", "Aspose Apps", "free-tier"),
 ("https://tinywow.com/", "TinyWow"),
 ],
 "creator-tools": [
 ("https://www.capcut.com/", "CapCut", "free-tier"),
 ("https://invideo.io/", "InVideo", "free-tier"),
 ],
 "design": [("https://www.canva.com/", "Canva", "free-tier")],
 "generative-ai": [
 ("https://www.bing.com/images/create", "Bing Image Creator"),
 ("https://ideogram.ai/", "Ideogram", "free-tier"),
 ("https://playground.com/", "Playground AI", "free-tier"),
 ("https://leonardo.ai/", "Leonardo AI", "free-tier"),
 ],
 "study": [
 ("https://goblin.tools/", "Goblin Tools"),
 ("https://www.brainscape.com/", "Brainscape", "free-tier"),
 ("https://www.cram.com/", "Cram"),
 ("https://www.sophia.org/", "Sophia", "free-tier"),
 ],
 "programming": [
 ("https://replit.com/", "Replit", "free-tier"),
 ("https://leetcode.com/", "LeetCode", "free-tier"),
 ("https://exercism.org/", "Exercism"),
 ("https://www.codewars.com/", "Codewars"),
 ("https://scratch.mit.edu/", "Scratch"),
 ],
 "code-editors": [
 ("https://replit.com/", "Replit", "free-tier"),
 ("https://www.jdoodle.com/", "JDoodle"),
 ],
 "email": [
 ("https://mail.google.com/", "Gmail"),
 ("https://proton.me/mail", "Proton Mail", "free-tier"),
 ("https://web3forms.com/", "Web3Forms"),
 ("https://getform.io/", "Getform", "free-tier"),
 ("https://formspree.io/", "Formspree", "free-tier"),
 ],
 "free-stuff": [
 ("https://alternativeto.net/", "AlternativeTo"),
 ("https://www.producthunt.com/", "Product Hunt"),
 ("https://fmhy.net/internet-tools", "FMHY Internet"),
 ("https://fmhy.net/system-tools", "FMHY System"),
 ("https://fmhy.net/", "FMHY"),
 ],
 "music-podcasts": [
 ("https://open.spotify.com/", "Spotify", "free-tier"),
 ("https://music.youtube.com/", "YouTube Music", "free-tier"),
 ("https://soundcloud.com/", "SoundCloud", "free-tier"),
 ("https://bandcamp.com/", "Bandcamp"),
 ],
 "math-science": [
 ("https://www.desmos.com/", "Desmos"),
 ("https://www.geogebra.org/", "GeoGebra"),
 ("https://phet.colorado.edu/", "PhET Sims"),
 ("https://www.wolframalpha.com/", "Wolfram Alpha"),
 ],
 "website-builders": [
 ("https://pages.github.com/", "GitHub Pages"),
 ("https://vercel.com/", "Vercel", "free-tier"),
 ("https://www.netlify.com/", "Netlify", "free-tier"),
 ("https://carrd.co/", "Carrd", "free-tier"),
 ("https://wordpress.com/", "WordPress.com", "free-tier"),
 ],
 "databases": [
 ("https://supabase.com/", "Supabase", "free-tier"),
 ("https://neon.tech/", "Neon", "free-tier"),
 ("https://dbdiagram.io/", "dbdiagram.io", "free-tier"),
 ("https://sqliteonline.com/", "SQLite Online"),
 ("https://drawsql.app/", "DrawSQL", "free-tier"),
 ],
 "api-testing": [
 ("https://www.postman.com/", "Postman", "free-tier"),
 ("https://hoppscotch.io/", "Hoppscotch"),
 ("https://insomnia.rest/", "Insomnia", "free-tier"),
 ("https://reqbin.com/", "ReqBin"),
 ("https://editor.swagger.io/", "Swagger Editor"),
 ],
 "social-media": [
 ("https://buffer.com/", "Buffer", "free-tier"),
 ("https://linktr.ee/", "Linktree", "free-tier"),
 ("https://later.com/", "Later", "free-tier"),
 ("https://metricool.com/", "Metricool", "free-tier"),
 ],
 "finance-budgeting": [
 ("https://www.splitwise.com/", "Splitwise", "free-tier"),
 ("https://www.waveapps.com/", "Wave", "free-tier"),
 ("https://goodbudget.com/", "Goodbudget", "free-tier"),
 ("https://www.creditkarma.com/", "Credit Karma"),
 ],
 "health-wellness": [
 ("https://insighttimer.com/", "Insight Timer"),
 ("https://www.myfitnesspal.com/", "MyFitnessPal", "free-tier"),
 ("https://www.strava.com/", "Strava", "free-tier"),
 ],
 "collaboration": [
 ("https://slack.com/", "Slack", "free-tier"),
 ("https://discord.com/", "Discord"),
 ("https://zoom.us/", "Zoom", "free-tier"),
 ("https://teams.microsoft.com/", "Microsoft Teams", "free-tier"),
 ("https://meet.jit.si/", "Jitsi Meet"),
 ],
 "scheduling": [
 ("https://calendar.google.com/", "Google Calendar"),
 ("https://cal.com/", "Cal.com", "free-tier"),
 ("https://calendly.com/", "Calendly", "free-tier"),
 ("https://www.when2meet.com/", "When2meet"),
 ("https://doodle.com/", "Doodle", "free-tier"),
 ],
 "mind-mapping": [
 ("https://app.diagrams.net/", "draw.io"),
 ("https://coggle.it/", "Coggle", "free-tier"),
 ("https://whimsical.com/", "Whimsical", "free-tier"),
 ("https://www.mindmeister.com/", "MindMeister", "free-tier"),
 ],
 "file-sharing": [
 ("https://wetransfer.com/", "WeTransfer", "free-tier"),
 ("https://pixeldrain.com/", "Pixeldrain"),
 ("https://send.cm/", "Send.cm"),
 ],
 "fonts-typography": [
 ("https://fonts.google.com/", "Google Fonts"),
 ("https://www.dafont.com/", "DaFont"),
 ("https://www.fontsquirrel.com/", "Font Squirrel"),
 ("https://www.fontshare.com/", "Fontshare"),
 ],
 "color-tools": [
 ("https://coolors.co/", "Coolors"),
 ("https://colorhunt.co/", "Color Hunt"),
 ("https://paletton.com/", "Paletton"),
 ("https://color.adobe.com/", "Adobe Color"),
 ],
 "stock-media": [
 ("https://unsplash.com/", "Unsplash"),
 ("https://www.pexels.com/", "Pexels"),
 ("https://pixabay.com/", "Pixabay"),
 ("https://coverr.co/", "Coverr"),
 ("https://mixkit.co/", "Mixkit"),
 ],
 "browser-extensions": [
 ("https://github.com/gorhill/uBlock", "uBlock Origin", "free", "gorhill"),
 ("https://sponsor.ajay.app/", "SponsorBlock"),
 ("https://darkreader.org/", "Dark Reader"),
 ("https://www.toby.io/", "Toby", "free-tier"),
 ("https://www.onetab.com/", "OneTab"),
 ("https://www.greasemonkey.net/", "Greasemonkey"),
 ],
 "grammar-writing-ai": [
 ("https://www.deepl.com/write", "DeepL Write", "free-tier"),
 ],
 "exam-test-prep": [
 ("https://www.khanacademy.org/sat", "Khan SAT"),
 ],
 "must-try": [
 ("https://github.com/gorhill/uBlock", "uBlock Origin", "free", "gorhill"),
 ("https://fmhy.net/", "FMHY"),
 ],
 "pdf": [
 ("https://www.ilovepdf.com/", "iLovePDF", "free-tier"),
 ("https://smallpdf.com/", "Smallpdf", "free-tier"),
 ],
 "image": [
 ("https://www.remove.bg/", "Remove.bg", "free-tier"),
 ("https://tinypng.com/", "TinyPNG", "free-tier"),
 ("https://www.iloveimg.com/", "iLoveIMG", "free-tier"),
 ],
}

# Intentional cross-category listings: (url_fragment, [categories])
ALLOW_MULTI = {
 "claude.ai": ["research", "mathematics", "programming-ai", "analytical", "conversation", "ai", "english"],
 "chat.qwen.ai": ["research", "mathematics", "analytical", "conversation", "programming", "ai", "english"],
 "chat.deepseek.com": ["research", "mathematics", "programming-ai", "analytical", "ai"],
 "perplexity.ai": ["research", "analytical", "ai", "ai-study-tools"],
 "gemini.google.com": ["research", "analytical", "ai", "english"],
 "chat.openai.com": ["research", "mathematics", "conversation", "english"],
 "chatgpt.com": ["ai", "research", "conversation", "english"],
 "copilot.microsoft.com": ["research", "programming-ai", "ai"],
 "notion.so": ["ai-notetakers", "notepad", "productivity", "note-taking"],
 "standardnotes.com": ["ai-notetakers", "notepad", "note-taking"],
 "cloudconvert.com": ["converters", "image", "video", "audio"],
 "canva.com": ["design", "creator-tools", "presentation", "social-media"],
 "github.com/gorhill/ublock": ["must-try", "browser-extensions", "chrome-extension"],
 "khanacademy.org": ["courses", "study", "open-courseware", "math-science", "exam-test-prep"],
 "coursera.org": ["courses", "study", "open-courseware"],
 "wolframalpha.com": ["math-science", "mathematics", "spreadsheets"],
 "fmhy.net": ["must-try", "free-stuff"],
 "removepaywall.com": ["must-try", "secret"],
 "vocalremover.org": ["must-try", "audio"],
 "cluely.com": ["must-try", "study"],
 "freebuff.com": ["must-try", "programming-ai"],
 "app.emergent.sh": ["must-try", "website-builders"],
 "openstax.org": ["free-books", "ebooks-textbooks"],
 "replit.com": ["programming", "code-editors"],
 "w3schools.com": ["courses", "programming", "css-web-dev"],
 "developer.mozilla.org": ["courses", "programming", "css-web-dev"],
 "miro.com": ["mind-mapping", "collaboration", "online-whiteboard"],
 "app.diagrams.net": ["mind-mapping", "diagramming", "online-whiteboard"],
 "stirling-tools/stirling-pdf": ["github-powerhouses", "pdf"],
 "ollama.com": ["github-powerhouses", "local-ai"],
}


def should_remove(cat, url):
 for frag in REMOVE_FROM.get(cat, []):
 if frag in url.lower():
 return True
 return False


def parse_sections(html):
 sections = {}
 for m in SECTION_RE.finditer(html):
 cat = m.group(2)
 tools = []
 for lm in LINK_RE.finditer(m.group(3)):
 tools.append({
 "url": lm.group(1),
 "pricing": lm.group(2),
 "name": lm.group(3).strip(),
 "raw": lm.group(0),
 "norm": norm_url(lm.group(1)),
 })
 sections[cat] = tools
 return sections


def find_template(sections, url_frag):
 for tools in sections.values():
 for t in tools:
 if url_frag in t["url"].lower():
 return t
 return None


def main():
 html = HTML_PATH.read_text(encoding="utf-8")
 sections = parse_sections(html)
 removed = []
 added = []

 # Step 1: remove misplaced
 for cat, tools in sections.items():
 kept = []
 for t in tools:
 if should_remove(cat, t["url"]):
 removed.append((t["name"], cat))
 else:
 kept.append(t)
 sections[cat] = kept

 # Step 2: add missing from ADD dict
 for cat, entries in ADD.items():
 if cat not in sections:
 sections[cat] = []
 seen = {t["norm"] for t in sections[cat]}
 for entry in entries:
 url, name = entry[0], entry[1]
 pricing = entry[2] if len(entry) > 2 else "free"
 github = entry[3] if len(entry) > 3 else None
 key = norm_url(url)
 if key in seen:
 continue
 seen.add(key)
 sections[cat].append({
 "url": url, "name": name, "pricing": pricing,
 "raw": None, "norm": key, "github": github,
 })
 added.append((name, cat))

 # Step 3: restore intentional multi-category listings
 for url_frag, cats in ALLOW_MULTI.items():
 template = find_template(sections, url_frag)
 if not template:
 continue
 for cat in cats:
 if cat not in sections:
 sections[cat] = []
 seen = {t["norm"] for t in sections[cat]}
 if template["norm"] in seen:
 continue
 # only add if URL matches this fragment
 if url_frag not in template["url"].lower():
 continue
 sections[cat].append(dict(template))
 added.append((template["name"], cat))

 def build_inner(cat_tools):
 out = []
 seen = set()
 for t in cat_tools:
 if t["norm"] in seen:
 continue
 seen.add(t["norm"])
 if t.get("raw"):
 out.append(" " + t["raw"].strip() + "\n")
 else:
 out.append(link(t["url"], t["name"], t["pricing"], t.get("github")))
 return "".join(out)

 def replacer(m):
 cat = m.group(2)
 if cat not in sections:
 return m.group(0)
 return m.group(1) + "\n" + build_inner(sections[cat]) + " " + m.group(4)

 html = SECTION_RE.sub(replacer, html)
 HTML_PATH.write_text(html, encoding="utf-8")

 print(f"Removed {len(removed)} misplaced tools:")
 for name, cat in removed:
 print(f" - {name} from {cat}")
 print(f"\nAdded {len(added)} tools:")
 for name, cat in added:
 print(f" + {name} -> {cat}")


if __name__ == "__main__":
 main()
