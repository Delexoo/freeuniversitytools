"""Fix data-pricing tags in student.html using curated URL/host rules."""
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
HTML_PATH = ROOT / "student.html"

LINK_RE = re.compile(
    r'(<a\s+href="[^"]+"[^>]*data-pricing=")([^"]+)("[^>]*>.*?<span class="tool-link-name">[^<]+</span></a>)',
    re.DOTALL,
)
HREF_RE = re.compile(r'href="([^"]+)"')


def host_key(url):
    p = urlparse(url.strip())
    return p.netloc.lower().replace("www.", "")


def path_key(url):
    p = urlparse(url.strip().rstrip("/"))
    h = p.netloc.lower().replace("www.", "")
    path = p.path.rstrip("/").lower()
    return f"{h}{path}"


# Exact path overrides (host+path)
EXACT = {
    "quillbot.com/word-counter": "free-tier",
    "chegg.com/internships": "free-tier",
    "github.com/features/copilot": "free-tier",
    "podcast.adobe.com/enhance": "free-tier",
    "color.adobe.com": "free",
    "open.edu/openlearn": "free",
    "icons8.com/lunacy": "free",
    "hoppscotch.io": "free",
    "kdenlive.org": "free",
    "tinkercad.com": "free",
    "worldtimebuddy.com": "free",
    "web3forms.com": "free",
    "jdoodle.com": "free-tier",
    "podcasters.spotify.com": "free-tier",
    "langflow.org": "free",
    "flowiseai.com": "free",
    "ollama.com": "free",
    "lightpdf.com/chatdoc": "free-tier",
    "linkedin.com/learning": "paid",
    "linkedin.com/jobs": "free",
    "lynda.com": "paid",
}

