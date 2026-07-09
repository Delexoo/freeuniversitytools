"""Import OSINT Framework links from arf.json into student.html."""
import json
import re
import unicodedata
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
ARF_PATH = Path(r"c:\Users\Massi\Downloads\arf.json")
HTML_PATH = ROOT / "student.html"
JS_PATH = ROOT / "js" / "student.js"

PRICING_MAP = {
 "free": "free",
 "freemium": "free-tier",
 "paid": "paid",
 "limited": "limited",
 "free/freemium": "free-tier",
 "unknown": "free",
 "?": "free",
}


BEGINNER_TITLES_BY_SOURCE = {
 "Username": "Username Search",
 "Email Address": "Email Search",
 "Domain Name": "Domain Search",
 "Cloud Infrastructure": "Cloud Infrastructure Search",
 "IP & MAC Address": "IP Address Search",
 "Images / Videos / Docs": "Image & Video Search",
 "Social Networks": "Social Network Search",
 "Instant Messaging": "Messaging Search",
 "People Search Engines": "People Search",
 "Dating": "Dating Search",
 "Telephone Numbers": "Phone Number Search",
 "Public Records": "Public Records Search",
 "Compliance & Risk Intelligence": "Compliance & Risk Search",
 "Business Records": "Business Records Search",
 "Transportation": "Vehicle & Transport Search",
 "Geolocation Tools / Maps": "Maps & Location Search",
 "Search Engines": "Search Engines",
 "Online Communities": "Forum & Community Search",
 "Archives": "Web Archives",
 "Language Translation": "Translation Tools",
 "Mobile OSINT": "Mobile Search Tools",
 "Dark Web": "Dark Web Search",
 "Disinformation & Media Verification": "Fact-Check & Media Tools",
 "Blockchain & Cryptocurrency": "Crypto Search",
 "Classifieds": "Classifieds Search",
 "Encoding / Decoding": "Encoding & Decoding Tools",
 "Tools": "Research Toolkit",
 "AI Tools": "AI Research Tools",
 "Malicious File Analysis": "Malware & File Analysis",
 "Cyber Threat Intelligence": "Threat Intelligence",
 "OpSec": "Privacy & Safety Tools",
 "Documentation / Evidence Capture": "Evidence Collection",
 "Training": "Research Training",
}


def beginner_title(source_name: str) -> str:
 return BEGINNER_TITLES_BY_SOURCE.get(source_name, source_name)


def slugify(value: str) -> str:
 value = unicodedata.normalize("NFKD", value)
 value = value.encode("ascii", "ignore").decode("ascii")
 value = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
 return value or "misc"


def norm_url(url: str) -> str:
 p = urlparse(url.strip().rstrip("/"))
 host = (p.netloc or "").lower().replace("www.", "")
 path = p.path.rstrip("/")
 return f"{host}{path}".lower()


def map_pricing(raw: str | None) -> str:
 return PRICING_MAP.get((raw or "free").strip().lower(), "free")


def github_owner(url: str) -> str | None:
 p = urlparse(url)
 if p.netloc.lower().replace("www.", "") != "github.com":
 return None
 parts = [part for part in p.path.split("/") if part]
 return parts[0] if parts else None


def link_html(url: str, name: str, pricing: str = "free") -> str:
 owner = github_owner(url)
 domain = urlparse(url).netloc.replace("www.", "")
 if owner:
 icon = fb = f"https://github.com/{owner}.png?size=64"
 else:
 icon = f"https://www.google.com/s2/favicons?domain={domain}&amp;sz=128"
 fb = f"https://www.google.com/s2/favicons?domain={domain}&sz=128"
 safe_name = (
 name.replace("&", "&amp;")
 .replace("<", "&lt;")
 .replace(">", "&gt;")
 .replace('"', "&quot;")
 )
 return (
 f' <a href="{url}" target="_blank" rel="noopener noreferrer" class="tool-link" data-pricing="{pricing}">'
 f'<img src="{icon}" data-fallback="{fb}" alt="" class="tool-link-icon">'
 f'<span class="tool-link-name">{safe_name}</span></a>\n'
 )


def section_html(cat_id: str, title: str, tools: list[tuple[str, str, str]]) -> str:
 lines = [
 f' <section class="tool-category" data-category="{cat_id}">',
 f" <h3 class=\"category-title\">{title}</h3>",
 ' <div class="category-tools">',
 ]
 for url, name, pricing in tools:
 lines.append(link_html(url, name, pricing).rstrip("\n"))
 lines.extend([" </div>", " </section>", ""])
 return "\n".join(lines)


