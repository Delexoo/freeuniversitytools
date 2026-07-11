"""Comprehensive pricing tag engine for student.html."""
from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
HTML_PATH = ROOT / "student.html"
RULES_PATH = Path(__file__).resolve().parent / "pricing_rules.json"

VALID = {"free", "free-tier", "limited", "paid"}

# Category defaults when no host-specific rule exists.
CATEGORY_DEFAULTS = {
    "free-movies": "free",
    "live-streaming": "free",
    "free-books": "free",
    "free-stuff": "free",
    "browser-games": "free",
    "gif-converters": "free",
    "open-source": "free",
    "open-courseware": "free",
    "scholarships": "free",
    "github-powerhouses": "free",
    "encode-hash-tools": "free",
    "cheat-sheets": "free",
    "regex-devtools": "free",
    "markdown-tools": "free",
    "latex-docs": "free",
    "chrome-extension": "free",
    "browser-extensions": "free",
    "secret": "free",
    "immersive-reader": "free",
    "remote-jobs": "free",
    "utilities": "free",
    "translation": "free",
    "stock-media": "free",
    "fonts-typography": "free",
    "color-tools": "free",
    "geography-history": "free",
    "science": "free",
    "english": "free",
    "math-science": "free",
    "ebooks-textbooks": "free",
    "accessibility": "free",
    "typing-practice": "free",
    "art-drawing": "free",
    "icons-illustrations": "free",
    "mockups-templates": "free",
    "git-version-control": "free",
    "privacy-tools": "free",
    "vpn-security": "free",
}

# Hosts that are always free regardless of category.
ALWAYS_FREE_HOSTS = {
    "github.com",
    "raw.githubusercontent.com",
    "addons.mozilla.org",
    "reddit.com",
    "archive.org",
    "wikipedia.org",
    "wikimedia.org",
    "wiktionary.org",
    "gutenberg.org",
    "openstax.org",
    "openlibrary.org",
    "arxiv.org",
    "semanticscholar.org",
    "scholar.google.com",
    "pubmed.ncbi.nlm.nih.gov",
    "ncbi.nlm.nih.gov",
    "annas-archive.gl",
    "annas-archive.li",
    "libgen.ac",
    "libgen.li",
    "oceanofpdf.com",
    "z-lib.gd",
    "fmhy.net",
    "deepwebnest.com",
    "mozilla.org",
    "w3.org",
    "w3schools.com",
    "developer.mozilla.org",
    "mdn.mozilla.org",
    "python.org",
    "r-project.org",
    "stackoverflow.com",
    "stackexchange.com",
    "khanacademy.org",
    "freecodecamp.org",
    "theodinproject.com",
    "exercism.org",
    "codewars.org",
    "hackerrank.com",
    "scratch.mit.edu",
    "ocw.mit.edu",
    "cs50.harvard.edu",
    "saylor.org",
    "open.edu",
    "alison.com",
    "classcentral.com",
    "geeksforgeeks.org",
    "torproject.org",
    "privacyguides.org",
    "duckduckgo.com",
    "twitch.tv",
    "kick.com",
    "youtube.com",
    "youtu.be",
    "pluto.tv",
    "tubitv.com",
    "crackle.com",
    "alternativeto.net",
    "producthunt.com",
    "vocalremover.org",
    "speakapp.com",
    "tinywow.com",
    "10015.io",
    "ezgif.com",
    "squoosh.app",
    "photopea.com",
    "round-corner.imageonline.co",
    "imageonline.co",
    "excalidraw.com",
    "tldraw.com",
    "draw.io",
    "app.diagrams.net",
    "obsidian.md",
    "joplinapp.org",
    "logseq.com",
    "zotero.org",
    "ankiweb.net",
    "goblin.tools",
    "knowt.com",
    "syncthing.net",
    "snapdrop.net",
    "poki.com",
    "eaglercraft.com",
    "eye2.ai",
    "freebuff.com",
    "courtlistener.com",
    "exploit-db.com",
    "otx.alienvault.com",
    "googleguide.com",
    "gov.uk",
    "premid.app",
    "lemmy.world",
    "yandex.com",
    "twitter.com",
    "x.com",
    "facebook.com",
    "tiktok.com",
    "google.com",
    "fontsquirrel.com",
    "timeanddate.com",
    "towardsdatascience.com",
    "quora.com",
    "code.org",
    "mybib.com",
    "readaloud.net",
    "ttsreader.com",
    "readaloud.app",
    "mindluster.com",
    "skillsbuild.org",
    "skills.google",
    "cram.com",
    "poll-maker.com",
    "polleverywhere.com",
    "whiteboard.fi",
    "zed.dev",
    "roadmap.sh",
    "mui.com",
    "21st.dev",
    "uiverse.io",
    "penpot.app",
    "kokonutui.com",
    "bklit.com",
    "hellotalk.com",
    "tandem.net",
    "openshot.org",
    "shotcut.org",
    "blackmagicdesign.com",
    "opencut.app",
    "mp3tag.de",
    "gifmaker.me",
    "audacityteam.org",
    "mp3cut.net",
    "vsave.net",
    "cnvmp3.com",
    "naturalreaders.com",
    "base-search.net",
    "inteltechniques.com",
    "malwaredomainlist.com",
    "ipfingerprints.com",
    "cidr-report.org",
    "search.wikileaks.org",
    "addons.mozilla.org",
    "blog.didierstevens.com",
    "start.umd.edu",
    "continue.dev",
    "lobechat.com",
    "tabby.tabbyml.com",
    "math.bot",
    "magichour.ai",
    "flixer.su",
    "cineby.app",
    "bitcine.app",
    "lordflix.org",
    "xprime.su",
    "fmovies.gd",
    "cinegram.net",
    "1337x.to",
    "primewire.mov",
    "gostreameast.link",
    "sportyhunter.com",
    "watchsports.to",
    "streamed.su",
    "tvpass.org",
    "livehdtv.com",
    "zhangboheng.github.io",
    "champagne.pages.dev",
    "opensource.builders",
    "openalternative.co",
    "switching.software",
    "oss.gallery",
    "similarsites.com",
    "alternative.me",
    "siteslike.com",
    "freesiteslike.com",
    "topbestalternatives.com",
    "libreprojects.net",
    "libreselfhosted.com",
    "rivestream.org",
    "libreoffice.org",
    "ollama.com",
}

