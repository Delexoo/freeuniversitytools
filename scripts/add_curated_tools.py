"""Add free/open-source tools curated from PreMiD, Champagne Wiki, Lemmy, etc."""
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
 "browser-extensions": [
 ("https://github.com/ClearURLs/Addon", "ClearURLs"),
 ("https://privacybadger.org/", "Privacy Badger"),
 ("https://github.com/honestbleeps/Reddit-Enhancement-Suite", "Reddit Enhancement Suite"),
 ("https://github.com/jwy916/clickbait-remover-for-youtube", "Clickbait Remover"),
 ("https://github.com/FastForwardTeam/FastForward", "FastForward"),
 ("https://returnyoutubedislike.com/", "Return YouTube Dislike"),
 ("https://github.com/tom-james-watson/Old-Reddit-Redirect", "Old Reddit Redirect"),
 ("https://github.com/aranguren/buster", "Buster"),
 ("https://github.com/extesy/hoverzoom", "Hover Zoom+"),
 ("https://violentmonkey.github.io/", "Violentmonkey"),
 ("https://github.com/OhMyGuus/I-Still-Dont-Care-About-Cookies", "I Still Don't Care About Cookies"),
 ("https://github.com/jonasstrehle/Canvas-Fingerprint-Defender", "Canvas Fingerprint Defender"),
 ("https://github.com/cavi-au/Consent-O-Matic", "Consent-O-Matic"),
 ("https://github.com/underpassapp/hush", "Hush"),
 ("https://malsync.moe/", "MALSync"),
 ("https://github.com/lexesjan/typescript-aniskip-extension", "AniSkip"),
 ("https://premid.app/", "PreMiD", "free-tier"),
 ("https://github.com/PreMiD/PreMiD", "PreMiD GitHub"),
 ("https://github.com/PreMiD/Activities", "PreMiD Activities"),
 ],
 "privacy-tools": [
 ("https://librewolf.net/", "LibreWolf"),
 ("https://github.com/ungoogled-software/ungoogled-chromium", "Ungoogled Chromium"),
 ("https://rethinkdns.com/", "RethinkDNS"),
 ],
 "local-ai": [
 ("https://jan.ai/", "Jan AI"),
 ("https://github.com/LostRuins/koboldcpp", "Koboldcpp"),
 ("https://github.com/SillyTavern/SillyTavern", "SillyTavern"),
 ("https://github.com/h2oai/h2ogpt", "H2O GPT"),
 ("https://github.com/oobabooga/text-generation-webui", "Text Gen Web UI"),
 ("https://github.com/ParisNeo/lollms-webui", "Lollms WebUI"),
 ],
 "generative-ai": [
 ("https://huggingface.co/chat", "Hugging Chat"),
 ("https://github.com/lllyasviel/Fooocus", "Fooocus"),
 ("https://github.com/AUTOMATIC1111/stable-diffusion-webui", "AUTOMATIC1111"),
 ("https://github.com/invoke-ai/InvokeAI", "InvokeAI"),
 ("https://diffusionbee.com/", "DiffusionBee"),
 ("https://chainner.app/", "chaiNNer"),
 ("https://github.com/LykosAI/StabilityMatrix", "Stability Matrix"),
 ],
 "programming-ai": [
 ("https://tabby.tabbyml.com/", "Tabby"),
 ("https://continue.dev/", "Continue"),
 ],
 "tech-communities": [
 ("https://lemmy.world/", "Lemmy"),
 ("https://lemmy.world/c/opensource", "Lemmy Open Source"),
 ("https://lemmy.world/c/selfhosted", "Lemmy Selfhosted"),
 ("https://www.search-lemmy.com/", "Search Lemmy"),
 ("https://github.com/LemmyNet/lemmy", "Lemmy GitHub"),
 ],
 "free-stuff": [
 ("https://champagne.pages.dev/", "Champagne Wiki"),
 ("https://premid.app/downloads", "PreMiD Downloads"),
 ],
 "open-source": [
 ("https://lemmy.world/c/opensource", "Lemmy OSS Community"),
 ("https://github.com/PreMiD/Activities", "PreMiD Activities"),
 ],
}

KEYWORD_PATCHES = {
 "browser-extensions": [
 "clearurls", "privacy badger", "reddit enhancement", "clickbait remover",
 "fastforward", "return youtube dislike", "old reddit", "buster", "hover zoom",
 "violentmonkey", "cookies", "canvas fingerprint", "consent-o-matic", "hush",
 "malsync", "aniskip", "premid", "discord activity",
 ],
 "privacy-tools": ["librewolf", "ungoogled chromium", "rethinkdns", "private dns"],
 "local-ai": ["jan ai", "koboldcpp", "sillytavern", "h2o gpt", "text gen webui", "lollms"],
 "generative-ai": ["hugging chat", "fooocus", "automatic1111", "invokeai", "diffusionbee", "chainner", "stability matrix"],
 "programming-ai": ["tabby", "continue", "code completion"],
 "tech-communities": ["lemmy", "fediverse", "selfhosted", "search lemmy", "opensource"],
 "free-stuff": ["champagne wiki", "premid downloads"],
}


def patch_keywords(js_text: str) -> str:
 for cat_id, words in KEYWORD_PATCHES.items():
 pattern = rf"('{cat_id}': \[)([^\]]*)(\],)"
 match = re.search(pattern, js_text)
 if not match:
 continue
 existing = match.group(2)
 additions = []
 for word in words:
 token = f"'{word}'"
 if token not in existing:
 additions.append(token)
 if additions:
 suffix = ", " if existing.strip() else " "
 js_text = js_text[: match.start(2)] + existing + suffix + ", ".join(additions) + js_text[match.end(2) :]
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

 js_text = JS_PATH.read_text(encoding="utf-8")
 JS_PATH.write_text(patch_keywords(js_text), encoding="utf-8", newline="\n")
 print(f"Added {added} tools ({skipped} duplicates skipped).")


if __name__ == "__main__":
 main()
