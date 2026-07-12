"""Split combined 'X and Y' tool categories into separate dedicated categories."""
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
HTML_PATH = ROOT / "student.html"

SECTION_RE = re.compile(
    r'(<section class="tool-category"[^>]*data-category="([^"]+)"[^>]*>)'
    r'.*?<h3 class="category-title">([^<]*)</h3>.*?'
    r'(<div class="category-tools">)(.*?)(</div>\s*</section>)',
    re.DOTALL,
)
LINK_RE = re.compile(
    r'(<a\s+href="[^"]+"[^>]*>.*?<span class="tool-link-name">[^<]*</span></a>)',
    re.DOTALL,
)
LINK_URL_RE = re.compile(r'href="([^"]+)"')

# slug -> list of (target_slug, target_title, url_substrings_for_this_bucket)
# Tools match first bucket whose substring list matches; unmatched tools go to first bucket.
SPLITS: dict[str, list[tuple[str, str, list[str]]]] = {
    "writing": [
        ("writing", "Writing", ["justdone.com", "scribbr.com", "hemingwayapp.com", "writersdigest.com"]),
        ("citations", "Citations", ["bibme.org", "citethisforme.com", "refworks.com", "zotero.org", "mendeley.com"]),
    ],
    "converters": [
        ("compressors", "Compressors", ["handbrake.fr"]),
        ("converters", "Converters", ["zamzar.com", "onlineconverter.com", "cloudconvert.com"]),
    ],
    "vpn-security": [
        ("vpn", "VPN", ["protonvpn.com", "windscribe.com", "mullvad.net"]),
        (
            "security",
            "Security",
            [
                "deepwebnest.com",
                "haveibeenpwned.com",
                "monitor.mozilla.org",
                "adguard-dns.io",
                "cloudflare.com/learning",
                "torproject.org",
            ],
        ),
    ],
    "resume-career": [
        (
            "resume",
            "Resume",
            ["flowcv.com", "novoresume.com", "enhancv.com", "resume.io", "zety.com", "resumegenius.com"],
        ),
        ("career", "Career", ["linkedin.com", "monster.com"]),
    ],
    "spreadsheets": [
        (
            "spreadsheets",
            "Spreadsheets",
            [
                "docs.google.com/spreadsheets",
                "libreoffice.org/discover/calc",
                "airtable.com",
                "cryptpad.fr/sheet",
                "zoho.com/sheet",
                "rowzero.io",
                "onlyoffice.com",
                "baserow.io",
                "microsoft-365/excel",
            ],
        ),
        ("data-tools", "Data Tools", ["wolframalpha.com"]),
    ],
    "math-science": [
        ("math-tools", "Math Tools", ["geogebra.org", "mathsisfun.com", "desmos.com", "wolframalpha.com"]),
        ("science-tools", "Science Tools", ["phet.colorado.edu", "khanacademy.org"]),
    ],
    "ebooks-textbooks": [
        (
            "ebooks",
            "E-Books",
            ["wikibooks.org", "bookboon.com"],
        ),
        (
            "textbooks",
            "Textbooks",
            ["libretexts.org", "open.umn.edu", "saylor.org/books", "oercommons.org", "openstax.org"],
        ),
    ],
    "music-podcasts": [
        (
            "music",
            "Music",
            [
                "shailen.dedyn.io/racoon",
                "azmp3.cc",
                "ezmp3.lat",
                "cobalt.tools",
                "lucida.to",
                "doubledouble.top",
                "ncs.io",
                "downloadmusicschool.com",
                "Music-Megathread",
                "open.spotify.com",
                "music.youtube.com",
                "soundcloud.com",
                "bandcamp.com",
            ],
        ),
        (
            "podcasts",
            "Podcasts",
            ["podcasters.spotify.com", "anchor.fm", "podcasts.google.com"],
        ),
    ],
    "3d-animation": [
        (
            "3d",
            "3D",
            ["blender.org", "tinkercad.com", "freecad.org", "spline.design", "sketchup.com", "mixamo.com", "godotengine.org"],
        ),
        ("animation", "Animation", ["opentoonz.org", "kdenlive.org", "animaker.com"]),
    ],
    "api-testing": [
        (
            "api-clients",
            "API Clients",
            ["postman.com", "hoppscotch.io", "insomnia.rest", "reqbin.com", "usebruno.com"],
        ),
        ("api-platforms", "API Platforms", ["editor.swagger.io", "rapidapi.com"]),
    ],
    "finance-budgeting": [
        ("budgeting", "Budgeting", ["splitwise.com", "goodbudget.com", "ynab.com"]),
        (
            "finance",
            "Finance",
            ["waveapps.com", "creditkarma.com", "mint.intuit.com", "mint.com", "personalcapital.com"],
        ),
    ],
    "health-wellness": [
        ("wellness", "Wellness", ["insighttimer.com", "headspace.com", "calm.com", "noom.com"]),
        ("health-fitness", "Health & Fitness", ["myfitnesspal.com", "strava.com", "nike.com/ntc-app"]),
    ],
    "scheduling": [
        ("calendars", "Calendars", ["calendar.google.com", "cal.com", "calendly.com", "doodle.com"]),
        ("scheduling", "Scheduling", ["when2meet.com", "worldtimebuddy.com", "time.is"]),
    ],
    "fonts-typography": [
        (
            "fonts",
            "Fonts",
            ["fonts.google.com", "dafont.com", "fontsquirrel.com", "fontshare.com", "fontesk.com", "fontspace.com"],
        ),
        ("typography", "Typography", ["fontjoy.com", "typewolf.com"]),
    ],
    "stock-media": [
        ("stock-photos", "Stock Photos", ["unsplash.com", "pexels.com", "pixabay.com"]),
        (
            "stock-video-audio",
            "Stock Video & Audio",
            ["coverr.co", "mixkit.co", "videvo.net", "videezy.com", "freesound.org", "storyblocks.com"],
        ),
    ],
    "ai-voice": [
        (
            "ai-voice",
            "AI Voice",
            ["elevenlabs.io", "ttsmaker.com", "play.ht", "murf.ai", "lovo.ai", "openai/whisper"],
        ),
        ("ai-audio", "AI Audio", ["suno.com", "udio.com", "podcast.adobe.com/enhance"]),
    ],
    "data-science": [
        ("notebooks", "Notebooks", ["colab.research.google.com", "jupyter.org", "deepnote.com"]),
        (
            "data-science",
            "Data Science",
            ["kaggle.com", "public.tableau.com", "databricks.com", "streamlit.io"],
        ),
    ],
    "diagramming": [
        ("flowcharts", "Flowcharts", ["mermaid.live"]),
        (
            "diagrams",
            "Diagrams",
            ["eraser.io", "lucidchart.com", "processon.com", "gliffy.com", "smartdraw.com", "diagrams.net"],
        ),
    ],
    "focus-productivity": [
        (
            "focus",
            "Focus",
            ["pomofocus.io", "forestapp.cc", "flocus.com", "noisli.com", "asoftmurmur.com", "marinaratimer.com"],
        ),
        ("time-tracking", "Time Tracking", ["toggl.com", "flow.app"]),
    ],
    "ai-study-tools": [
        (
            "ai-study",
            "AI Study",
            ["notebooklm.google.com", "quizgecko.com", "studyfetch.com", "revisely.com", "perplexity.ai"],
        ),
        ("ai-homework", "AI Homework", ["socratic.org", "brainly.com", "gradescope.com"]),
    ],
    "cheat-sheets": [
        (
            "cheat-sheets",
            "Cheat Sheets",
            ["quickref.me", "overapi.com", "cheatography.com", "cheat-sheets.org", "devhints.io"],
        ),
        ("dev-docs", "Dev Docs", ["devdocs.io"]),
    ],
    "regex-devtools": [
        (
            "regex",
            "Regex",
            ["regex101.com", "regexr.com", "debuggex.com", "extendsclass.com/regex"],
        ),
        ("dev-tools", "Dev Tools", ["crontab.guru", "jsonformatter.org"]),
    ],
    "latex-docs": [
        (
            "latex",
            "LaTeX",
            ["overleaf.com", "papeeria.com", "latexbase.com", "latex-project.org", "latex-tutorial.com"],
        ),
        ("math-docs", "Math Docs", ["tablesgenerator.com"]),
    ],
    "bookmarks-rss": [
        ("bookmarks", "Bookmarks", ["getpocket.com", "raindrop.io", "instapaper.com"]),
        ("rss", "RSS", ["feedly.com", "inoreader.com", "theoldreader.com"]),
    ],
    "art-drawing": [
        ("drawing", "Drawing", ["aggie.io", "kleki.com", "sketch.io", "pixilart.com"]),
        ("digital-art", "Digital Art", ["autodraw.com", "sumopaint.com"]),
    ],
    "scholarships": [
        (
            "scholarships",
            "Scholarships",
            ["fastweb.com", "scholarships.com", "cappex.com", "unigo.com", "scholarshipowl.com"],
        ),
        ("financial-aid", "Financial Aid", ["bigfuture.collegeboard.org"]),
    ],
    "geography-history": [
        ("geography", "Geography", ["seterra.com", "geoguessr.com", "ourworldindata.org"]),
        ("history", "History", ["loc.gov", "britannica.com", "ducksters.com"]),
    ],
    "icons-illustrations": [
        ("icons", "Icons", ["icons8.com", "flaticon.com", "iconscout.com", "svgrepo.com"]),
        ("illustrations", "Illustrations", ["undraw.co", "humaaans.com"]),
    ],
    "mockups-templates": [
        ("mockups", "Mockups", ["mockupworld.co", "mockuphone.com", "smartmockups.com", "placeit.net"]),
        ("templates", "Templates", ["freepik.com", "pixeden.com"]),
    ],
    "git-version-control": [
        ("git-hosting", "Git Hosting", ["gitlab.com", "gitea.io"]),
        ("git-tools", "Git Tools", ["gitkraken.com", "sourcetreeapp.com", "ohshitgit.com"]),
    ],
    "cloud-storage-sync": [
        ("cloud-sync", "Cloud Sync", ["immich.app"]),
        ("backup", "Backup", ["idrive.com", "duplicati.com", "backblaze.com"]),
    ],
    "exam-test-prep": [
        ("exam-prep", "Exam Prep", ["collegeboard.org", "khanacademy.org/sat"]),
        (
            "test-prep",
            "Test Prep",
            ["magoosh.com", "240tutoring.com", "testprepreview.com", "khanacademy.org"],
        ),
    ],
    "logo-branding": [
        ("logo-makers", "Logo Makers", ["logo-maker", "logomakr.com", "looka.com", "favicon.io"]),
        ("branding", "Branding", ["brandcrowd.com"]),
    ],
    "css-web-dev": [
        (
            "css",
            "CSS",
            ["cssgrid-generator", "flexbox.help", "caniuse.com", "animejs.com", "motion.dev"],
        ),
        ("web-dev", "Web Dev", ["w3schools.com", "developer.mozilla.org"]),
    ],
    "devops-containers": [
        (
            "containers",
            "Containers",
            ["play-with-docker", "docker.com/play-with-docker", "portainer.io"],
        ),
        (
            "devops",
            "DevOps",
            ["kodekloud.com", "github.com/coollabsio/coolify", "github.com/louislam/uptime-kuma"],
        ),
    ],
    "encode-hash-tools": [
        ("encode", "Encode Tools", ["jwt.io", "base64encode.org", "urlencoder.org"]),
        ("hash-tools", "Hash Tools", ["md5hashgenerator.com", "uuidgenerator.net"]),
    ],
    "placeholder-design": [
        ("lorem-ipsum", "Lorem Ipsum", ["lipsum.com"]),
        ("placeholders", "Placeholders", ["placeholder.com", "picsum.photos", "placehold.co", "dummyimage.com"]),
    ],
    "hackathons-events": [
        ("hackathons", "Hackathons", ["devpost.com", "mlh.io"]),
        ("events", "Events", ["eventbrite.com", "meetup.com", "lu.ma"]),
    ],
    "maps-gis": [
        (
            "maps",
            "Maps",
            ["openstreetmap.org", "google.com/earth", "openrailwaymap.org", "openaerialmap.org"],
        ),
        ("gis", "GIS", ["qgis.org"]),
    ],
    "speed-network": [
        ("speed-test", "Speed Test", ["fast.com", "speedtest.net", "speed.cloudflare.com"]),
        ("network-tools", "Network Tools", ["whatsmydns.net", "dnschecker.org"]),
    ],
    "cms-blogging": [
        ("cms", "CMS", ["ghost.org", "gohugo.io", "jekyllrb.com"]),
        ("blogging", "Blogging", ["medium.com", "substack.com"]),
    ],
    "ai-agents": [
        ("ai-agents", "AI Agents", ["github.com/crewAIInc/crewAI"]),
        (
            "ai-flows",
            "AI Flows",
            ["langflow.org", "flowiseai.com", "github.com/FlowiseAI/Flowise", "dify.ai"],
        ),
    ],
    "gradient-css": [
        ("gradients", "Gradients", ["cssgradient.io", "uigradients.com", "webgradients.com"]),
        ("css-generators", "CSS Generators", ["neumorphism.io", "glassmorphism.com"]),
    ],
    "diff-format-tools": [
        ("diff-tools", "Diff Tools", ["diffchecker.com"]),
        (
            "format-tools",
            "Format Tools",
            ["codebeautify.org", "prettier.io", "jsonlint.com", "jsonformatter.curiousconcept.com"],
        ),
    ],
}