def walk_urls(node, path=None):
 path = path or []
 if node.get("type") == "url" and node.get("url"):
 yield path, node
 for child in node.get("children", []):
 yield from walk_urls(child, path + [node.get("name", "")])


def collect_categories(data):
 categories = {}
 for top in data.get("children", []):
 top_name = top.get("name", "Misc")
 cat_id = f"osint-{slugify(top_name)}"
 tools = []
 seen = set()
 for path, node in walk_urls(top, [data.get("name", "OSINT Framework"), top_name]):
 if node.get("deprecated"):
 continue
 url = node.get("url", "").strip()
 if not url or not url.startswith("http"):
 continue
 key = norm_url(url)
 if key in seen:
 continue
 seen.add(key)
 tools.append((url, node.get("name", "Untitled"), map_pricing(node.get("pricing"))))
 if tools:
 categories[cat_id] = (beginner_title(top_name), tools)
 return categories


def existing_urls(html: str) -> set[str]:
 return {norm_url(url) for url in re.findall(r'href="(https?://[^"]+)"', html)}


def update_category_keywords(js_text: str, categories: dict[str, tuple[str, list]]) -> str:
 marker = "const CATEGORY_KEYWORDS = {"
 start = js_text.find(marker)
 if start == -1:
 raise RuntimeError("Could not find CATEGORY_KEYWORDS in student.js")
 end = js_text.find("};", start)
 if end == -1:
 raise RuntimeError("Could not find end of CATEGORY_KEYWORDS")

 block = js_text[start : end + 2]
 additions = []
 for cat_id, (title, tools) in categories.items():
 if f"'{cat_id}':" in block or f'"{cat_id}":' in block:
 continue
 names = [name for _, name, _ in tools[:12]]
 keywords = ["osint", slugify(title.replace("OSINT: ", ""))]
 keywords.extend(slugify(name).replace("-", " ") for name in names[:6])
 keyword_list = ", ".join(f"'{kw}'" for kw in dict.fromkeys(k for k in keywords if k))
 additions.append(f" '{cat_id}': [{keyword_list}],")

 if not additions:
 return js_text

 insert_at = end
 new_block = block[: insert_at - start] + "\n" + "\n".join(additions) + block[insert_at - start :]
 return js_text[:start] + new_block + js_text[end + 2 :]


def main():
 data = json.loads(ARF_PATH.read_text(encoding="utf-8"))
 categories = collect_categories(data)
 html = HTML_PATH.read_text(encoding="utf-8")
 known = existing_urls(html)

 sections = []
 stats = {"categories": 0, "added": 0, "skipped_dupes": 0}
 for cat_id, (title, tools) in categories.items():
 fresh = []
 for url, name, pricing in tools:
 if norm_url(url) in known:
 stats["skipped_dupes"] += 1
 continue
 fresh.append((url, name, pricing))
 known.add(norm_url(url))
 if not fresh:
 continue
 sections.append(section_html(cat_id, title, fresh))
 stats["categories"] += 1
 stats["added"] += len(fresh)

 if not sections:
 print("No new links to add.")
 return

 marker = " </div>\n </main>"
 if marker not in html:
 raise RuntimeError("Could not find tools-directory closing marker in student.html")

 html = html.replace(marker, "\n".join(sections) + marker, 1)
 HTML_PATH.write_text(html, encoding="utf-8", newline="\n")

 js_text = JS_PATH.read_text(encoding="utf-8")
 filtered = {cid: (title, tools) for cid, (title, tools) in categories.items() if cid in {s.split('"')[3] for s in sections}}
 # Rebuild filtered from sections we actually added
 added_ids = []
 for section in sections:
 match = re.search(r'data-category="([^"]+)"', section)
 if match:
 added_ids.append(match.group(1))
 filtered = {cid: categories[cid] for cid in added_ids}
 JS_PATH.write_text(update_category_keywords(js_text, filtered), encoding="utf-8", newline="\n")

 print(
 f"Added {stats['added']} links across {stats['categories']} OSINT categories "
 f"({stats['skipped_dupes']} duplicates skipped)."
 )


if __name__ == "__main__":
 main()
