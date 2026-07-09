"""Add tools discovered via AlternativeTo similar-sites / OSS discovery chains."""
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
HTML_PATH = ROOT / "student.html"
JS_PATH = ROOT / "js" / "student.js"

SECTION_RE = re.compile(
 r'(<section class="tool-category" data-category="([^"]+)">.*?<div class="category-tools">)(.*?)(</div>\s*</section>)',
 re.DOTALL,
)
HREF_RE = re.compile(r'href="([^"]+)"')


def norm_url(url: str) -> str:
 p = urlparse(url.strip().rstrip("/"))
 host = (p.netloc or "").lower().replace("www.", "")
 path = p.path.rstrip("/")
 return f"{host}{path}".lower()


def github_owner(url: str) -> str | None:
 p = urlparse(url)
 if p.netloc.lower().replace("www.", "") != "github.com":
 return None
 parts = [part for part in p.path.split("/") if part]
 return parts[0] if parts else None


def link(url: str, name: str, pricing: str = "free") -> str:
 owner = github_owner(url)
 domain = urlparse(url).netloc.replace("www.", "")
 if owner:
 icon = fb = f"https://github.com/{owner}.png?size=64"
 else:
 icon = f"https://www.google.com/s2/favicons?domain={domain}&amp;sz=128"
 fb = f"https://www.google.com/s2/favicons?domain={domain}&sz=128"
 safe = name.replace("&", "&amp;")
 return (
 f' <a href="{url}" target="_blank" rel="noopener noreferrer" class="tool-link" data-pricing="{pricing}">'
 f'<img src="{icon}" data-fallback="{fb}" alt="" class="tool-link-icon">'
 f'<span class="tool-link-name">{safe}</span></a>\n'
 )


ADDITIONS = {
 "free-stuff": [
 ("https://opensource.builders/", "Opensource.Builders"),
 ("https://openalternative.co/", "OpenAlternative"),
 ("https://switching.software/", "switching.software"),
 ("https://oss.gallery/", "OSS Gallery"),
 ("https://similarsites.com/", "SimilarSites"),
 ("https://alternative.me/", "alternative.me"),
 ("https://www.siteslike.com/", "Sites Like"),
 ("https://www.freesiteslike.com/", "FreeSitesLike"),
 ("https://www.topbestalternatives.com/", "Top Best Alternatives"),
 ("https://libreprojects.net/", "Libre Projects"),
 ("https://libreselfhosted.com/", "Libre Selfhosted"),
 ("https://alternativeto.net/software/top-similar-sites/", "Top Similar Sites"),
 ],
 "open-source": [
 ("https://directory.fsf.org/", "Free Software Directory"),
 ("https://prism-break.org/", "PRISM Break"),
 ("https://openhub.net/", "Open HUB"),
 ("https://github.com/awesome-selfhosted/awesome-selfhosted", "Awesome Selfhosted"),
 ("https://github.com/public-apis/public-apis", "Public APIs List"),
 ("https://github.com/codecrafters-io/build-your-own-x", "Build Your Own X"),
 ("https://roadmap.sh/", "roadmap.sh"),
 ("https://ui.shadcn.com/", "shadcn/ui"),
 ],
 "privacy-tools": [
 ("https://switching.software/", "switching.software"),
 ("https://prism-break.org/", "PRISM Break"),
 ],
 "file-sharing": [
 ("https://localsend.org/", "LocalSend"),
 ],
 "cloud-storage-sync": [
 ("https://immich.app/", "Immich"),
 ],
 "utilities": [
 ("https://rustdesk.com/", "RustDesk"),
 ],
 "devops-containers": [
 ("https://github.com/louislam/uptime-kuma", "Uptime Kuma"),
 ],
 "programming": [
 ("https://zed.dev/", "Zed Editor"),
 ("https://roadmap.sh/", "roadmap.sh"),
 ],
 "programming-ai": [
 ("https://github.com/All-Hands-AI/OpenHands", "OpenHands"),
 ("https://lobechat.com/", "LobeChat"),
 ("https://github.com/mendableai/firecrawl", "Firecrawl"),
 ("https://github.com/anomalyco/opencode", "OpenCode"),
 ],
 "ai-agents": [
 ("https://github.com/All-Hands-AI/OpenHands", "OpenHands"),
 ("https://lobechat.com/", "LobeChat"),
 ],
 "notepad": [
 ("https://affine.pro/", "AFFiNE"),
 ],
 "screen-recording": [
 ("https://cap.so/", "Cap"),
 ],
 "video": [
 ("https://opencut.app/", "OpenCut"),
 ],
 "3d-animation": [
 ("https://godotengine.org/", "Godot"),
 ],
 "automation": [
 ("https://www.home-assistant.io/", "Home Assistant"),
 ],
}