# Host-level defaults (longest match wins via exact first, then host)
HOST = {
    # Primarily paid subscription services
    "chegg.com": "paid",
    "coursehero.com": "paid",
    "studocu.com": "paid",
    "bartleby.com": "paid",
    "lynda.com": "paid",
    "pluralsight.com": "paid",
    "youlearn.ai": "paid",

    # Freemium / free tier SaaS
    "notion.so": "free-tier",
    "canva.com": "free-tier",
    "figma.com": "free-tier",
    "slack.com": "free-tier",
    "zoom.us": "free-tier",
    "dropbox.com": "free-tier",
    "spotify.com": "free-tier",
    "grammarly.com": "limited",
    "quillbot.com": "limited",
    "chatgpt.com": "free-tier",
    "chat.openai.com": "free-tier",
    "claude.ai": "free-tier",
    "perplexity.ai": "free-tier",
    "gemini.google.com": "free-tier",
    "copilot.microsoft.com": "free-tier",
    "replit.com": "free-tier",
    "leetcode.com": "free-tier",
    "postman.com": "free-tier",
    "supabase.com": "free-tier",
    "neon.tech": "free-tier",
    "planetscale.com": "free-tier",
    "turso.tech": "free-tier",
    "mongodb.com": "free-tier",
    "vercel.com": "free-tier",
    "netlify.com": "free-tier",
    "mailchimp.com": "free-tier",
    "buffer.com": "free-tier",
    "calendly.com": "free-tier",
    "cal.com": "free-tier",
    "miro.com": "free-tier",
    "evernote.com": "free-tier",
    "todoist.com": "free-tier",
    "trello.com": "free-tier",
    "asana.com": "free-tier",
    "remove.bg": "free-tier",
    "smallpdf.com": "free-tier",
    "ilovepdf.com": "free-tier",
    "deepl.com": "free-tier",
    "overleaf.com": "free-tier",
    "elevenlabs.io": "free-tier",
    "runwayml.com": "free-tier",
    "runway.com": "free-tier",
    "midjourney.com": "free-tier",
    "tabnine.com": "free-tier",
    "codeium.com": "free-tier",
    "wix.com": "free-tier",
    "wordpress.com": "free-tier",
    "carrd.co": "free-tier",
    "ynab.com": "free-tier",
    "headspace.com": "free-tier",
    "calm.com": "free-tier",
    "strava.com": "free-tier",
    "brainscape.com": "free-tier",
    "quizlet.com": "free-tier",
    "coursera.org": "free-tier",
    "udemy.com": "free-tier",
    "skillshare.com": "limited",
    "linkedin.com": "free-tier",
    "zapier.com": "free-tier",
    "make.com": "free-tier",
    "ifttt.com": "free-tier",
    "n8n.io": "free-tier",
    "storyblocks.com": "free-tier",
    "adobe.com": "free-tier",
    "sketch.com": "free-tier",
    "framer.com": "free-tier",
    "loom.com": "free-tier",
    "descript.com": "free-tier",
    "veed.io": "free-tier",
    "capcut.com": "free-tier",
    "invideo.io": "free-tier",
    "animaker.com": "free-tier",
    "bitwarden.com": "free-tier",
    "1password.com": "paid",
    "lastpass.com": "free-tier",
    "insomnia.rest": "free-tier",
    "feedly.com": "free-tier",
    "raindrop.io": "free-tier",
    "getpocket.com": "free-tier",
    "instapaper.com": "free-tier",
    "character.ai": "free-tier",
    "poe.com": "free-tier",
    "you.com": "free-tier",
    "pi.ai": "free-tier",
    "mem.ai": "free-tier",
    "reflect.app": "free-tier",
    "craft.do": "free-tier",
    "capacities.io": "free-tier",
    "humata.ai": "free-tier",
    "chatpdf.com": "free-tier",
    "pdf.ai": "free-tier",
    "lightpdf.com": "free-tier",
    "symbolab.com": "free-tier",
    "mathway.com": "free-tier",
    "wolframalpha.com": "limited",
    "geoguessr.com": "free-tier",
    "duolingo.com": "free-tier",
    "memrise.com": "free-tier",
    "babbel.com": "paid",
    "chat.qwen.ai": "free-tier",
    "qwen.ai": "free-tier",
    "sololearn.com": "free-tier",
    "busuu.com": "free-tier",
    "craiyon.com": "free-tier",
    "anytype.io": "free-tier",
    "obsidian.md": "free",
    "chat.deepseek.com": "free-tier",
    "deepseek.com": "free-tier",
    "grok.com": "free-tier",
    "x.ai": "free-tier",
    "bing.com": "free-tier",
    "diffchecker.com": "free-tier",
    "scrimba.com": "free-tier",
    "brilliant.org": "limited",
    "codecademy.com": "limited",
    "hemingwayapp.com": "limited",
    "vimeo.com": "free-tier",
    "virustotal.com": "free-tier",
    "render.com": "free-tier",
    "railway.app": "free-tier",
    "firebase.google.com": "free-tier",
    "sanity.io": "free-tier",
    "linear.app": "free-tier",
    "onenote.com": "free",
    "microsoft.com/microsoft-365/onenote": "free",
    "google.com/keep": "free",
    "simplenote.com": "free",
    "standardnotes.com": "free-tier",
    "joplinapp.org": "free",
    "logseq.com": "free",
    "zotero.org": "free",
    "mendeley.com": "free-tier",
    "overleaf.com": "free-tier",
    "deepl.com": "free-tier",
    "translate.google.com": "free",
    "windscribe.com": "free-tier",
    "protonvpn.com": "free-tier",
    "mega.nz": "free-tier",
    "icloud.com": "free-tier",
    "open.spotify.com": "free-tier",
    "music.youtube.com": "free-tier",
    "anchor.fm": "free",
    "10015.io": "free",
    "anara.ai": "free-tier",
    "app.gptzero.me": "free-tier",
    "gptzero.me": "free-tier",
    "designarena.ai": "free-tier",
    "disco.google.com": "free-tier",
    "manus.im": "free-tier",
    "notebooklm.google": "free",
    "socratic.org": "free",
    "brainly.com": "free-tier",
    "studyfetch.com": "free-tier",
    "roamresearch.com": "paid",
    "ahrefs.com": "paid",
    "squarespace.com": "paid",
    "proton.me": "free-tier",
    "ticktick.com": "free-tier",
    "any.do": "free-tier",
    "wetransfer.com": "free-tier",
    "box.com": "free-tier",
    "icedrive.net": "free-tier",
    "backblaze.com": "free-tier",
    "idrive.com": "free-tier",
    "pcloud.com": "free-tier",
    "later.com": "free-tier",
    "metricool.com": "free-tier",
    "hootsuite.com": "free-tier",
    "mailerlite.com": "free-tier",
    "brevo.com": "free-tier",
    "sendpulse.com": "free-tier",
    "mailjet.com": "free-tier",
    "ghost.org": "free-tier",
    "substack.com": "free-tier",
    "medium.com": "free-tier",
    "dify.ai": "free-tier",
    "gradescope.com": "free-tier",
    "magoosh.com": "free-tier",
    "photomath.com": "free-tier",
    "naturalreaders.com": "free-tier",
    "speechify.com": "free-tier",
    "murf.ai": "free-tier",
    "suno.com": "free-tier",
    "udio.com": "free-tier",
    "lovo.ai": "free-tier",
    "freepik.com": "free-tier",
    "flaticon.com": "free-tier",
    "icons8.com": "free-tier",
    "iconscout.com": "free-tier",
    "placeit.net": "free-tier",
    "smartmockups.com": "free-tier",
    "looka.com": "free-tier",
    "soundtrap.com": "free-tier",
    "soundation.com": "free-tier",
    "bandlab.com": "free-tier",
    "scholarshipowl.com": "free-tier",
    "cappex.com": "free-tier",
    "pipedream.com": "free-tier",
    "activepieces.com": "free-tier",
    "whimsical.com": "free-tier",
    "mindmeister.com": "free-tier",
    "coggle.it": "free-tier",
    "mindomo.com": "free-tier",
    "lucidchart.com": "free-tier",
    "smartdraw.com": "free-tier",
    "eraser.io": "free-tier",
    "splitwise.com": "free-tier",
    "waveapps.com": "free-tier",
    "goodbudget.com": "free-tier",
    "myfitnesspal.com": "free-tier",
    "teams.microsoft.com": "free-tier",
    "whereby.com": "free-tier",
    "doodle.com": "free-tier",
    "4shared.com": "free-tier",
    "mediafire.com": "free-tier",
    "befunky.com": "free-tier",
    "fotor.com": "free-tier",
    "pixlr.com": "free-tier",
    "photoroom.com": "free-tier",
    "stylar.ai": "free-tier",
    "cleanup.pictures": "free-tier",
    "connectedpapers.com": "free-tier",
    "litmaps.com": "free-tier",
    "scite.ai": "free-tier",
    "elicit.org": "free-tier",
    "julius.ai": "free-tier",
    "chatcsv.com": "free-tier",
    "phind.com": "free-tier",
    "replika.com": "free-tier",
    "journey.cloud": "free-tier",
    "penzu.com": "free-tier",
    "dayoneapp.com": "free-tier",
    "zoho.com": "free-tier",
    "getform.io": "free-tier",
    "formspree.io": "free-tier",
    "convertio.co": "free-tier",
    "products.aspose.app": "free-tier",
    "pdf2go.com": "free-tier",
    "sketchup.com": "free-tier",
    "spline.design": "free-tier",
    "drawsql.app": "free-tier",
    "dbdiagram.io": "free-tier",
    "sophia.org": "free-tier",
    "alison.com": "free",
    "open.edu": "free",
    "writersdigest.com": "free-tier",
    "britannica.com": "free-tier",
    "debuggex.com": "free-tier",
    "accessibilitychecker.org": "free-tier",
    "gitkraken.com": "free-tier",
    "gitlab.com": "free-tier",
    "sumopaint.com": "free-tier",
    "emergent.sh": "free-tier",
    "cursor.com": "free-tier",
    "cloudconvert.com": "free-tier",
    "onlineocr.net": "free-tier",
    "123apps.com": "free-tier",
    "toolfk.com": "free-tier",
    "tinywow.com": "free",
    "dataquest.io": "limited",
    "datacamp.com": "limited",
    "hume.ai": "free-tier",
    "venice.ai": "free-tier",
    "cluely.com": "limited",
    "uncensored.chat": "limited",
    "dyad.sh": "limited",
    "aistudio.google.com": "free-tier",
    "scribbr.com": "limited",
    "dbdiagram.io": "free-tier",
    "inoreader.com": "free-tier",
    "penpot.app": "free",
    "photopea.com": "free",
    "gimp.org": "free",
    "inkscape.org": "free",
    "krita.org": "free",
    "blender.org": "free",
    "audacityteam.org": "free",
    "obsproject.com": "free",
    "handbrake.fr": "free",
    "vscode.dev": "free",
    "codesandbox.io": "free-tier",
    "stackblitz.com": "free-tier",
    "codepen.io": "free-tier",
    "jsfiddle.net": "free",
    "excalidraw.com": "free",
    "draw.io": "free",
    "app.diagrams.net": "free",
    "notepad-plus-plus.org": "free",
    "libreoffice.org": "free",
    "openoffice.org": "free",
    "khanacademy.org": "free",
    "openstax.org": "free",
    "gutenberg.org": "free",
    "openlibrary.org": "free",
    "archive.org": "free",
    "wikimedia.org": "free",
    "wikipedia.org": "free",
    "wiktionary.org": "free",
    "mdn.mozilla.org": "free",
    "developer.mozilla.org": "free",
    "w3schools.com": "free",
    "freecodecamp.org": "free",
    "edx.org": "free-tier",
    "futurelearn.com": "free-tier",
    "udacity.com": "free-tier",
    "mit.edu": "free",
    "stanford.edu": "free",
    "harvard.edu": "free",
    "jupyter.org": "free",
    "colab.research.google.com": "free",
    "kaggle.com": "free-tier",
    "deepnote.com": "free-tier",
    "tableau.com": "free-tier",
    "docker.com": "free-tier",
    "portainer.io": "free-tier",
    "coolify.io": "free-tier",
    "beeceptor.com": "free-tier",
    "discord.com": "free",
    "meet.jit.si": "free",
    "jitsi.org": "free",
    "mega.nz": "free-tier",
    "onedrive.live.com": "free-tier",
    "drive.google.com": "free-tier",
    "icloud.com": "free-tier",
    "syncthing.net": "free",
    "tresorit.com": "paid",
    "keepassxc.org": "free",
    "keepass.info": "free",
    "passwords.google.com": "free-tier",
    "protonmail.com": "free-tier",
    "tutanota.com": "free-tier",
    "tuta.io": "free-tier",
    "fmhy.net": "free",
    "github.com": "free",
    "gitlab.com": "free-tier",
    "sourceforge.net": "free",
    "snapdrop.net": "free",
}

