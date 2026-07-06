"""List 'free' tagged tools that may need review."""
import re
from pathlib import Path
from urllib.parse import urlparse

HTML = Path(__file__).resolve().parent.parent / "student.html"
LINK_RE = re.compile(
    r'href="([^"]+)"[^>]*data-pricing="free"[^>]*>.*?<span class="tool-link-name">([^<]+)</span>',
    re.DOTALL,
)

# Known legitimately free (OSS, edu, gov, community)
OK_FRAGMENTS = [
    "github.com", "gitlab.com", "gutenberg", "openstax", "wikipedia", "wikimedia",
    "archive.org", "openlibrary", "libgen", "annas-archive", "oceanofpdf", "z-lib",
    "khanacademy", "freecodecamp", "mdn", "w3schools", "mozilla", "arxiv",
    "semanticscholar", "scholar.google", "pubmed", "mit.edu", "stanford.edu",
    "harvard.edu", "phet.colorado", "desmos", "geogebra", "excalidraw", "draw.io",
    "diagrams.net", "gimp", "inkscape", "blender", "krita", "audacity", "obs",
    "handbrake", "libreoffice", "notepad-plus", "keepass", "syncthing", "jitsi",
    "fmhy", "eye2.ai", "vocalremover", "freebuff", "removepaywall", "uncensored",
    "ollama", "langchain", "open-webui", "tldraw", "whiteboard.fi", "limnu",
    "ziteboard", "kleki", "pixilart", "autodraw", "coolmathgames", "itch.io",
    "poki.com", "crazygames", "temple", "subway", "minecraft", "fancy",
    "tubi", "pluto", "soap2day", "flix", "fmovies", "1337x", "primewire",
    "streameast", "sporty", "open.spotify",  # spotify should be free-tier - check
    "alison.com", "open.edu", "openlearn", "saylor", "libretexts", "wikibooks",
    "goblin.tools", "when2meet", "time.is", "worldtimebuddy", "web3forms",
    "hoppscotch", "kdenlive", "tinkercad", "langflow", "flowise", "penpot",
    "photopea", "lunacy", "color.adobe", "tinywow", "pdf24", "ilovepdf",
    "snapdrop", "pixeldrain", "send.cm", "wetransfer",  # wetransfer fixed
    "jsonplaceholder", "httpbin", "mockoon", "beeceptor", "reqbin", "swagger",
    "sqliteonline", "jsonlint", "prettier", "base64", "jwt.io", "uuid",
    "caniuse", "regex101", "devdocs", "quickref", "cheatography",
    "fonts.google", "dafont", "fontshare", "fontjoy", "colormind", "coolors",
    "happyhues", "htmlcolorcodes", "colorhunt", "encycolorpedia",
    "remove.bg",  # fixed
    "insighttimer", "nike.com/ntc",  # ntc free
    "calculator.net", "speedtest", "fast.com", "downforeveryone",
    "temp-mail", "guerrillamail", "10minutemail",
    "radio.garden", "listen.moe", "ncs.io", "freemusicarchive",
    "cobalt", "lucida", "soundcloud",  # soundcloud free-tier?
    "bandcamp", "music.youtube",
    "python.org", "nodejs.org", "rust-lang", "golang.org", "ruby-lang",
    "developer.apple", "android.com", "kotlinlang", "scala-lang", "php.net",
    "r-project", "jupyter", "colab.research.google",  # colab free
    "replit",  # fixed
    "scratch.mit", "exercism", "codewars", "projecteuler",
    "leetcode",  # fixed
    "geeksforgeeks", "tutorialspoint", "javatpoint", "programiz",
    "stackoverflow", "stackexchange", "reddit.com", "quora.com",
    "alternativeto", "producthunt", "slant.co",
    "duckduckgo", "searx", "brave.com/search",
    "protonvpn", "windscribe",  # windscribe free-tier?
    "mullvad",  # paid
    "riseup", "tutanota", "proton.me",  # proton free-tier
    "gmail", "mail.google",
    "calendar.google", "when2meet",
    "google.com/forms", "docs.google", "sheets.google", "slides.google",
    "notion",  # should be free-tier
    "obsidian",  # free for personal
    "joplin", "standardnotes", "simplenote", "google.com/keep",
    "zotero", "mendeley",  # mendeley free-tier?
    "libreoffice", "overleaf",  # overleaf free-tier
    "bibtex", "citationmachine", "easybib",
    "wordcounter", "hemingwayapp",  # hemingway limited free?
    "languagetool",  # free-tier
    "deepl.com/translator",  # free-tier
    "translate.google",
    "reverso", "linguee", "wordreference",
    "codecademy",  # limited free
    "sololearn", "scrimba",  # freemium
    "theodinproject", "fullstackopen", "javascript.info",
    "cs50", "ocw.mit", "oyc.yale",
    "brilliant.org",  # limited
    "phet.", "wolframalpha",  # limited now
    "mathisfun", "mathway",  # mathway free-tier
    "cymath", "symbolab",  # free-tier
    "numworks", "geogebra",
    "periodic", "ptable", "chemcollective",
    "nasa.gov", "noaa.gov", "usgs.gov", "cdc.gov", "nih.gov",
    "britannica",  # free-tier partial
    "ted.com", "youtube.com", "youtu.be",
    "vimeo.com",  # free-tier
    "dailymotion",
    "imgur", "imgbb", "postimages",
    "squoosh", "squoosh.app",
    "remove.bg", "cleanup.pictures",
    "unsplash", "pexels", "pixabay", "coverr", "mixkit", "videvo", "freesound",
    "coolors", "fontpair",
    "miro",  # free-tier
    "slack",  # free-tier
    "discord",
    "zoom",  # free-tier
    "teams.microsoft",  # free-tier
    "whereby",  # free-tier
    "meet.jit",
    "raindrop",  # free-tier
    "pocket",  # free-tier
    "feedly",  # free-tier
    "inoreader",  # free-tier
    "instapaper",  # free-tier
    "news.ycombinator", "lobste.rs",
    "hackerone", "bugcrowd",
    "haveibeenpwned",
    "virustotal",  # free-tier
    "urlscan",
    "shodan.io",  # free-tier
    "censys.io",  # free-tier
    "crt.sh", "dns.google",
    "iplocation", "whatismyip",
    "whois",
    "wappalyzer",  # free-tier extension
    "builtwith",  # free-tier
    "similarweb",  # free-tier
    "semrush",  # limited
    "ahrefs",  # paid
    "moz.com",  # free-tier limited
    "pages.github", "vercel", "netlify",  # free-tier
    "neocities", "glitch",  # glitch gone
    "surge.sh", "render.com",  # free-tier
    "railway.app",  # free-tier limited
    "fly.io",  # free-tier limited
    "supabase",  # free-tier
    "neon.tech",  # free-tier
    "planetscale",  # free-tier
    "turso",  # free-tier
    "mongodb.com/atlas",  # free-tier
    "firebase.google",  # free-tier
    "appwrite",  # free OSS
    "pocketbase",  # free OSS
    "directus",  # free OSS
    "strapi",  # free OSS
    "sanity.io",  # free-tier
    "contentful",  # free-tier
    "airtable",  # free-tier
    "clickup",  # free-tier
    "monday.com",  # free-tier limited
    "basecamp",  # paid
    "linear.app",  # free-tier
    "height.app",  # free-tier
    "shortcut",  # free-tier
    "openproject",  # free OSS
    "taiga",  # free OSS
    "wekan",  # free OSS
    "focalboard",  # free OSS
    "logseq",  # free
    "remnote",  # free-tier
    "roamresearch",  # paid
    "amplenote",  # free-tier
    "bear.app",  # paid apple
    "ulysses",  # paid
    "ia.net/writer",  # paid
    "typora",  # paid
    "marktext",  # free OSS
    "zettlr",  # free OSS
    "hackmd",  # free-tier
    "stackedit",  # free
    "dillinger",  # free
    "notion", "coda",  # free-tier
    "airtable",
    "clickup",
    "coggle",  # free-tier
    "whimsical",  # free-tier
    "mindmeister",  # free-tier
    "xmind",  # free-tier limited
    "freemind",  # free OSS
    "freeplane",  # free OSS
    "lucidchart",  # free-tier
    "eraser",  # free-tier
    "mermaid.live",  # free
    "plantuml",  # free
    "asciiflow",  # free
    "excalidraw",
    "drawsql",  # free-tier
    "dbdiagram",  # free-tier
    "sqliteonline",
    "dbeaver",  # free OSS
    "pgadmin",  # free OSS
    "postman",  # free-tier
    "insomnia",  # free-tier
    "hoppscotch",
    "swagger",
    "stoplight",  # free-tier
    "readme.io",  # free-tier
    "gitbook",  # free-tier
    "docusaurus",  # free OSS
    "mkdocs",  # free OSS
    "hugo",  # free OSS
    "jekyll",  # free OSS
    "gatsby",  # free OSS
    "nextjs",  # free OSS
    "vitejs",  # free OSS
    "webpack",  # free OSS
    "parceljs",  # free OSS
    "eslint",  # free OSS
    "prettier",  # free OSS
    "stylelint",  # free OSS
    "biomejs",  # free OSS
    "rome",  # deprecated
    "storybook",  # free OSS
    "chromatic",  # free-tier
    "figma",  # free-tier fixed
    "canva",  # free-tier
    "penpot",  # free OSS
    "lunacy",
    "framer",  # free-tier
    "webflow",  # free-tier limited
    "bubble.io",  # free-tier limited
    "softr",  # free-tier
    "glide",  # free-tier
    "adalo",  # free-tier
    "flutterflow",  # free-tier
    "buildfire",  # paid
    "shopify",  # paid trial
    "woocommerce",  # free OSS
    "magento",  # free OSS community
    "prestashop",  # free OSS
    "opencart",  # free OSS
    "bigcommerce",  # paid
    "squarespace",  # paid
    "wix",  # free-tier
    "wordpress.com",  # free-tier
    "blogger.com",  # free
    "tumblr.com",  # free
    "mastodon",  # free OSS instances
    "bsky.app",  # free
    "threads.net",  # free
    "discord",
    "telegram.org",  # free
    "signal.org",  # free
    "element.io",  # free OSS
    "matrix.org",  # free OSS
    "riot.im",
    "snapchat",  # free
    "tiktok",  # free
    "instagram",  # free
    "twitter.com", "x.com",  # free-tier X premium
    "facebook.com",  # free
    "reddit",
    "pinterest",  # free
    "linkedin",  # paid fixed
    "buffer",  # free-tier
    "hootsuite",  # free-tier limited
    "later.com",  # free-tier
    "metricool",  # free-tier
    "linktr.ee",  # free-tier
    "bio.link",  # free-tier
    "beacons.ai",  # free-tier
    "carrd",  # free-tier
    "about.me",  # free-tier
    "linktree",
    "stan.store",  # paid
    "gumroad",  # free-tier
    "patreon",  # free to browse
    "ko-fi",  # free-tier
    "buymeacoffee",  # free-tier
    "opencollective",  # free
    "github.com/sponsors",
    "stripe.com",  # paid service
    "paypal",  # free to use
    "venmo",  # free
    "cashapp",  # free
    "revolut",  # free-tier
    "wise.com",  # free-tier
    "mint.com",  # free
    "creditkarma",  # free
    "splitwise",  # free-tier
    "waveapps",  # free-tier
    "goodbudget",  # free-tier
    "ynab",  # paid
    "personalcapital", "empower.com",  # free
    "nerdwallet",  # free
    "bankrate",  # free
    "investopedia",  # free
    "tradingview",  # free-tier
    "yahoo.com/finance",  # free-tier
    "google.com/finance",  # free
    "marketwatch",  # free-tier
    "bloomberg",  # paid
    "reuters",  # free-tier
    "apnews",  # free
    "bbc.com",  # free
    "npr.org",  # free
    "spotify",  # free-tier
    "apple.com/music",  # paid
    "tidal.com",  # paid
    "deezer",  # free-tier
    "pandora",  # free-tier
    "last.fm",  # free-tier
    "discogs",  # free
    "musicbrainz",  # free
    "musescore",  # free-tier
    "flat.io",  # free-tier
    "soundtrap",  # free-tier
    "soundation",  # free-tier
    "lmms",  # free OSS
    "ardour",  # free OSS pay what you want
    "reaper",  # paid trial
    "cakewalk",  # free
    "waveform",  # free OSS
    "shotcut",  # free OSS
    "openshot",  # free OSS
    "davinci resolve",  # free version
    "blackmagicdesign",  # resolve free
    "capcut",  # free-tier
    "invideo",  # free-tier
    "clipchamp",  # free-tier
    "canva",
    "runway",  # free-tier
    "pika",  # free-tier
    "kling",  # free-tier
    "haiper",  # free-tier
    "lumen5",  # free-tier
    "animoto",  # free-tier
    "biteable",  # free-tier
    "powtoon",  # free-tier
    "prezi",  # free-tier
    "beautiful.ai",  # free-tier
    "slidesgo",  # free-tier
    "slidebean",  # free-tier
    "pitch.com",  # free-tier
    "gamma.app",  # free-tier
    "tome.app",  # free-tier
    "notion",
    "craft",
    "reflect",
    "capacities",
    "mem.ai",
    "evernote",  # free-tier
    "onenote",  # free
    "google keep",
    "simplenote",
    "standardnotes",  # free-tier
    "joplin",
    "obsidian",  # free personal
    "logseq",
    "remnote",
    "roam",
    "amplenote",
    "bear",
    "ulysses",
    "ia.net",
    "typora",
    "marktext",
    "zettlr",
    "hackmd",
    "stackedit",
    "dillinger",
    "notion",
    "coda",
    "airtable",
    "clickup",
    "monday",
    "basecamp",
    "linear",
    "height",
    "shortcut",
    "openproject",
    "taiga",
    "wekan",
    "focalboard",
    "miro",
    "mural",  # free-tier limited
    "conceptboard",  # free-tier
    "stormboard",  # free-tier
    "ideaflip",  # paid
    "groupmap",  # paid
    "lucidspark",  # free-tier
    "figjam",  # free-tier
    "milanote",  # free-tier
    "padlet",  # free-tier
    "wakelet",  # free-tier
    "pearltrees",  # free-tier
    "raindrop",
    "pocket",
    "instapaper",
    "omnivore",  # free OSS
    "matter",  # free-tier
    "readwise",  # paid
    "feedly",
    "inoreader",
    "newsblur",  # free-tier
    "theoldreader",  # free-tier
    "netvibes",  # free-tier
    "flipboard",  # free
    "google news",
    "apple news",  # paid
    "ground.news",  # free-tier
    "allsides",  # free
    "snopes",  # free
    "factcheck",  # free
    "politifact",  # free
    "fullfact",  # free
    "reuters/fact-check",
]

def main():
    html = HTML.read_text(encoding="utf-8")
    review = []
    for m in LINK_RE.finditer(html):
        url, name = m.group(1), m.group(2).strip()
        low = url.lower()
        if any(f in low for f in OK_FRAGMENTS):
            continue
        host = urlparse(url).netloc.lower().replace("www.", "")
        # skip obvious free TLD patterns
        if host.endswith(".gov") or host.endswith(".edu") or host.endswith(".ac.uk"):
            continue
        review.append((name, url, host))

    print(f"Free-tagged tools needing review: {len(review)}")
    for name, url, host in sorted(review, key=lambda x: x[2])[:80]:
        print(f"  {name:30} {host:35} {url}")
    if len(review) > 80:
        print(f"  ... {len(review) - 80} more")


if __name__ == "__main__":
    main()