# URLs to relocate into an existing category during any split.
MERGE_TARGETS = {"security", "privacy-tools"}

RELOCATE = {
    "deepwebnest.com": "privacy-tools",
}


def norm_url(url: str) -> str:
    p = urlparse(url.strip().rstrip("/"))
    return f"{(p.netloc or '').lower().replace('www.', '')}{p.path.rstrip('/').lower()}"


def url_matches(url: str, patterns: list[str]) -> bool:
    u = norm_url(url)
    return any(p.lower().replace("www.", "") in u for p in patterns)


def assign_tool(url: str, buckets: list[tuple[str, str, list[str]]]) -> tuple[str, str]:
    for slug, title, patterns in buckets:
        if url_matches(url, patterns):
            return slug, title
    return buckets[0][0], buckets[0][1]


def section_block(slug: str, title: str, links: list[str]) -> str:
    body = "".join(links)
    return (
        f' <section class="tool-category" data-category="{slug}">\n'
        f' <h3 class="category-title">{title}</h3>\n'
        f' <div class="category-tools">\n'
        f"{body}"
        f" </div>\n"
        f" </section>\n"
    )


def merge_links(existing: str, new_links: list[str]) -> str:
    seen = {norm_url(m.group(1)) for m in LINK_URL_RE.finditer(existing)}
    out = existing
    for link_html in new_links:
        m = LINK_URL_RE.search(link_html)
        if not m:
            continue
        key = norm_url(m.group(1))
        if key in seen:
            continue
        seen.add(key)
        out += link_html + "\n"
    return out