# Open-source / free-by-nature hosts always free
FREE_HOSTS = {
    "raw.githubusercontent.com", "gutenberg.org", "openstax.org", "libgen.ac",
    "annas-archive.gl", "oceanofpdf.com", "z-lib.gd", "arxiv.org", "semanticscholar.org",
    "scholar.google.com", "pubmed.ncbi.nlm.nih.gov", "ncbi.nlm.nih.gov",
}


def expected_pricing(url):
    pk = path_key(url)
    if pk in EXACT:
        return EXACT[pk]
    for exact_path, pricing in EXACT.items():
        if "/" in exact_path and pk.startswith(exact_path):
            return pricing

    host = host_key(url)
    if host in FREE_HOSTS:
        return "free"
    if host in HOST:
        return HOST[host]

    # github repos are free
    if host == "github.com":
        return "free"

    # subdomains: check parent
    parts = host.split(".")
    for i in range(len(parts) - 1):
        parent = ".".join(parts[i:])
        if parent in HOST:
            return HOST[parent]

    return None


def main():
    html = HTML_PATH.read_text(encoding="utf-8")
    changes = []

    def replacer(m):
        prefix, current, suffix = m.group(1), m.group(2), m.group(3)
        href_m = HREF_RE.search(prefix + current + suffix)
        if not href_m:
            return m.group(0)
        url = href_m.group(1)
        expected = expected_pricing(url)
        if expected and expected != current:
            name_m = re.search(r'<span class="tool-link-name">([^<]+)</span>', suffix)
            name = name_m.group(1) if name_m else url
            changes.append((name, current, expected, url))
            return f"{prefix}{expected}{suffix}"
        return m.group(0)

    new_html = LINK_RE.sub(replacer, html)

    if changes:
        HTML_PATH.write_text(new_html, encoding="utf-8")

    print(f"Updated {len(changes)} pricing tags")
    for name, old, new, url in sorted(changes, key=lambda x: (x[3], x[0])):
        print(f"  {name}: {old} -> {new}  ({url})")


if __name__ == "__main__":
    main()
