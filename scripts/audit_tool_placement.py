"""Audit and fix misplaced tools across categories."""
import re
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
HTML_PATH = ROOT / "student.html"

SECTION_RE = re.compile(
 r'(<section class="tool-category"[^>]*data-category="([^"]+)">.*?<div class="category-tools">)(.*?)(</div>\s*</section>)',
 re.DOTALL,
)
LINK_RE = re.compile(
 r'(<a\s+href="([^"]+)"[^>]*data-pricing="([^"]+)"[^>]*>.*?<span class="tool-link-name">([^<]+)</span></a>)',
 re.DOTALL,
)


def norm_url(url):
 p = urlparse(url.strip().rstrip("/"))
 host = (p.netloc or "").lower().replace("www.", "")
 path = p.path.rstrip("/").lower()
 return f"{host}{path}"


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


# domain/path fragment -> correct category (first match wins)
CORRECT_CATEGORY = {
 # databases
 "supabase.com": "databases",
 "neon.tech": "databases",
 "dbdiagram.io": "databases",
 "sqliteonline.com": "databases",
 "drawsql.app": "databases",
 "planetscale.com": "databases",
 "turso.tech": "databases",
 "mongodb.com": "databases",
 # api testing
 "postman.com": "api-testing",
 "hoppscotch.io": "api-testing",
 "insomnia.rest": "api-testing",
 "reqbin.com": "api-testing",
 "editor.swagger.io": "api-testing",
 "usebruno.com": "api-testing",
 "rapidapi.com": "api-testing",
 "mockoon.com": "api-mocking",
 "beeceptor.com": "api-mocking",
 "webhook.site": "api-mocking",
 "httpbin.org": "api-mocking",
 "jsonplaceholder.typicode.com": "api-mocking",
 # security / passwords
 "keepassxc.org": "security",
 "keepass.info": "security",
 "passwords.google.com": "security",
 "bitwarden.com": "security",
 # converters / all-in-one
 "tools.pdf24.org": "all-in-one-tools",
 "pdf24.org": "all-in-one-tools",
 "convertio.co": "all-in-one-tools",
 "onlinetools.com": "all-in-one-tools",
 "products.aspose.app": "all-in-one-tools",
 "tinywow.com": "all-in-one-tools",
 # creator tools
 "canva.com": "design",
 "capcut.com": "creator-tools",
 "invideo.io": "creator-tools",
 # generative ai
 "bing.com/images/create": "generative-ai",
 "ideogram.ai": "generative-ai",
 "playground.com": "generative-ai",
 "leonardo.ai": "generative-ai",
 # study
 "goblin.tools": "study",
 "brainscape.com": "study",
 "cram.com": "study",
 "sophia.org": "study",
 # programming
 "replit.com": "programming",
 "leetcode.com": "programming",
 "exercism.org": "programming",
 "codewars.com": "programming",
 "scratch.mit.edu": "programming",
 "freecodecamp.org": "programming",
 "theodinproject.com": "programming",
 # email
 "mail.google.com": "email",
 "proton.me/mail": "email",
 "web3forms.com": "email",
 "getform.io": "email",
 "formspree.io": "email",
 # free-stuff / discovery
 "alternativeto.net": "free-stuff",
 "producthunt.com": "free-stuff",
 "fmhy.net/internet-tools": "free-stuff",
 "fmhy.net/system-tools": "free-stuff",
 # music
 "open.spotify.com": "music-podcasts",
 "music.youtube.com": "music-podcasts",
 "soundcloud.com": "music-podcasts",
 "bandcamp.com": "music-podcasts",
 # math-science
 "desmos.com": "math-science",
 "geogebra.org": "math-science",
 "phet.colorado.edu": "math-science",
 "wolframalpha.com": "math-science",
 # website builders
 "pages.github.com": "website-builders",
 "vercel.com": "website-builders",
 "netlify.com": "website-builders",
 "carrd.co": "website-builders",
 "wordpress.com": "website-builders",
 # stock media
 "unsplash.com": "stock-media",
 "pexels.com": "stock-media",
 "pixabay.com": "stock-media",
 "coverr.co": "stock-media",
 "mixkit.co": "stock-media",
 "videvo.net": "stock-media",
 "videezy.com": "stock-media",
 "freesound.org": "stock-media",
 # fonts
 "fonts.google.com": "fonts-typography",
 "dafont.com": "fonts-typography",
 "fontsquirrel.com": "fonts-typography",
 "fontshare.com": "fonts-typography",
 # color tools
 "coolors.co": "color-tools",
 "colorhunt.co": "color-tools",
 "paletton.com": "color-tools",
 "color.adobe.com": "color-tools",
 # collaboration
 "slack.com": "collaboration",
 "discord.com": "collaboration",
 "zoom.us": "collaboration",
 "teams.microsoft.com": "collaboration",
 "meet.jit.si": "collaboration",
 # scheduling
 "calendar.google.com": "scheduling",
 "cal.com": "scheduling",
 "calendly.com": "scheduling",
 "when2meet.com": "scheduling",
 "doodle.com": "scheduling",
 # mind mapping
 "diagrams.net": "mind-mapping",
 "app.diagrams.net": "mind-mapping",
 "coggle.it": "mind-mapping",
 "whimsical.com": "mind-mapping",
 "mindmeister.com": "mind-mapping",
 "miro.com": "mind-mapping",
 # file sharing
 "wetransfer.com": "file-sharing",
 "pixeldrain.com": "file-sharing",
 "send.cm": "file-sharing",
 "file.io": "file-sharing",
 # browser extensions
 "github.com/gorhill/ublock": "browser-extensions",
 "sponsor.ajay.app": "browser-extensions",
 "darkreader.org": "browser-extensions",
 "toby.io": "browser-extensions",
 "onetab.com": "browser-extensions",
 "tampermonkey.net": "browser-extensions",
 "greasemonkey.net": "browser-extensions",
 # social media
 "buffer.com": "social-media",
 "linktr.ee": "social-media",
 "later.com": "social-media",
 "metricool.com": "social-media",
 # finance
 "splitwise.com": "finance-budgeting",
 "waveapps.com": "finance-budgeting",
 "goodbudget.com": "finance-budgeting",
 "creditkarma.com": "finance-budgeting",
 # health
 "insighttimer.com": "health-wellness",
 "myfitnesspal.com": "health-wellness",
 "strava.com": "health-wellness",
 # git
 "gitlab.com": "git-version-control",
 "gitea.io": "git-version-control",
 "gitkraken.com": "git-version-control",
 "sourcetreeapp.com": "git-version-control",
 # code editors
 "codesandbox.io": "code-editors",
 "stackblitz.com": "code-editors",
 "codepen.io": "code-editors",
 "jsfiddle.net": "code-editors",
 # data science
 "colab.research.google.com": "data-science",
 "kaggle.com": "data-science",
 "jupyter.org": "data-science",
 # local ai
 "ollama.com": "local-ai",
 "lmstudio.ai": "local-ai",
 "gpt4all.io": "local-ai",
 # courses misplaced in programming category duplicates
 "coursera.org": "courses",
 "edx.org": "courses",
 "khanacademy.org": "courses",
 "udemy.com": "courses",
 # pdf tools
 "ilovepdf.com": "pdf",
 "smallpdf.com": "pdf",
 "sejda.com": "pdf",
 # image tools
 "remove.bg": "image",
 "tinypng.com": "image",
 "iloveimg.com": "image",
 # video
 "clipchamp.com": "video",
 "openshot.org": "video",
 "shotcut.org": "video",
 # vpn
 "protonvpn.com": "vpn-security",
 "windscribe.com": "vpn-security",
 # translation
 "deepl.com": "translation",
 "libretranslate.com": "translation",
 # markdown
 "dillinger.io": "markdown-tools",
 "stackedit.io": "markdown-tools",
 "hackmd.io": "markdown-tools",
 # latex
 "overleaf.com": "latex-docs",
 # regex/devtools
 "regex101.com": "regex-devtools",
 "jsonformatter.org": "regex-devtools",
 # encode/hash -> encode-hash-tools
 "jwt.io": "encode-hash-tools",
 "base64encode.org": "encode-hash-tools",
 # diff
 "diffchecker.com": "diff-format-tools",
 "prettier.io": "diff-format-tools",
 # internships
 "joinhandshake.com": "internships",
 "wayup.com": "internships",
 # scholarships
 "fastweb.com": "scholarships",
 "scholarships.com": "scholarships",
}


