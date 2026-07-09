"""Repair misplaced category tools and add missing free apps."""
import re
from pathlib import Path
from urllib.parse import urlparse

path = Path(__file__).resolve().parent.parent / "student.html"
html = path.read_text(encoding="utf-8")

SECTION_RE = re.compile(
 r'(<section class="tool-category" data-category="([^"]+)">.*?<div class="category-tools">)(.*?)(</div>\s*</section>)',
 re.DOTALL,
)
LINK_RE = re.compile(
 r'<a\s+href="([^"]+)"[^>]*data-pricing="([^"]+)"[^>]*>.*?<span class="tool-link-name">([^<]+)</span></a>',
 re.DOTALL,
)


def norm_url(url):
 p = urlparse(url.strip().rstrip("/"))
 host = (p.netloc or "").lower().replace("www.", "")
 path_part = p.path.rstrip("/")
 return f"{host}{path_part}".lower()


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


REMOVE_FROM = {
 "databases": ["keepassxc.org", "keepass.info", "passwords.google.com"],
 "api-testing": ["tools.pdf24.org", "convertio.co", "onlinetools.com", "products.aspose.app"],
 "social-media": ["canva.com", "capcut.com", "invideo.io"],
 "finance-budgeting": ["bing.com/images/create", "ideogram.ai", "playground.com", "huggingface.co", "leonardo.ai"],
 "health-wellness": ["goblin.tools", "brainscape.com", "cram.com", "sophia.org"],
 "collaboration": ["replit.com", "leetcode.com", "exercism.org", "codewars.com", "scratch.mit.edu"],
 "scheduling": ["mail.google.com", "proton.me/mail", "web3forms.com", "getform.io"],
 "mind-mapping": ["alternativeto.net", "producthunt.com", "fmhy.net/internet-tools", "fmhy.net/system-tools"],
 "file-sharing": ["open.spotify.com", "music.youtube.com", "soundcloud.com", "bandcamp.com"],
 "fonts-typography": ["desmos.com", "geogebra.org", "phet.colorado.edu", "wolframalpha.com"],
 "color-tools": ["pages.github.com", "vercel.com", "netlify.com", "carrd.co", "wordpress.com"],
 "stock-media": ["supabase.com", "neon.tech", "dbdiagram.io", "sqliteonline.com", "drawsql.app"],
 "browser-extensions": ["postman.com", "hoppscotch.io", "insomnia.rest", "reqbin.com", "editor.swagger.io"],
 "writing": ["chat.qwen.ai"],
 "notepad": [], # handle dup below
 "gif-converters": ["ezgif.com/"],
}

ADD = {
 "security": [
 ("https://keepassxc.org/", "KeePassXC"),
 ("https://keepass.info/", "KeePass"),
 ("https://passwords.google.com/", "Google Passwords", "free-tier"),
 ],
 "all-in-one-tools": [
 ("https://tools.pdf24.org/en/", "PDF24 Tools"),
 ("https://www.convertio.co/", "Convertio", "free-tier"),
 ("https://onlinetools.com/", "OnlineTools"),
 ("https://products.aspose.app/", "Aspose Apps", "free-tier"),
 ],
 "creator-tools": [
 ("https://www.canva.com/", "Canva", "free-tier"),
 ("https://www.capcut.com/", "CapCut", "free-tier"),
 ("https://invideo.io/", "InVideo", "free-tier"),
 ],
 "generative-ai": [
 ("https://www.bing.com/images/create", "Bing Image Creator"),
 ("https://ideogram.ai/", "Ideogram", "free-tier"),
 ("https://playground.com/", "Playground AI", "free-tier"),
 ("https://huggingface.co/", "Hugging Face"),
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
 "email": [
 ("https://mail.google.com/", "Gmail"),
 ("https://proton.me/mail", "Proton Mail", "free-tier"),
 ("https://web3forms.com/", "Web3Forms"),
 ("https://getform.io/", "Getform", "free-tier"),
 ],
 "free-stuff": [
 ("https://alternativeto.net/", "AlternativeTo"),
 ("https://www.producthunt.com/", "Product Hunt"),
 ("https://fmhy.net/internet-tools", "FMHY Internet"),
 ("https://fmhy.net/system-tools", "FMHY System"),
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
 ("https://namechk.com/", "Namechk"),
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
 ("https://miro.com/", "Miro", "free-tier"),
 ],
 "file-sharing": [
 ("https://send.cm/", "Send.cm"),
 ("https://pixeldrain.com/", "Pixeldrain"),
 ("https://file.io/", "file.io"),
 ("https://transfer.sh/", "transfer.sh"),
 ("https://tmpfiles.org/", "TmpFiles"),
 ],
 "fonts-typography": [
 ("https://fonts.google.com/", "Google Fonts"),
 ("https://www.dafont.com/", "DaFont"),
 ("https://www.fontsquirrel.com/", "Font Squirrel"),
 ("https://www.fontshare.com/", "Fontshare"),
 ("https://fontesk.com/", "Fontesk"),
 ],
 "color-tools": [
 ("https://coolors.co/", "Coolors"),
 ("https://colorhunt.co/", "Color Hunt"),
 ("https://paletton.com/", "Paletton"),
 ("https://color.adobe.com/", "Adobe Color"),
 ("https://webaim.org/resources/contrastchecker/", "Contrast Checker"),
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
 ],
}


def should_remove(cat, url):
 for frag in REMOVE_FROM.get(cat, []):
 if frag in url.lower():
 return True
 return False


sections = {}
for m in SECTION_RE.finditer(html):
 cat = m.group(2)
 inner = m.group(3)
 kept = []
 seen = set()
 for lm in LINK_RE.finditer(inner):
 url, pricing, name = lm.group(1), lm.group(2), lm.group(3).strip()
 if should_remove(cat, url):
 continue
 key = norm_url(url)
 if key in seen:
 continue
 seen.add(key)
 kept.append({"url": url, "name": name, "pricing": pricing, "raw": lm.group(0)})
 sections[cat] = kept

for cat, tools in ADD.items():
 if cat not in sections:
 sections[cat] = []
 seen = {norm_url(x["url"]) for x in sections[cat]}
 for t in tools:
 url, name = t[0], t[1]
 pricing = t[2] if len(t) > 2 else "free"
 github = t[3] if len(t) > 3 else None
 key = norm_url(url)
 if key in seen:
 continue
 seen.add(key)
 sections[cat].append({"url": url, "name": name, "pricing": pricing, "raw": None, "github": github})


def build_inner(links):
 out = []
 for item in links:
 if item.get("raw"):
 out.append(" " + item["raw"].strip() + "\n")
 else:
 out.append(link(item["url"], item["name"], item["pricing"], github=item.get("github")))
 return "".join(out)


def replacer(m):
 cat = m.group(2)
 if cat not in sections:
 return m.group(0)
 return m.group(1) + "\n" + build_inner(sections[cat]) + " " + m.group(4)


html = SECTION_RE.sub(replacer, html)
path.write_text(html, encoding="utf-8")
print("Fixed", path)
