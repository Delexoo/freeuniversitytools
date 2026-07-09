"""Add new categories and expand existing ones with free tools."""
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
HTML_PATH = ROOT / "student.html"


def norm_url(url):
 p = urlparse(url.strip().rstrip("/"))
 host = (p.netloc or "").lower().replace("www.", "")
 path = p.path.rstrip("/")
 return f"{host}{path}".lower()


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
 lines = [f' <section class="tool-category" data-category="{cat_id}">']
 lines.append(f' <h3 class="category-title">{title}</h3>')
 lines.append(' <div class="category-tools">')
 for t in tools:
 if len(t) == 2:
 lines.append(link(t[0], t[1]))
 elif len(t) == 3:
 lines.append(link(t[0], t[1], t[2]))
 elif len(t) == 4:
 lines.append(link(t[0], t[1], t[2], t[3]))
 lines.append(" </div>")
 lines.append(" </section>")
 lines.append("")
 return "\n".join(lines)


SECTION_RE = re.compile(
 r'(<section class="tool-category" data-category="([^"]+)">.*?<div class="category-tools">)(.*?)(</div>\s*</section>)',
 re.DOTALL,
)
HREF_RE = re.compile(r'href="([^"]+)"')


NEW_CATEGORIES = {
 "cheat-sheets": (
 "Cheat Sheets and Docs",
 [
 ("https://devdocs.io/", "DevDocs"),
 ("https://quickref.me/", "QuickRef"),
 ("https://overapi.com/", "OverAPI"),
 ("https://cheatography.com/", "Cheatography"),
 ("https://www.cheat-sheets.org/", "Cheat-Sheets.org"),
 ],
 ),
 "markdown-tools": (
 "Markdown Editors",
 [
 ("https://hackmd.io/", "HackMD", "free-tier"),
 ("https://dillinger.io/", "Dillinger"),
 ("https://stackedit.io/", "StackEdit"),
 ("https://markdownlivepreview.com/", "MD Live Preview"),
 ("https://www.markdowntopdf.com/", "MD to PDF"),
 ],
 ),
 "regex-devtools": (
 "Regex and Dev Tools",
 [
 ("https://regex101.com/", "Regex101"),
 ("https://regexr.com/", "RegExr"),
 ("https://www.debuggex.com/", "Debuggex", "free-tier"),
 ("https://crontab.guru/", "Crontab Guru"),
 ("https://www.jsonformatter.org/", "JSON Formatter"),
 ],
 ),
 "accessibility": (
 "Accessibility Tools",
 [
 ("https://wave.webaim.org/", "WAVE"),
 ("https://webaim.org/resources/contrastchecker/", "Contrast Checker"),
 ("https://www.accessibilitychecker.org/", "A11y Checker", "free-tier"),
 ("https://colororacle.org/", "Color Oracle"),
 ("https://www.deque.com/axe/devtools/", "axe DevTools", "free-tier"),
 ],
 ),
 "typing-practice": (
 "Typing Practice",
 [
 ("https://monkeytype.com/", "Monkeytype"),
 ("https://www.keybr.com/", "Keybr"),
 ("https://www.typingclub.com/", "TypingClub"),
 ("https://play.typeracer.com/", "TypeRacer"),
 ("https://10fastfingers.com/", "10FastFingers"),
 ],
 ),
 "latex-docs": (
 "LaTeX and Math Docs",
 [
 ("https://www.overleaf.com/", "Overleaf", "free-tier"),
 ("https://papeeria.com/", "Papeeria", "free-tier"),
 ("https://latexbase.com/", "LaTeX Base"),
 ("https://www.latex-project.org/", "LaTeX Project"),
 ("https://www.tablesgenerator.com/", "Tables Generator"),
 ],
 ),
 "ai-pdf-chat": (
 "AI PDF Chat",
 [
 ("https://www.chatpdf.com/", "ChatPDF", "free-tier"),
 ("https://www.humata.ai/", "Humata", "free-tier"),
 ("https://pdf.ai/", "PDF.ai", "free-tier"),
 ("https://www.lightpdf.com/chatdoc", "LightPDF Chat", "free-tier"),
 ("https://www.notion.so/product/ai", "Notion AI", "free-tier"),
 ],
 ),
 "bookmarks-rss": (
 "Bookmarks and RSS",
 [
 ("https://getpocket.com/", "Pocket", "free-tier"),
 ("https://raindrop.io/", "Raindrop", "free-tier"),
 ("https://feedly.com/", "Feedly", "free-tier"),
 ("https://www.inoreader.com/", "Inoreader", "free-tier"),
 ("https://www.instapaper.com/", "Instapaper", "free-tier"),
 ],
 ),
 "art-drawing": (
 "Art and Drawing",
 [
 ("https://aggie.io/", "Aggie.io"),
 ("https://kleki.com/", "Kleki"),
 ("https://sketch.io/sketchpad/", "Sketchpad"),
 ("https://www.pixilart.com/", "Pixilart"),
 ("https://www.autodraw.com/", "AutoDraw"),
 ],
 ),
 "music-production": (
 "Music Production",
 [
 ("https://www.bandlab.com/", "BandLab"),
 ("https://www.lmms.io/", "LMMS"),
 ("https://www.audiotool.com/", "Audiotool"),
 ("https://soundation.com/", "Soundation", "free-tier"),
 ("https://www.musehub.com/", "MuseHub"),
 ],
 ),
 "scholarships": (
 "Scholarships and Aid",
 [
 ("https://www.fastweb.com/", "Fastweb"),
 ("https://www.scholarships.com/", "Scholarships.com"),
 ("https://bigfuture.collegeboard.org/", "BigFuture"),
 ("https://www.cappex.com/", "Cappex", "free-tier"),
 ("https://www.unigo.com/", "Unigo", "free-tier"),
 ],
 ),
 "open-source": (
 "Open Source Discovery",
 [
 ("https://f-droid.org/", "F-Droid"),
 ("https://github.com/trending", "GitHub Trending"),
 ("https://github.com/sindresorhus/awesome", "Awesome Lists"),
 ("https://opensource.org/", "Open Source Initiative"),
 ("https://alternativeto.net/", "AlternativeTo"),
 ],
 ),
 "automation": (
 "Automation Tools",
 [
 ("https://ifttt.com/", "IFTTT", "free-tier"),
 ("https://zapier.com/", "Zapier", "free-tier"),
 ("https://n8n.io/", "n8n", "free-tier"),
 ("https://make.com/", "Make", "free-tier"),
 ("https://www.activepieces.com/", "Activepieces", "free-tier"),
 ],
 ),
 "geography-history": (
 "Geography and History",
 [
 ("https://online.seterra.com/", "Seterra"),
 ("https://www.geoguessr.com/", "GeoGuessr", "free-tier"),
 ("https://ourworldindata.org/", "Our World in Data"),
 ("https://www.loc.gov/", "Library of Congress"),
 ("https://www.britannica.com/", "Britannica", "free-tier"),
 ],
 ),
 "icons-illustrations": (
 "Icons and Illustrations",
 [
 ("https://icons8.com/", "Icons8", "free-tier"),
 ("https://www.flaticon.com/", "Flaticon", "free-tier"),
 ("https://iconscout.com/", "IconScout", "free-tier"),
 ("https://undraw.co/", "unDraw"),
 ("https://www.humaaans.com/", "Humaaans"),
 ],
 ),
 "mockups-templates": (
 "Mockups and Templates",
 [
 ("https://mockupworld.co/", "Mockup World"),
 ("https://www.freepik.com/", "Freepik", "free-tier"),
 ("https://www.mockuphone.com/", "MockUPhone"),
 ("https://smartmockups.com/", "Smartmockups", "free-tier"),
 ("https://placeit.net/", "Placeit", "free-tier"),
 ],
 ),
 "git-version-control": (
 "Git and Version Control",
 [
 ("https://gitlab.com/", "GitLab", "free-tier"),
 ("https://gitea.io/", "Gitea"),
 ("https://www.gitkraken.com/", "GitKraken", "free-tier"),
 ("https://www.sourcetreeapp.com/", "Sourcetree"),
 ("https://ohshitgit.com/", "Oh Shit Git"),
 ],
 ),
 "cloud-storage-sync": (
 "Cloud Sync and Backup",
 [
 ("https://www.box.com/", "Box", "free-tier"),
 ("https://www.mediafire.com/", "MediaFire", "free-tier"),
 ("https://www.4shared.com/", "4shared", "free-tier"),
 ("https://www.idrive.com/", "IDrive", "free-tier"),
 ("https://duplicati.com/", "Duplicati"),
 ],
 ),
}

