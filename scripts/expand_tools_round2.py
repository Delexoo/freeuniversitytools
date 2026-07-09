"""Round 2: more free tools + new categories."""
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
HTML_PATH = ROOT / "student.html"

SECTION_RE = re.compile(
 r'(<section class="tool-category" data-category="([^"]+)">.*?<div class="category-tools">)(.*?)(</div>\s*</section>)',
 re.DOTALL,
)
HREF_RE = re.compile(r'href="([^"]+)"')


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


def section_block(cat_id, title, tools):
 lines = [
 f' <section class="tool-category" data-category="{cat_id}">',
 f' <h3 class="category-title">{title}</h3>',
 ' <div class="category-tools">',
 ]
 for t in tools:
 if len(t) == 2:
 lines.append(link(t[0], t[1]))
 elif len(t) == 3:
 lines.append(link(t[0], t[1], t[2]))
 elif len(t) == 4:
 lines.append(link(t[0], t[1], t[2], t[3]))
 lines += [" </div>", " </section>", ""]
 return "\n".join(lines)


NEW_CATEGORIES = {
 "exam-test-prep": (
 "Exam and Test Prep",
 [
 ("https://www.khanacademy.org/sat", "Khan SAT"),
 ("https://www.collegeboard.org/", "College Board"),
 ("https://www.magoosh.com/", "Magoosh", "free-tier"),
 ("https://www.240tutoring.com/", "240 Tutoring", "free-tier"),
 ("https://www.testprepreview.com/", "Test Prep Preview"),
 ],
 ),
 "student-discounts": (
 "Student Discounts",
 [
 ("https://www.myunidays.com/", "UNiDAYS"),
 ("https://www.studentbeans.com/", "Student Beans"),
 ("https://www.joinhoney.com/", "Honey"),
 ("https://www.groupon.com/", "Groupon"),
 ("https://www.retailmenot.com/", "RetailMeNot"),
 ],
 ),
 "logo-branding": (
 "Logo and Branding",
 [
 ("https://www.shopify.com/tools/logo-maker", "Hatchful"),
 ("https://logomakr.com/", "LogoMakr"),
 ("https://looka.com/", "Looka", "free-tier"),
 ("https://www.brandcrowd.com/", "BrandCrowd", "free-tier"),
 ("https://favicon.io/", "Favicon.io"),
 ],
 ),
 "css-web-dev": (
 "CSS and Web Dev",
 [
 ("https://cssgrid-generator.netlify.app/", "CSS Grid Generator"),
 ("https://flexbox.help/", "Flexbox Help"),
 ("https://caniuse.com/", "Can I Use"),
 ("https://www.w3schools.com/", "W3Schools"),
 ("https://developer.mozilla.org/", "MDN Web Docs"),
 ],
 ),
 "devops-containers": (
 "DevOps and Containers",
 [
 ("https://labs.play-with-docker.com/", "Play with Docker"),
 ("https://www.docker.com/play-with-docker/", "Docker Playground"),
 ("https://kodekloud.com/free-labs/", "KodeKloud Labs", "free-tier"),
 ("https://www.portainer.io/", "Portainer", "free-tier"),
 ("https://github.com/coollabsio/coolify", "Coolify", "free", "coollabsio"),
 ],
 ),
 "api-mocking": (
 "API Mocking",
 [
 ("https://mockoon.com/", "Mockoon"),
 ("https://beeceptor.com/", "Beeceptor", "free-tier"),
 ("https://webhook.site/", "Webhook.site"),
 ("https://httpbin.org/", "HTTPBin"),
 ("https://jsonplaceholder.typicode.com/", "JSONPlaceholder"),
 ],
 ),
 "encode-hash-tools": (
 "Encode and Hash Tools",
 [
 ("https://jwt.io/", "JWT.io"),
 ("https://www.base64encode.org/", "Base64 Encode"),
 ("https://www.md5hashgenerator.com/", "MD5 Generator"),
 ("https://www.uuidgenerator.net/", "UUID Generator"),
 ("https://www.urlencoder.org/", "URL Encoder"),
 ],
 ),
 "placeholder-design": (
 "Placeholders and Lorem",
 [
 ("https://www.lipsum.com/", "Lorem Ipsum"),
 ("https://placeholder.com/", "Placeholder.com"),
 ("https://picsum.photos/", "Lorem Picsum"),
 ("https://placehold.co/", "Placehold.co"),
 ("https://dummyimage.com/", "DummyImage"),
 ],
 ),
 "tech-communities": (
 "Tech Communities",
 [
 ("https://dev.to/", "DEV Community"),
 ("https://news.ycombinator.com/", "Hacker News"),
 ("https://stackoverflow.com/", "Stack Overflow"),
 ("https://www.reddit.com/r/learnprogramming/", "r/learnprogramming"),
 ("https://hashnode.com/", "Hashnode"),
 ],
 ),
 "hackathons-events": (
 "Hackathons and Events",
 [
 ("https://devpost.com/", "Devpost"),
 ("https://mlh.io/", "MLH"),
 ("https://www.eventbrite.com/", "Eventbrite"),
 ("https://www.meetup.com/", "Meetup"),
 ("https://lu.ma/", "Luma"),
 ],
 ),
 "internships": (
 "Internships",
 [
 ("https://www.joinhandshake.com/", "Handshake"),
 ("https://www.wayup.com/", "WayUp"),
 ("https://www.internships.com/", "Internships.com"),
 ("https://www.chegg.com/internships", "Chegg Internships"),
 ("https://www.linkedin.com/jobs/", "LinkedIn Jobs"),
 ],
 ),
 "journaling": (
 "Journaling",
 [
 ("https://journey.cloud/", "Journey", "free-tier"),
 ("https://penzu.com/", "Penzu", "free-tier"),
 ("https://dayoneapp.com/", "Day One", "free-tier"),
 ("https://www.diariumapp.com/", "Diarium", "free-tier"),
 ("https://reflect.app/", "Reflect", "free-tier"),
 ],
 ),
 "maps-gis": (
 "Maps and GIS",
 [
 ("https://www.openstreetmap.org/", "OpenStreetMap"),
 ("https://www.google.com/earth/", "Google Earth"),
 ("https://www.qgis.org/", "QGIS"),
 ("https://www.openrailwaymap.org/", "OpenRailwayMap"),
 ("https://www.openaerialmap.org/", "OpenAerialMap"),
 ],
 ),
 "speed-network": (
 "Speed and Network Tools",
 [
 ("https://fast.com/", "Fast.com"),
 ("https://www.speedtest.net/", "Speedtest"),
 ("https://speed.cloudflare.com/", "Cloudflare Speed"),
 ("https://www.whatsmydns.net/", "WhatsMyDNS"),
 ("https://dnschecker.org/", "DNS Checker"),
 ],
 ),
 "email-marketing": (
 "Email Marketing",
 [
 ("https://mailchimp.com/", "Mailchimp", "free-tier"),
 ("https://www.mailerlite.com/", "MailerLite", "free-tier"),
 ("https://www.brevo.com/", "Brevo", "free-tier"),
 ("https://sendpulse.com/", "SendPulse", "free-tier"),
 ("https://www.mailjet.com/", "Mailjet", "free-tier"),
 ],
 ),
 "cms-blogging": (
 "CMS and Blogging",
 [
 ("https://ghost.org/", "Ghost", "free-tier"),
 ("https://gohugo.io/", "Hugo"),
 ("https://jekyllrb.com/", "Jekyll"),
 ("https://medium.com/", "Medium"),
 ("https://substack.com/", "Substack", "free-tier"),
 ],
 ),
 "ai-agents": (
 "AI Agents and Flows",
 [
 ("https://github.com/crewAIInc/crewAI", "CrewAI", "free", "crewAIInc"),
 ("https://www.langflow.org/", "Langflow"),
 ("https://flowiseai.com/", "Flowise"),
 ("https://github.com/FlowiseAI/Flowise", "Flowise GitHub", "free", "FlowiseAI"),
 ("https://dify.ai/", "Dify", "free-tier"),
 ],
 ),
 "local-ai": (
 "Local AI Models",
 [
 ("https://lmstudio.ai/", "LM Studio"),
 ("https://gpt4all.io/", "GPT4All"),
 ("https://ollama.com/", "Ollama"),
 ("https://github.com/jmorganca/ollama", "Ollama GitHub", "free", "ollama"),
 ("https://localai.io/", "LocalAI"),
 ],
 ),
 "gradient-css": (
 "Gradients and CSS Gen",
 [
 ("https://cssgradient.io/", "CSS Gradient"),
 ("https://uigradients.com/", "UI Gradients"),
 ("https://webgradients.com/", "WebGradients"),
 ("https://neumorphism.io/", "Neumorphism"),
 ("https://glassmorphism.com/", "Glassmorphism"),
 ],
 ),
 "diff-format-tools": (
 "Diff and Format Tools",
 [
 ("https://www.diffchecker.com/", "Diffchecker"),
 ("https://codebeautify.org/", "CodeBeautify"),
 ("https://prettier.io/playground/", "Prettier Playground"),
 ("https://jsonlint.com/", "JSONLint"),
 ("https://jsonformatter.curiousconcept.com/", "JSON Formatter"),
 ],
 ),
}