def correct_category(url):
 u = url.lower()
 # longest fragment match first
 for frag in sorted(CORRECT_CATEGORY.keys(), key=len, reverse=True):
 if frag in u:
 return CORRECT_CATEGORY[frag]
 return None


def parse_sections(html):
 sections = {}
 order = []
 for m in SECTION_RE.finditer(html):
 cat = m.group(2)
 order.append(cat)
 tools = []
 for lm in LINK_RE.finditer(m.group(3)):
 tools.append({
 "raw": lm.group(1),
 "url": lm.group(2),
 "pricing": lm.group(3),
 "name": lm.group(4).strip(),
 "norm": norm_url(lm.group(2)),
 })
 sections[cat] = tools
 return sections, order


def audit(html):
 sections, _ = parse_sections(html)
 issues = []
 url_locations = defaultdict(list)

 for cat, tools in sections.items():
 for t in tools:
 url_locations[t["norm"]].append((cat, t["name"]))
 correct = correct_category(t["url"])
 if correct and correct != cat:
 issues.append((t["name"], cat, correct, t["url"]))

 dupes = {k: v for k, v in url_locations.items() if len(v) > 1}
 return issues, dupes, sections


def rebuild_tool_from_dict(t):
 if t.get("raw"):
 return " " + t["raw"].strip() + "\n"
 github = None
 if "github.com/" in t["url"]:
 parts = urlparse(t["url"]).path.strip("/").split("/")
 if parts:
 github = parts[0]
 return link(t["url"], t["name"], t["pricing"], github)


