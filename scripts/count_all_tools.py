import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).parent.parent

PAGES = [
    ("Student Tools", ROOT / "student.html"),
    ("Powerful Tools", ROOT / "doc" / "powerful.html"),
    ("Homepage featured", ROOT / "index.html"),
    ("Doc homepage featured", ROOT / "doc" / "index.html"),
]


def normalize_href(href: str) -> str:
    href = href.strip().rstrip("/")
    if href.startswith("http"):
        parsed = urlparse(href)
        return f"{parsed.netloc.lower()}{parsed.path.rstrip('/')}"
    return href.lower()


def extract_hrefs(html: str, class_name: str):
    tag_pattern = re.compile(r"<a\s+[^>]*class=\"%s\"[^>]*>" % class_name, re.IGNORECASE)
    href_pattern = re.compile(r'href="([^"]+)"', re.IGNORECASE)
    hrefs = []
    for tag_match in tag_pattern.finditer(html):
        tag = tag_match.group(0)
        href_match = href_pattern.search(tag)
        if href_match:
            hrefs.append(href_match.group(1).strip())
    return hrefs


def main():
    all_hrefs = []
    per_page = {}

    for label, path in PAGES:
        if not path.exists():
            per_page[label] = "missing"
            continue

        html = path.read_text(encoding="utf-8")
        tool_links = extract_hrefs(html, "tool-link")
        tool_cards = extract_hrefs(html, "tool-card")
        total = len(tool_links) + len(tool_cards)
        per_page[label] = {
            "tool_links": len(tool_links),
            "tool_cards": len(tool_cards),
            "total": total,
        }
        all_hrefs.extend((href, label) for href in tool_links + tool_cards)

    unique = {}
    for href, label in all_hrefs:
        key = normalize_href(href)
        unique.setdefault(key, {"href": href, "pages": set()})
        unique[key]["pages"].add(label)

    print("Per page:")
    for label, data in per_page.items():
        if data == "missing":
            print(f"  {label}: missing")
            continue
        print(
            f"  {label}: {data['total']} total "
            f"({data['tool_links']} tool-link + {data['tool_cards']} tool-card)"
        )

    print()
    print(f"Grand total listed (includes duplicates across pages): {len(all_hrefs)}")
    print(f"Unique tools by URL: {len(unique)}")
    print(f"URLs on multiple pages: {sum(1 for v in unique.values() if len(v['pages']) > 1)}")

    # Per-page unique counts and within-page duplicate listings
    for label, path in PAGES:
        if not path.exists():
            continue
        html = path.read_text(encoding="utf-8")
        hrefs = extract_hrefs(html, "tool-link") + extract_hrefs(html, "tool-card")
        if not hrefs:
            continue
        keys = [normalize_href(h) for h in hrefs]
        dup_listings = len(hrefs) - len(set(keys))
        print(
            f"{label}: {len(hrefs)} listings, {len(set(keys))} unique URLs, "
            f"{dup_listings} repeat listings in same page"
        )

    student_hrefs = extract_hrefs((ROOT / "student.html").read_text(encoding="utf-8"), "tool-link")
    powerful_hrefs = extract_hrefs((ROOT / "doc" / "powerful.html").read_text(encoding="utf-8"), "tool-link")
    student_keys = {normalize_href(h) for h in student_hrefs}
    powerful_keys = {normalize_href(h) for h in powerful_hrefs}
    print()
    print(f"Student vs Powerful overlap: {len(student_keys & powerful_keys)} shared unique URLs")
    print(f"Only on Powerful page: {len(powerful_keys - student_keys)}")
    print(f"Only on Student page: {len(student_keys - powerful_keys)}")


if __name__ == "__main__":
    main()
