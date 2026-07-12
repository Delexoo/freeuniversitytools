"""Remove tool listings whose display name is only an em dash or dash-like placeholder."""
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
HTML_PATH = ROOT / "student.html"

LINK_RE = re.compile(
    r'\s*<a\s+href="[^"]+"[^>]*class="tool-link"[^>]*>.*?</a>',
    re.DOTALL | re.IGNORECASE,
)
NAME_RE = re.compile(r'<span class="tool-link-name">([^<]*)</span>', re.DOTALL)

BAD_NAMES = {
    "\u2014",  # em dash
    "\u2013",  # en dash
    "\u2012",  # figure dash
    "\u2015",  # horizontal bar
    "\u2212",  # minus sign
    "-",
    "–",
    "—",
    "",
}


def is_bad_name(raw: str) -> bool:
    from html import unescape

    name = unescape(raw).strip()
    if name in BAD_NAMES:
        return True
    if not name:
        return True
    # only dash / whitespace characters
    stripped = name.replace(" ", "").replace("\t", "")
    if stripped and all(c in BAD_NAMES or c.isspace() for c in name):
        return True
    return False


def main() -> None:
    html = HTML_PATH.read_text(encoding="utf-8")
    removed = 0
    removed_urls: list[str] = []

    def drop_link(match: re.Match[str]) -> str:
        nonlocal removed
        block = match.group(0)
        name_m = NAME_RE.search(block)
        if not name_m or not is_bad_name(name_m.group(1)):
            return block
        href_m = re.search(r'href="([^"]+)"', block)
        if href_m:
            removed_urls.append(href_m.group(1))
        removed += 1
        return ""

    new_html = LINK_RE.sub(drop_link, html)
    if removed:
        # collapse extra blank lines inside category-tools
        new_html = re.sub(r"\n{3,}", "\n\n", new_html)
        HTML_PATH.write_text(new_html, encoding="utf-8", newline="\n")
        print(f"Removed {removed} dash-named tools from {HTML_PATH.name}")
        for url in removed_urls[:20]:
            print(f"  - {url}")
        if len(removed_urls) > 20:
            print(f"  ... and {len(removed_urls) - 20} more")
    else:
        print("No dash-named tools found in student.html")


if __name__ == "__main__":
    main()