EXPAND = {
 "must-try": [("https://fmhy.net/", "FMHY")],
 "free-books": [("https://standardebooks.org/", "Standard Ebooks"), ("https://www.feedbooks.com/", "Feedbooks", "free-tier")],
 "immersive-reader": [("https://www.naturalreaders.com/", "NaturalReaders", "free-tier")],
 "courses": [("https://www.open.edu/", "Open University", "free-tier"), ("https://alison.com/", "Alison")],
 "essay-tools": [("https://www.grammarly.com/plagiarism-checker", "Grammarly Check", "limited")],
 "research": [("https://www.connectedpapers.com/", "Connected Papers"), ("https://www.litmaps.com/", "Litmaps", "free-tier")],
 "mathematics": [("https://www.cymath.com/", "Cymath", "free-tier"), ("https://www.photomath.com/", "Photomath", "free-tier")],
 "programming-ai": [("https://codeium.com/", "Codeium"), ("https://www.tabnine.com/", "Tabnine", "free-tier")],
 "analytical": [("https://www.tableau.com/public", "Tableau Public")],
 "conversation": [("https://www.replika.com/", "Replika", "free-tier")],
 "ai-notetakers": [("https://www.capacities.io/", "Capacities", "free-tier")],
 "study": [("https://www.memrise.com/", "Memrise"), ("https://www.supermemo.com/", "SuperMemo", "free-tier")],
 "cloud": [("https://www.icedrive.net/", "IceDrive", "free-tier")],
 "online-poll": [("https://www.poll-maker.com/", "Poll Maker")],
 "pdf": [("https://www.pdf2go.com/", "PDF2Go", "free-tier")],
 "image": [("https://www.befunky.com/", "BeFunky", "free-tier"), ("https://www.fotor.com/", "Fotor", "free-tier")],
 "video": [("https://www.clipchamp.com/", "Clipchamp")],
 "audio": [("https://www.bandlab.com/", "BandLab")],
 "gif-converters": [("https://convertio.co/gif-converter/", "Convertio GIF", "free-tier")],
 "online-whiteboard": [("https://tldraw.com/", "tldraw")],
 "programming": [("https://www.w3schools.com/", "W3Schools"), ("https://developer.mozilla.org/", "MDN")],
 "design": [("https://www.sketch.com/", "Sketch", "free-tier")],
 "language-learning": [("https://www.lingodeer.com/", "LingoDeer", "free-tier")],
 "todo-list": [("https://www.microsoft.com/microsoft-365/microsoft-to-do", "Microsoft To Do", "free-tier")],
 "utilities": [("https://www.calculator.net/", "Calculator.net"), ("https://www.convertunits.com/", "ConvertUnits")],
 "secret": [("https://archive.is/", "Archive.is")],
 "ai": [("https://you.com/", "You.com", "free-tier"), ("https://pi.ai/", "Pi", "free-tier")],
 "creator-tools": [("https://www.subscribr.ai/", "Subscribr", "free-tier")],
 "browser-games": [("https://www.newgrounds.com/", "Newgrounds")],
 "remote-jobs": [("https://www.glassdoor.com/", "Glassdoor")],
 "generative-ai": [("https://www.midjourney.com/", "Midjourney", "free-tier"), ("https://www.dreamstudio.ai/", "DreamStudio", "free-tier")],
 "all-in-one-tools": [("https://www.123apps.com/", "123Apps")],
 "security": [("https://www.avast.com/free-antivirus", "Avast Free")],
 "science": [("https://www.britannica.com/science", "Britannica Science", "free-tier")],
 "writing": [("https://www.writersdigest.com/", "Writers Digest", "free-tier")],
 "converters": [("https://www.onlineconverter.com/", "OnlineConverter")],
 "email": [("https://www.zoho.com/mail/", "Zoho Mail", "free-tier")],
 "vpn-security": [("https://www.torproject.org/", "Tor Browser")],
 "resume-career": [("https://www.monster.com/", "Monster")],
 "presentation": [("https://www.microsoft.com/microsoft-365/powerpoint", "PowerPoint Web", "free-tier")],
 "spreadsheets": [("https://www.microsoft.com/microsoft-365/excel", "Excel Web", "free-tier")],
 "note-taking": [("https://www.craft.do/", "Craft", "free-tier")],
 "math-science": [("https://www.khanacademy.org/math", "Khan Math")],
 "ebooks-textbooks": [("https://bookboon.com/", "Bookboon", "free-tier")],
 "screen-recording": [("https://www.apowersoft.com/free-online-screen-recorder", "Apowersoft Rec")],
 "website-builders": [("https://www.wix.com/", "Wix", "free-tier")],
 "3d-animation": [("https://www.animaker.com/", "Animaker", "free-tier")],
 "databases": [("https://www.mongodb.com/atlas", "MongoDB Atlas", "free-tier")],
 "api-testing": [("https://www.postman.com/", "Postman", "free-tier")],
 "social-media": [("https://www.tiktok.com/", "TikTok")],
 "finance-budgeting": [("https://www.mint.com/", "Mint")],
 "health-wellness": [("https://www.nike.com/ntc-app", "Nike Training", "free-tier")],
 "collaboration": [("https://www.miro.com/", "Miro", "free-tier")],
 "scheduling": [("https://calendar.google.com/", "Google Calendar")],
 "mind-mapping": [("https://www.mindomo.com/", "Mindomo", "free-tier")],
 "file-sharing": [("https://www.4shared.com/", "4shared", "free-tier")],
 "fonts-typography": [("https://www.fontspace.com/", "FontSpace")],
 "color-tools": [("https://colormind.io/", "Colormind")],
 "stock-media": [("https://www.storyblocks.com/", "Storyblocks", "free-tier")],
 "browser-extensions": [("https://www.greasemonkey.net/", "Greasemonkey")],
 "grammar-writing-ai": [("https://www.grammarcheck.net/", "GrammarCheck")],
 "translation": [("https://www.mymemory.translated.net/", "MyMemory")],
 "ai-video": [("https://www.descript.com/", "Descript", "free-tier")],
 "ai-voice": [("https://lovo.ai/", "LOVO", "free-tier")],
 "cybersecurity": [("https://www.sans.org/cyberaces/", "SANS Cyber Aces")],
 "data-science": [("https://www.kaggle.com/learn", "Kaggle Learn")],
 "diagramming": [("https://www.smartdraw.com/", "SmartDraw", "free-tier")],
 "focus-productivity": [("https://www.marinaratimer.com/", "Marinara Timer")],
 "ai-study-tools": [("https://www.gradescope.com/", "Gradescope", "free-tier")],
 "code-editors": [("https://replit.com/", "Replit", "free-tier")],
 "ai-image-editing": [("https://www.stylar.ai/", "Stylar", "free-tier")],
 "open-courseware": [("https://www.saylor.org/", "Saylor Academy")],
 "privacy-tools": [("https://www.startpage.com/", "Startpage")],
 "cheat-sheets": [("https://devhints.io/", "DevHints")],
 "markdown-tools": [("https://www.markdowntopdf.com/", "MD to PDF")],
 "regex-devtools": [("https://extendsclass.com/regex-tester.html", "Regex Tester")],
 "accessibility": [("https://tota11y.org/", "tota11y")],
 "typing-practice": [("https://www.typing.com/", "Typing.com")],
 "latex-docs": [("https://www.latex-tutorial.com/", "LaTeX Tutorial")],
 "ai-pdf-chat": [("https://www.humata.ai/", "Humata", "free-tier")],
 "bookmarks-rss": [("https://www.theoldreader.com/", "The Old Reader", "free-tier")],
 "art-drawing": [("https://www.sumopaint.com/", "Sumo Paint", "free-tier")],
 "music-production": [("https://www.soundtrap.com/", "Soundtrap", "free-tier")],
 "scholarships": [("https://www.scholarshipowl.com/", "ScholarshipOwl", "free-tier")],
 "open-source": [("https://www.gnu.org/", "GNU")],
 "automation": [("https://pipedream.com/", "Pipedream", "free-tier")],
 "geography-history": [("https://www.ducksters.com/", "Ducksters")],
 "icons-illustrations": [("https://www.svgrepo.com/", "SVG Repo")],
 "mockups-templates": [("https://www.pixeden.com/", "Pixeden", "free-tier")],
 "git-version-control": [("https://github.com/", "GitHub")],
 "cloud-storage-sync": [("https://www.backblaze.com/", "Backblaze", "free-tier")],
 "github-powerhouses": [("https://github.com/open-webui/open-webui", "Open WebUI", "free", "open-webui")],
 "productivity": [("https://www.notion.so/", "Notion", "free-tier")],
 "english": [("https://www.englishclub.com/", "English Club")],
 "chrome-extension": [("https://www.greasemonkey.net/", "Greasemonkey")],
 "notepad": [("https://dillinger.io/", "Dillinger")],
 "live-streaming": [("https://www.youtube.com/live", "YouTube Live")],
 "music-podcasts": [("https://podcasts.google.com/", "Google Podcasts")],
 "free-stuff": [("https://www.reddit.com/r/FreeEBOOKS/", "r/FreeEBOOKS")],
 "free-movies": [("https://www.crackle.com/", "Crackle")],
}


