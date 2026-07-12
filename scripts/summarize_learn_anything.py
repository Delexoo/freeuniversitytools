"""Print a summary of Learn Anything open-source tool inventory."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "scripts" / "learn_anything_os_tools.json"

CURATED_LISTS = {
    "learn-anything/alfred-workflows": "Alfred workflows",
    "learn-anything/chrome-extensions": "Chrome extensions",
    "learn-anything/command-line-tools": "Command-line tools",
    "learn-anything/firefox-extensions": "Firefox extensions",
    "learn-anything/programming-languages": "Programming languages",
    "learn-anything/safari-extensions": "Safari extensions",
    "learn-anything/macos-apps": "macOS apps",
    "learn-anything/ios-apps": "iOS apps",
}


def main() -> None:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    by_list: dict[str, int] = {}
    for item in data["curated_list_github"]:
        repo = item.get("from_list", "unknown")
        by_list[repo] = by_list.get(repo, 0) + 1

    print("Learn Anything open-source inventory")
    print("=" * 40)
    print(f"Open-source learning maps: {data['stats']['open_source_maps']}")
    for m in data["open_source_maps"]:
        print(f"  - {m['key']} (map {m['map_id']})")
    print()
    print("OSS list repos referenced in maps:")
    for item in data["open_source_github_from_maps"]:
        print(f"  - {item['title']}: {item['url']}")
    print()
    print("Curated tool lists (GitHub repos linked):")
    for repo, label in CURATED_LISTS.items():
        count = by_list.get(repo, 0)
        print(f"  - {label}: {count}")
    print()
    print(f"Total GitHub links across curated lists: {data['stats']['curated_list_github_repos']}")


if __name__ == "__main__":
    main()