# Remove empty and dedupe within script
ADDITIONS = {k: v for k, v in ADDITIONS.items() if v}

KEYWORD_PATCHES = {
 "free-stuff": [
 "opensource builders", "openalternative", "switching software", "oss gallery",
 "similarsites", "alternative.me", "sites like", "freesiteslike",
 "libre projects", "libre selfhosted", "top similar sites", "app discovery",
 ],
 "open-source": [
 "free software directory", "prism break", "open hub", "awesome selfhosted",
 "public apis", "build your own x", "roadmap", "shadcn",
 ],
 "programming-ai": ["openhands", "lobechat", "firecrawl", "opencode"],
 "ai-agents": ["openhands", "lobechat"],
 "utilities": ["rustdesk", "remote desktop"],
 "cloud-storage-sync": ["immich", "self hosted photos"],
 "file-sharing": ["localsend", "airdrop"],
 "devops-containers": ["uptime kuma", "monitoring"],
 "video": ["opencut", "video editor"],
 "screen-recording": ["cap", "screen recorder"],
 "3d-animation": ["godot", "game engine"],
 "automation": ["home assistant", "smart home"],
 "notepad": ["affine", "notes workspace"],
 "programming": ["zed", "code editor"],
}


def patch_keywords(js_text: str) -> str:
 for cat_id, words in KEYWORD_PATCHES.items():
 pattern = rf"('{cat_id}': \[)([^\]]*)(\],)"
 match = re.search(pattern, js_text)
 if not match:
 continue
 existing = match.group(2)
 additions = [f"'{w}'" for w in words if f"'{w}'" not in existing]
 if additions:
 suffix = ", " if existing.strip() else " "
 js_text = (
 js_text[: match.start(2)]
 + existing
 + suffix
 + ", ".join(additions)
 + js_text[match.end(2) :]
 )
 return js_text


def main():
 html = HTML_PATH.read_text(encoding="utf-8")
 known = {norm_url(u) for u in HREF_RE.findall(html)}
 added = 0
 skipped = 0

 def replacer(match):
 nonlocal added, skipped
 cat = match.group(2)
 if cat not in ADDITIONS:
 return match.group(0)
 inner = match.group(3)
 new_links = []
 for item in ADDITIONS[cat]:
 url, name = item[0], item[1]
 pricing = item[2] if len(item) > 2 else "free"
 key = norm_url(url)
 if key in known:
 skipped += 1
 continue
 known.add(key)
 new_links.append(link(url, name, pricing))
 added += 1
 if not new_links:
 return match.group(0)
 inner_clean = inner.rstrip() + "\n"
 return match.group(1) + inner_clean + "".join(new_links) + " " + match.group(4)

 html = SECTION_RE.sub(replacer, html)
 HTML_PATH.write_text(html, encoding="utf-8", newline="\n")
 JS_PATH.write_text(patch_keywords(JS_PATH.read_text(encoding="utf-8")), encoding="utf-8", newline="\n")
 print(f"Added {added} tools ({skipped} duplicates skipped).")


if __name__ == "__main__":
 main()