# Additional curated host rules (freemium / paid).
EXTRA_HOST = {
    "freeconvert.com": "free-tier",
    "online-video-cutter.com": "free-tier",
    "online-convert.com": "free-tier",
    "online-audio-converter.com": "free-tier",
    "onlineocr.net": "free-tier",
    "huggingface.co": "free-tier",
    "deepai.org": "free-tier",
    "researchgate.net": "free-tier",
    "citationmachine.net": "free-tier",
    "easybib.com": "free-tier",
    "bibguru.com": "free-tier",
    "quetext.com": "free-tier",
    "plagscan.com": "free-tier",
    "cymath.com": "free-tier",
    "mathgptpro.com": "free-tier",
    "kapwing.com": "free-tier",
    "flexclip.com": "free-tier",
    "videosoftdev.com": "free-tier",
    "limnu.com": "free-tier",
    "ziteboard.com": "free-tier",
    "edabit.com": "free-tier",
    "lingq.com": "free-tier",
    "clozemaster.com": "free-tier",
    "italki.com": "free-tier",
    "lingodeer.com": "free-tier",
    "typeform.com": "free-tier",
    "surveymonkey.com": "free-tier",
    "mentimeter.com": "free-tier",
    "kahoot.com": "free-tier",
    "pollfish.com": "free-tier",
    "surveycake.com": "free-tier",
    "iloveimg.com": "free-tier",
    "ilovepdf.com": "free-tier",
    "smallpdf.com": "free-tier",
    "sejda.com": "free-tier",
    "pdfescape.com": "free-tier",
    "docfly.com": "free-tier",
    "tinypng.com": "free-tier",
    "remove.bg": "free-tier",
    "befunky.com": "free-tier",
    "fotor.com": "free-tier",
    "twistedwave.com": "free-tier",
    "bandlab.com": "free-tier",
    "thatsthem.com": "free-tier",
    "spyse.com": "free-tier",
    "app.netlas.io": "free-tier",
    "netlas.io": "free-tier",
    "blockchair.com": "free-tier",
    "etherscan.io": "free-tier",
    "portswigger.net": "free-tier",
    "projecthoneypot.org": "free-tier",
    "flickr.com": "free-tier",
    "social-searcher.com": "free-tier",
    "doogal.co.uk": "free-tier",
    "forensicosint.com": "free-tier",
    "virustotal.com": "free-tier",
    "shodan.io": "free-tier",
    "censys.io": "free-tier",
    "securitytrails.com": "free-tier",
    "builtwith.com": "free-tier",
    "similarweb.com": "free-tier",
    "semrush.com": "free-tier",
    "ahrefs.com": "paid",
    "mailboxvalidator.com": "paid",
    "perfect-privacy.com": "free",
    "inteltechniques.com": "free-tier",
    "youlearn.ai": "paid",
    "tresorit.com": "paid",
    "coursehero.com": "paid",
    "studocu.com": "paid",
    "chegg.com": "paid",
    "bartleby.com": "paid",
    "pluralsight.com": "paid",
    "babbel.com": "paid",
    "1password.com": "paid",
    "squarespace.com": "paid",
    "roamresearch.com": "paid",
    "linode.com": "paid",
    "akamai.com": "paid",
    "feedbooks.com": "free-tier",
    "elevenreader.io": "free-tier",
    "elevenlabs.io": "free-tier",
    "speechify.com": "free-tier",
    "granola.ai": "free-tier",
    "mem.ai": "free-tier",
    "reflect.app": "free-tier",
    "remnote.com": "free-tier",
    "capacities.io": "free-tier",
    "apps.apple.com": "free",
    "emergent.sh": "free-tier",
    "app.emergent.sh": "free-tier",
    "icons8.com": "free-tier",
    "modelslab.com": "free-tier",
    "formspree.io": "free-tier",
    "eye2.ai": "free",
    "uncensored.chat": "limited",
    "cluely.com": "limited",
    "dyad.sh": "limited",
    "scribbr.com": "limited",
    "skillshare.com": "limited",
    "dataquest.io": "limited",
    "datacamp.com": "limited",
    "codecademy.com": "limited",
    "brilliant.org": "limited",
    "hemingwayapp.com": "limited",
    "wolframalpha.com": "limited",
    "grammarly.com": "limited",
    "quillbot.com": "limited",
}


