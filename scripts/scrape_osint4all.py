"""Fetch OSINT4ALL tools via WordPress REST API + profile page domains."""
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "scripts" / "osint4all_tools.json"
API = "https://osint4all.com/wp-json/wp/v2/tool"
DOMAIN_RE = re.compile(
    r'<small>\s*([a-z0-9][a-z0-9.-]+\.[a-z]{2,})\s*</small>', re.I
)

CATEGORY_MAP = {
    "tool_category-geolocation-mapping": "osint-geolocation-tools-maps",
    "tool_category-domain-dns-intelligence": "osint-domain-name",
    "tool_category-network-attack-surface": "osint-domain-name",
    "tool_category-threat-intelligence": "osint-compliance-risk-intelligence",
    "tool_category-blockchain-crypto-osint": "osint-blockchain-cryptocurrency",
    "tool_category-archives-historical-web": "osint-archives",
    "tool_category-social-listening": "osint-social-networks",
    "tool_category-people-search": "osint-people-search-engines",
    "tool_category-email-osint": "osint-email-address",
    "tool_category-phone-osint": "osint-telephone-numbers",
    "tool_category-media-monitoring": "osint-disinformation-media-verification",
    "tool_category-public-interest-datasets": "osint-public-records",
    "tool_category-company-corporate-intelligence": "osint-business-records",
    "tool_category-transportation-mobility": "osint-transportation",
    "tool_category-images-video-documents": "osint-images-videos-docs",
    "tool_category-search-discovery": "osint-search-engines",
    "tool_category-mobile-osint": "osint-mobile-osint",
    "tool_category-dark-web": "osint-dark-web",
    "tool_category-language-translation": "osint-language-translation",
}


def fetch_json(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=90) as resp:
        return json.load(resp)


def fetch_text(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=90) as resp:
        return resp.read().decode("utf-8", "replace")


def pick_category(class_list: list[str]) -> str:
    for cls in class_list:
        if cls in CATEGORY_MAP:
            return CATEGORY_MAP[cls]
    return "osint-search-engines"


def domain_to_url(domain: str) -> str:
    domain = domain.strip().lower()
    if domain.startswith("github.com") or domain.startswith("www.github.com"):
        return f"https://{domain}"
    return f"https://{domain}"


def main() -> None:
    page = 1
    tools = []
    while True:
        url = f"{API}?per_page=100&page={page}"
        batch = fetch_json(url)
        if not batch:
            break
        for item in batch:
            name = item.get("title", {}).get("rendered", "OSINT Tool")
            profile = item.get("link", "")
            category = pick_category(item.get("class_list", []))
            try:
                html = fetch_text(profile)
            except Exception:
                continue
            m = DOMAIN_RE.search(html)
            if not m:
                continue
            ext_url = domain_to_url(m.group(1))
            tools.append(
                {
                    "name": name,
                    "url": ext_url,
                    "profile": profile,
                    "category": category,
                }
            )
            time.sleep(0.1)
        if len(batch) < 100:
            break
        page += 1

    OUT.write_text(json.dumps(tools, indent=2), encoding="utf-8")
    print(f"Wrote {len(tools)} tools to {OUT}")


if __name__ == "__main__":
    main()