# category -> list of (url, name, pricing?)
EXPAND = {
 "must-try": [
 ("https://fmhy.net/beginners-guide", "FMHY Guide"),
 ("https://www.removepaywall.com/", "Remove Paywall"),
 ],
 "github-powerhouses": [
 ("https://github.com/ollama/ollama", "Ollama", "free", "ollama"),
 ("https://github.com/langchain-ai/langchain", "LangChain", "free", "langchain-ai"),
 ("https://github.com/Stirling-Tools/Stirling-PDF", "Stirling PDF", "free", "Stirling-Tools"),
 ],
 "immersive-reader": [
 ("https://ttsreader.com/", "TTSReader"),
 ("https://www.naturalreaders.com/online/", "NaturalReader", "free-tier"),
 ("https://readaloud.app/", "Read Aloud"),
 ],
 "mathematics": [
 ("https://www.symbolab.com/", "Symbolab", "free-tier"),
 ("https://www.mathway.com/", "Mathway", "free-tier"),
 ("https://www.wolframalpha.com/", "Wolfram Alpha"),
 ],
 "programming-ai": [
 ("https://aistudio.google.com/", "Google AI Studio"),
 ("https://github.com/features/copilot", "GitHub Copilot", "free-tier"),
 ("https://www.phind.com/", "Phind", "free-tier"),
 ],
 "analytical": [
 ("https://julius.ai/", "Julius AI", "free-tier"),
 ("https://www.chatcsv.com/", "ChatCSV", "free-tier"),
 ],
 "conversation": [
 ("https://www.character.ai/", "Character.ai", "free-tier"),
 ("https://poe.com/", "Poe", "free-tier"),
 ],
 "ai-notetakers": [
 ("https://reflect.app/", "Reflect", "free-tier"),
 ("https://www.remnote.com/", "RemNote", "free-tier"),
 ],
 "ebooks-textbooks": [
 ("https://openstax.org/", "OpenStax"),
 ("https://www.gutenberg.org/", "Project Gutenberg"),
 ("https://openlibrary.org/", "Open Library"),
 ("https://www.oercommons.org/", "OER Commons"),
 ],
 "health-wellness": [
 ("https://www.headspace.com/", "Headspace", "free-tier"),
 ("https://www.calm.com/", "Calm", "free-tier"),
 ("https://www.noom.com/", "Noom", "free-tier"),
 ],
 "finance-budgeting": [
 ("https://mint.intuit.com/", "Mint", "free"),
 ("https://www.personalcapital.com/", "Empower", "free"),
 ("https://www.ynab.com/", "YNAB", "free-tier"),
 ],
 "3d-animation": [
 ("https://www.mixamo.com/", "Mixamo"),
 ("https://www.opentoonz.org/", "OpenToonz"),
 ("https://www.kdenlive.org/", "Kdenlive"),
 ],
 "language-learning": [
 ("https://www.lingq.com/", "LingQ", "free-tier"),
 ("https://www.clozemaster.com/", "Clozemaster", "free-tier"),
 ("https://www.italki.com/", "italki", "free-tier"),
 ],
 "browser-games": [
 ("https://www.miniclip.com/", "Miniclip"),
 ("https://www.addictinggames.com/", "Addicting Games"),
 ("https://www.kongregate.com/", "Kongregate"),
 ],
 "creator-tools": [
 ("https://www.remove.bg/", "Remove.bg", "free-tier"),
 ("https://www.thumbnail.ai/", "Thumbnail AI", "free-tier"),
 ],
 "generative-ai": [
 ("https://www.craiyon.com/", "Craiyon"),
 ("https://stability.ai/", "Stability AI", "free-tier"),
 ("https://tensor.art/", "Tensor.art", "free-tier"),
 ],
 "ai-video": [
 ("https://www.lumen5.com/", "Lumen5", "free-tier"),
 ("https://www.synthesia.io/", "Synthesia", "free-tier"),
 ],
 "ai-voice": [
 ("https://play.ht/", "Play.ht", "free-tier"),
 ("https://murf.ai/", "Murf", "free-tier"),
 ],
 "cybersecurity": [
 ("https://www.root-me.org/", "Root Me"),
 ("https://www.hackthissite.org/", "HackThisSite"),
 ],
 "data-science": [
 ("https://www.databricks.com/try-databricks", "Databricks", "free-tier"),
 ("https://www.streamlit.io/", "Streamlit"),
 ],
 "privacy-tools": [
 ("https://www.torproject.org/", "Tor Browser"),
 ("https://mullvad.net/", "Mullvad", "free-tier"),
 ("https://www.mozilla.org/firefox/", "Firefox"),
 ],
 "grammar-writing-ai": [
 ("https://www.prowritingaid.com/", "ProWritingAid", "free-tier"),
 ("https://www.ginger.com/", "Ginger", "free-tier"),
 ],
 "translation": [
 ("https://www.deepl.com/translator", "DeepL", "free-tier"),
 ("https://lingva.ml/", "Lingva"),
 ],
 "focus-productivity": [
 ("https://www.noisli.com/", "Noisli", "free-tier"),
 ("https://asoftmurmur.com/", "A Soft Murmur"),
 ],
 "ai-study-tools": [
 ("https://www.socratic.org/", "Socratic"),
 ("https://www.brainly.com/", "Brainly", "free-tier"),
 ],
 "code-editors": [
 ("https://www.jdoodle.com/", "JDoodle"),
 ("https://onecompiler.com/", "OneCompiler"),
 ],
 "ai-image-editing": [
 ("https://www.remove.bg/", "Remove.bg", "free-tier"),
 ("https://www.befunky.com/", "BeFunky", "free-tier"),
 ],
 "open-courseware": [
 ("https://www.coursera.org/", "Coursera", "free-tier"),
 ("https://www.khanacademy.org/", "Khan Academy"),
 ("https://www.codecademy.com/", "Codecademy", "free-tier"),
 ],
 "utilities": [
 ("https://www.unitconverters.net/", "Unit Converters"),
 ("https://www.timeanddate.com/worldclock/", "World Clock"),
 ("https://www.epochconverter.com/", "Epoch Converter"),
 ],
 "research": [
 ("https://scholar.google.com/", "Google Scholar"),
 ("https://www.semanticscholar.org/", "Semantic Scholar"),
 ("https://arxiv.org/", "arXiv"),
 ("https://www.base-search.net/", "BASE Search"),
 ],
 "essay-tools": [
 ("https://www.quetext.com/", "Quetext", "free-tier"),
 ("https://www.plagscan.com/", "PlagScan", "free-tier"),
 ],
 "vpn-security": [
 ("https://www.cloudflare.com/learning/", "Cloudflare Learn"),
 ("https://mullvad.net/", "Mullvad", "free-tier"),
 ],
 "social-media": [
 ("https://hootsuite.com/", "Hootsuite", "free-tier"),
 ("https://www.canva.com/", "Canva", "free-tier"),
 ],
 "databases": [
 ("https://planetscale.com/", "PlanetScale", "free-tier"),
 ("https://turso.tech/", "Turso", "free-tier"),
 ],
 "api-testing": [
 ("https://www.usebruno.com/", "Bruno"),
 ("https://rapidapi.com/", "RapidAPI", "free-tier"),
 ],
 "stock-media": [
 ("https://www.videvo.net/", "Videvo"),
 ("https://www.videezy.com/", "Videezy"),
 ("https://freesound.org/", "Freesound"),
 ],
 "fonts-typography": [
 ("https://fontjoy.com/", "Fontjoy"),
 ("https://www.typewolf.com/", "Typewolf"),
 ],
 "color-tools": [
 ("https://www.realtimecolors.com/", "Realtime Colors"),
 ("https://www.happyhues.co/", "Happy Hues"),
 ],
 "file-sharing": [
 ("https://www.mediafire.com/", "MediaFire", "free-tier"),
 ("https://gofile.io/", "GoFile"),
 ],
 "mind-mapping": [
 ("https://bubbl.us/", "bubbl.us", "free-tier"),
 ("https://www.xmind.net/", "XMind", "free-tier"),
 ],
 "scheduling": [
 ("https://www.worldtimebuddy.com/", "World Time Buddy"),
 ("https://time.is/", "Time.is"),
 ],
 "collaboration": [
 ("https://www.whereby.com/", "Whereby", "free-tier"),
 ("https://around.co/", "Around", "free-tier"),
 ],
 "website-builders": [
 ("https://webflow.com/", "Webflow", "free-tier"),
 ("https://bubble.io/", "Bubble", "free-tier"),
 ],
 "all-in-one-tools": [
 ("https://www.ilovepdf.com/", "iLovePDF", "free-tier"),
 ("https://www.iloveimg.com/", "iLoveIMG", "free-tier"),
 ],
 "pdf": [
 ("https://www.pdfescape.com/", "PDFescape", "free-tier"),
 ("https://www.docfly.com/", "DocFly", "free-tier"),
 ],
 "image": [
 ("https://www.squoosh.app/", "Squoosh"),
 ("https://www.photopea.com/", "Photopea", "free-tier"),
 ],
 "video": [
 ("https://www.blackmagicdesign.com/products/davinciresolve", "DaVinci Resolve"),
 ("https://www.videosoftdev.com/", "VSDC", "free-tier"),
 ],
 "audio": [
 ("https://www.mp3tag.de/en/", "Mp3tag"),
 ("https://www.audacityteam.org/", "Audacity"),
 ],
 "design": [
 ("https://www.sketch.com/", "Sketch", "free-tier"),
 ("https://www.figma.com/community", "Figma Community", "free-tier"),
 ],
 "todo-list": [
 ("https://habitica.com/", "Habitica", "free-tier"),
 ("https://www.rememberthemilk.com/", "Remember The Milk", "free-tier"),
 ],
 "notepad": [
 ("https://hackmd.io/", "HackMD", "free-tier"),
 ("https://bear.app/", "Bear", "free-tier"),
 ],
 "chrome-extension": [
 ("https://www.toby.io/", "Toby", "free-tier"),
 ("https://www.onetab.com/", "OneTab"),
 ],
 "browser-extensions": [
 ("https://www.tampermonkey.net/", "Tampermonkey"),
 ("https://www.bypass-paywalls-clean.org/", "Bypass Paywalls"),
 ],
 "secret": [
 ("https://unpaywall.org/", "Unpaywall"),
 ],
 "free-stuff": [
 ("https://fmhy.net/educational", "FMHY Educational"),
 ("https://fmhy.net/privacy", "FMHY Privacy"),
 ],
 "courses": [
 ("https://www.udacity.com/", "Udacity", "free-tier"),
 ("https://www.skillshare.com/", "Skillshare", "free-tier"),
 ],
 "ai": [
 ("https://www.mistral.ai/", "Mistral", "free-tier"),
 ("https://cohere.com/", "Cohere", "free-tier"),
 ],
 "ai-browser": [
 ("https://www.brave.com/", "Brave Browser"),
 ("https://www.vivaldi.com/", "Vivaldi"),
 ],
 "security": [
 ("https://www.passbolt.com/", "Passbolt", "free-tier"),
 ("https://vault.bitwarden.com/", "Bitwarden", "free"),
 ],
 "remote-jobs": [
 ("https://www.flexjobs.com/", "FlexJobs", "free-tier"),
 ("https://www.indeed.com/", "Indeed"),
 ],
 "resume-career": [
 ("https://www.zety.com/", "Zety", "free-tier"),
 ("https://resumegenius.com/", "Resume Genius", "free-tier"),
 ],
 "presentation": [
 ("https://prezi.com/", "Prezi", "free-tier"),
 ("https://www.visme.co/", "Visme", "free-tier"),
 ],
 "spreadsheets": [
 ("https://www.notion.so/", "Notion Tables", "free-tier"),
 ("https://baserow.io/", "Baserow", "free-tier"),
 ],
 "note-taking": [
 ("https://www.notion.so/", "Notion", "free-tier"),
 ("https://workflowy.com/", "Workflowy", "free-tier"),
 ],
 "math-science": [
 ("https://www.symbolab.com/", "Symbolab", "free-tier"),
 ("https://www.mathsisfun.com/", "Math is Fun"),
 ],
 "science": [
 ("https://www.sciencebuddies.org/", "Science Buddies"),
 ("https://www.sciencekids.co.nz/", "Science Kids"),
 ],
 "english": [
 ("https://www.vocabulary.com/", "Vocabulary.com", "free-tier"),
 ("https://www.merriam-webster.com/", "Merriam-Webster"),
 ],
 "writing": [
 ("https://www.citethisforme.com/", "Cite This For Me", "free-tier"),
 ("https://www.refworks.com/", "RefWorks", "free-tier"),
 ],
 "converters": [
 ("https://www.online-convert.com/", "Online-Convert"),
 ("https://products.aspose.app/", "Aspose Apps", "free-tier"),
 ],
 "email": [
 ("https://mail.yahoo.com/", "Yahoo Mail"),
 ("https://outlook.live.com/", "Outlook"),
 ],
 "cloud": [
 ("https://www.sync.com/", "Sync", "free-tier"),
 ("https://www.tresorit.com/", "Tresorit", "free-tier"),
 ],
 "online-poll": [
 ("https://www.pollfish.com/", "Pollfish", "free-tier"),
 ("https://www.surveycake.com/", "SurveyCake", "free-tier"),
 ],
 "online-whiteboard": [
 ("https://www.limnu.com/", "Limnu", "free-tier"),
 ("https://www.ziteboard.com/", "Ziteboard", "free-tier"),
 ],
 "programming": [
 ("https://www.hackerrank.com/", "HackerRank"),
 ("https://www.edabit.com/", "Edabit", "free-tier"),
 ],
 "gif-converters": [
 ("https://gifmaker.me/", "GIF Maker"),
 ("https://ezgif.com/maker", "EZGIF Maker"),
 ],
 "diagramming": [
 ("https://www.processon.com/", "ProcessOn", "free-tier"),
 ("https://www.gliffy.com/", "Gliffy", "free-tier"),
 ],
 "productivity": [
 ("https://clickup.com/", "ClickUp", "free-tier"),
 ("https://www.any.do/", "Any.do", "free-tier"),
 ],
 "study": [
 ("https://www.chegg.com/", "Chegg", "free-tier"),
 ("https://www.coursehero.com/", "Course Hero", "free-tier"),
 ],
 "music-podcasts": [
 ("https://podcasters.spotify.com/", "Spotify Podcasters"),
 ("https://anchor.fm/", "Anchor"),
 ],
 "live-streaming": [
 ("https://www.twitch.tv/", "Twitch"),
 ("https://kick.com/", "Kick"),
 ],
 "free-books": [
 ("https://manybooks.net/", "ManyBooks"),
 ("https://archive.org/details/texts", "Internet Archive"),
 ],
 "free-movies": [
 ("https://tubitv.com/", "Tubi"),
 ("https://pluto.tv/", "Pluto TV"),
 ],
}


