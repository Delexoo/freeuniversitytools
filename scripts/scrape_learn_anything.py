"""Scrape Learn Anything map data for open-source GitHub tools."""
import json
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "scripts" / "learn_anything_os_tools.json"

URLS = {
    "maps": "https://raw.githubusercontent.com/linsa-io/2017-release/master/maps/maps-bak.json",
    "nodes": "https://raw.githubusercontent.com/linsa-io/2017-release/master/maps/nodes-bak.json",
    "resources": "https://raw.githubusercontent.com/linsa-io/2017-release/master/maps/resources-bak.json",
}

GITHUB_RE = re.compile(r"https?://github\.com/[^/\s\"']+/[^/\s\"'#?]+", re.I)

CURATED_TOOL_LISTS = [
    "learn-anything/alfred-workflows",
    "learn-anything/chrome-extensions",
    "learn-anything/command-line-tools",
    "learn-anything/firefox-extensions",
    "learn-anything/programming-languages",
    "learn-anything/safari-extensions",
    "learn-anything/macos-apps",
    "learn-anything/ios-apps",
]


def load_jsonl(url: str) -> list[dict]:
    items = []
    with urllib.request.urlopen(url, timeout=180) as resp:
        for line in resp:
            items.append(json.loads(line))
    return items


def fetch_text(url: str) -> str | None:
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            return resp.read().decode("utf-8", errors="ignore")
    except Exception:
        return None


def github_links(text: str) -> list[str]:
    return [g.rstrip("/") for g in GITHUB_RE.findall(text)]


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    print("Loading Learn Anything map data...")
    maps = load_jsonl(URLS["maps"])
    nodes = load_jsonl(URLS["nodes"])
    resources = load_jsonl(URLS["resources"])

    res_by_map: dict[int, list[dict]] = {}
    for resource in resources:
        res_by_map.setdefault(resource["mapID"], []).append(resource)

    os_maps = []
    os_map_ids: set[int] = set()
    for m in maps:
        blob = f"{m.get('title', '')} {m.get('key', '')}".lower()
        if "open source" in blob or "open-source" in blob:
            os_maps.append(m)
            os_map_ids.add(m["mapID"])

    os_github: dict[str, dict] = {}
    for mid in os_map_ids:
        for res in res_by_map.get(mid, []):
            url = res.get("url", "")
            for g in github_links(url):
                key = g.lower()
                os_github.setdefault(
                    key,
                    {
                        "url": g,
                        "title": res.get("text", ""),
                        "category": res.get("category", ""),
                        "map_id": mid,
                    },
                )

    tool_cats = {
        "tool",
        "tools",
        "library",
        "framework",
        "package",
        "software",
        "app",
        "application",
        "cli",
        "extension",
        "plugin",
    }
    tool_github: dict[str, dict] = {}
    for res in resources:
        cat = (res.get("category") or "").lower()
        url = res.get("url", "")
        if "github.com" not in url.lower():
            continue
        if cat not in tool_cats and "tool" not in cat:
            continue
        for g in github_links(url):
            key = g.lower()
            tool_github.setdefault(
                key,
                {
                    "url": g,
                    "title": res.get("text", ""),
                    "category": cat,
                    "map_id": res.get("mapID"),
                },
            )

    curated_github: dict[str, dict] = {}
    for repo in CURATED_TOOL_LISTS:
        text = fetch_text(f"https://raw.githubusercontent.com/{repo}/master/readme.md")
        if text is None:
            text = fetch_text(f"https://raw.githubusercontent.com/{repo}/main/readme.md")
        if not text:
            continue
        for g in github_links(text):
            key = g.lower()
            curated_github.setdefault(key, {"url": g, "from_list": repo})

    payload = {
        "open_source_maps": [
            {
                "map_id": m["mapID"],
                "key": m.get("key", ""),
                "title": m.get("title", ""),
            }
            for m in sorted(os_maps, key=lambda x: x.get("key", ""))
        ],
        "open_source_github_from_maps": sorted(
            os_github.values(), key=lambda x: x["url"].lower()
        ),
        "tool_category_github_from_maps": sorted(
            tool_github.values(), key=lambda x: x["url"].lower()
        ),
        "curated_list_github": sorted(
            curated_github.values(), key=lambda x: x["url"].lower()
        ),
        "stats": {
            "open_source_maps": len(os_maps),
            "open_source_github_repos": len(os_github),
            "tool_category_github_repos": len(tool_github),
            "curated_list_github_repos": len(curated_github),
        },
    }

    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload["stats"], indent=2))
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