def load_base_rules() -> dict[str, str]:
    spec = importlib.util.spec_from_file_location(
        "fix_pricing", ROOT / "scripts" / "fix_pricing.py"
    )
    fp = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fp)
    rules = dict(fp.HOST)
    rules.update(fp.EXACT)
    rules.update(EXTRA_HOST)
    if RULES_PATH.exists():
        rules.update(json.loads(RULES_PATH.read_text(encoding="utf-8")))
    return rules


def host_key(url: str) -> str:
    return urlparse(url.strip()).netloc.lower().replace("www.", "")


def path_key(url: str) -> str:
    p = urlparse(url.strip().rstrip("/"))
    h = p.netloc.lower().replace("www.", "")
    path = p.path.rstrip("/").lower()
    return f"{h}{path}"


def is_public_sector_host(host: str) -> bool:
    return (
        host.endswith(".gov")
        or host.endswith(".gov.uk")
        or host.endswith(".edu")
        or host.endswith(".ac.uk")
        or host.endswith(".mil")
        or ".gov." in host
    )


def infer_osint_pricing(name: str) -> str | None:
    """OSINT listings use suffix markers: (T) tool, (M) manual, (R) register, (R$) paid."""
    n = name.strip()
    if n.endswith("(R$)"):
        return "paid"
    if n.endswith("(R)"):
        return "free-tier"
    if n.endswith("(T)") or n.endswith("(M)") or n.endswith("(D)"):
        return "free"
    return None


def resolve_pricing(
    url: str, category: str, rules: dict[str, str], name: str = ""
) -> str | None:
    pk = path_key(url)
    if pk in rules:
        return rules[pk]

    host = host_key(url)
    if host in ALWAYS_FREE_HOSTS:
        return "free"
    if host in rules:
        return rules[host]
    if is_public_sector_host(host):
        return "free"
    if host == "github.com":
        return "free"

    parts = host.split(".")
    for i in range(len(parts) - 1):
        parent = ".".join(parts[i:])
        if parent in rules:
            return rules[parent]
        if parent in ALWAYS_FREE_HOSTS:
            return "free"

    if category in CATEGORY_DEFAULTS:
        return CATEGORY_DEFAULTS[category]

    if category.startswith("osint-"):
        inferred = infer_osint_pricing(name)
        if inferred:
            return inferred

    if host.endswith(".github.io") or host.endswith(".gitlab.io"):
        return "free"
    if host.endswith(".pages.dev") or host.endswith(".vercel.app"):
        return "free"

    return None


SECTION_RE = re.compile(
    r'<section class="tool-category"[^>]*data-category="([^"]+)"[^>]*>.*?'
    r'<div class="category-tools">(.*?)</div>\s*</section>',
    re.DOTALL,
)
LINK_RE = re.compile(
    r'(<a\s+href=")([^"]+)("[^>]*data-pricing=")([^"]+)("[^>]*>.*?'
    r'<span class="tool-link-name">[^<]+</span></a>)',
    re.DOTALL,
)
NAME_RE = re.compile(r'<span class="tool-link-name">([^<]+)</span>')


def apply_pricing(dry_run: bool = False) -> list[tuple[str, str, str, str, str]]:
    rules = load_base_rules()
    html = HTML_PATH.read_text(encoding="utf-8")
    changes: list[tuple[str, str, str, str, str]] = []

    def replace_section(match: re.Match[str]) -> str:
        category = match.group(1)
        body = match.group(2)

        def replace_link(link_match: re.Match[str]) -> str:
            prefix, url, mid, current, suffix = link_match.groups()
            name_m = NAME_RE.search(suffix)
            name = name_m.group(1).strip() if name_m else url
            expected = resolve_pricing(url, category, rules, name)
            if not expected or expected == current or expected not in VALID:
                return link_match.group(0)
            changes.append((name, category, current, expected, url))
            return f"{prefix}{url}{mid}{expected}{suffix}"

        new_body = LINK_RE.sub(replace_link, body)
        return match.group(0).replace(body, new_body, 1)

    new_html = SECTION_RE.sub(replace_section, html)

    if changes and not dry_run:
        HTML_PATH.write_text(new_html, encoding="utf-8")

    return changes


def main() -> None:
    changes = apply_pricing(dry_run=False)
    print(f"Updated {len(changes)} pricing tags")
    for name, cat, old, new, url in sorted(changes, key=lambda x: (x[3], x[0]))[:80]:
        print(f"  [{cat}] {name}: {old} -> {new}")
    if len(changes) > 80:
        print(f"  ... and {len(changes) - 80} more")


if __name__ == "__main__":
    main()