def build_expand_link(t):
 url, name = t[0], t[1]
 pricing = t[2] if len(t) > 2 else "free"
 github = t[3] if len(t) > 3 else None
 return link(url, name, pricing, github=github)


html = HTML_PATH.read_text(encoding="utf-8")

# Expand existing categories
sections = {}
for m in SECTION_RE.finditer(html):
 cat = m.group(2)
 inner = m.group(3)
 urls = {norm_url(u) for u in HREF_RE.findall(inner)}
 sections[cat] = {"prefix": m.group(1), "inner": inner, "suffix": m.group(4), "urls": urls}

for cat, tools in EXPAND.items():
 if cat not in sections:
 continue
 add_lines = []
 for t in tools:
 key = norm_url(t[0])
 if key in sections[cat]["urls"]:
 continue
 sections[cat]["urls"].add(key)
 add_lines.append(build_expand_link(t))
 if add_lines:
 sections[cat]["inner"] = sections[cat]["inner"] + "".join(add_lines)

def replacer(m):
 cat = m.group(2)
 if cat not in sections:
 return m.group(0)
 s = sections[cat]
 return s["prefix"] + s["inner"] + s["suffix"]

html = SECTION_RE.sub(replacer, html)

# Append new categories before closing tools-directory div
new_blocks = []
for cat_id, (title, tools) in NEW_CATEGORIES.items():
 if f'data-category="{cat_id}"' in html:
 continue
 new_blocks.append(section_block(cat_id, title, tools))

if new_blocks:
 marker = "\n </div>\n </main>"
 insert = "\n" + "\n".join(new_blocks) + marker
 html = html.replace(marker, insert, 1)

HTML_PATH.write_text(html, encoding="utf-8")
print(f"Updated {HTML_PATH}")
print(f"New categories: {len(new_blocks)}")
print(f"Expanded categories: {len(EXPAND)}")