def fix(html):
 sections, order = parse_sections(html)
 # collect all tools by norm url, prefer correct category
 all_tools = {}
 tool_meta = {}

 for cat, tools in sections.items():
 for t in tools:
 key = t["norm"]
 correct = correct_category(t["url"])
 if key not in all_tools:
 all_tools[key] = t
 tool_meta[key] = correct or cat
 else:
 # keep the one in correct category
 existing_correct = tool_meta[key]
 if correct == correct and correct != existing_correct:
 all_tools[key] = t
 tool_meta[key] = correct
 elif correct and not existing_correct:
 all_tools[key] = t
 tool_meta[key] = correct

 # rebuild sections: clear and redistribute
 new_sections = {cat: [] for cat in sections}
 seen_in_cat = defaultdict(set)
 moves = []

 for key, t in all_tools.items():
 correct = correct_category(t["url"])
 target = correct if correct else None

 # find current category
 current = None
 for cat, tools in sections.items():
 if any(x["norm"] == key for x in tools):
 current = cat
 break

 if target and current and target != current:
 moves.append((t["name"], current, target))

 dest = target if target else current
 if dest is None:
 continue
 if key in seen_in_cat[dest]:
 continue
 seen_in_cat[dest].add(key)
 new_sections[dest].append(t)

 # tools without mapping stay in original category only
 for cat, tools in sections.items():
 for t in tools:
 key = t["norm"]
 if correct_category(t["url"]):
 continue # already handled
 if key in seen_in_cat[cat]:
 continue
 # only add if this was its original home and not placed elsewhere
 placed = any(key in seen_in_cat[c] for c in new_sections)
 if not placed:
 seen_in_cat[cat].add(key)
 new_sections[cat].append(t)

 def replacer(m):
 cat = m.group(2)
 tools = new_sections.get(cat, [])
 inner = "".join(rebuild_tool_from_dict(t) for t in tools)
 return m.group(1) + "\n" + inner + " " + m.group(4)

 html = SECTION_RE.sub(replacer, html)
 return html, moves


def main():
 html = HTML_PATH.read_text(encoding="utf-8")
 issues, dupes, _ = audit(html)
 print(f"Misplaced tools (by rules): {len(issues)}")
 for name, wrong, right, url in sorted(issues, key=lambda x: (x[1], x[0])):
 print(f" {name}: {wrong} -> {right} ({url})")
 print(f"\nDuplicate URLs across categories: {len(dupes)}")
 for norm, locs in sorted(dupes.items(), key=lambda x: -len(x[1]))[:30]:
 print(f" {norm}: {locs}")

 html2, moves = fix(html)
 if moves:
 HTML_PATH.write_text(html2, encoding="utf-8")
 print(f"\nMoved {len(moves)} tools:")
 for name, fr, to in moves:
 print(f" {name}: {fr} -> {to}")
 else:
 print("\nNo moves needed from rule-based fix.")

 issues2, dupes2, _ = audit(html2 if moves else html)
 print(f"\nAfter fix, misplaced: {len(issues2)}, duplicates: {len(dupes2)}")


if __name__ == "__main__":
 main()