def build_link(t):
 return link(t[0], t[1], t[2] if len(t) > 2 else "free", t[3] if len(t) > 3 else None)


html = HTML_PATH.read_text(encoding="utf-8")
sections = {}
for m in SECTION_RE.finditer(html):
 cat = m.group(2)
 inner = m.group(3)
 urls = {norm_url(u) for u in HREF_RE.findall(inner)}
 sections[cat] = {"prefix": m.group(1), "inner": inner, "suffix": m.group(4), "urls": urls}

added_expand = 0
for cat, tools in EXPAND.items():
 if cat not in sections:
 continue
 for t in tools:
 key = norm_url(t[0])
 if key in sections[cat]["urls"]:
 continue
 sections[cat]["urls"].add(key)
 sections[cat]["inner"] += build_link(t)
 added_expand += 1


def replacer(m):
 cat = m.group(2)
 if cat not in sections:
 return m.group(0)
 s = sections[cat]
 return s["prefix"] + s["inner"] + s["suffix"]


html = SECTION_RE.sub(replacer, html)

new_blocks = []
for cat_id, (title, tools) in NEW_CATEGORIES.items():
 if f'data-category="{cat_id}"' in html:
 continue
 new_blocks.append(section_block(cat_id, title, tools))

if new_blocks:
 marker = "\n </div>\n </main>"
 html = html.replace(marker, "\n" + "\n".join(new_blocks) + marker, 1)

HTML_PATH.write_text(html, encoding="utf-8")
print(f"Updated {HTML_PATH}")
print(f"New categories: {len(new_blocks)}")
print(f"Tools added to existing: {added_expand}")