def find_section(html: str, slug: str) -> re.Match[str] | None:
    pattern = re.compile(
        r'(<section class="tool-category"[^>]*data-category="'
        + re.escape(slug)
        + r'"[^>]*>)'
        r'.*?<h3 class="category-title">([^<]*)</h3>.*?'
        r'(<div class="category-tools">)(.*?)(</div>\s*</section>)',
        re.DOTALL,
    )
    return pattern.search(html)


def merge_into(html: str, slug: str, bucket_links: list[str]) -> str:
    ex = find_section(html, slug)
    if not ex:
        return html
    merged = merge_links(ex.group(4), bucket_links)
    return html[: ex.start(4)] + merged + html[ex.end(4) :]


def main() -> None:
    html = HTML_PATH.read_text(encoding="utf-8")
    changes = 0

    for old_slug, buckets in SPLITS.items():
        m = find_section(html, old_slug)
        if not m:
            print(f"SKIP (not found): {old_slug}")
            continue

        if " and " not in m.group(2).lower():
            print(f"SKIP (already split): {old_slug}")
            continue

        links = LINK_RE.findall(m.group(4))
        grouped: dict[str, list[str]] = {}
        bucket_titles = {slug: title for slug, title, _ in buckets}
        for link_html in links:
            url_m = LINK_URL_RE.search(link_html)
            if not url_m:
                continue
            url = url_m.group(1)
            slug, _ = assign_tool(url, buckets)
            for fragment, target in RELOCATE.items():
                if fragment in norm_url(url):
                    slug = target
                    break
            grouped.setdefault(slug, []).append(link_html)

        # Merge tools into existing categories that are not the section being split.
        for slug, bucket_links in list(grouped.items()):
            if slug not in MERGE_TARGETS:
                continue
            other = find_section(html, slug)
            if other and other.start() != m.start():
                html = merge_into(html, slug, bucket_links)
                del grouped[slug]
                changes += 1
                print(f"MERGE {len(bucket_links)} tools into '{slug}' from '{old_slug}'")
                m = find_section(html, old_slug)
                if not m:
                    break

        if not m:
            continue

        replacement_parts: list[str] = []
        for slug, title, _ in buckets:
            bucket_links = grouped.get(slug, [])
            if bucket_links and slug not in MERGE_TARGETS:
                replacement_parts.append(section_block(slug, title, bucket_links))

        new_section = "".join(replacement_parts)
        html = html[: m.start()] + new_section + html[m.end() :]
        changes += 1
        print(f"SPLIT '{old_slug}' -> {[b[0] for b in buckets if grouped.get(b[0])]}")

    if changes:
        HTML_PATH.write_text(html, encoding="utf-8")
        print(f"\nDone. Applied {changes} category splits to {HTML_PATH}")
    else:
        print("No changes made.")


if __name__ == "__main__":
    main()
