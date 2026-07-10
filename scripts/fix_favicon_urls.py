import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = [ROOT / "student.html"]

google_pattern = re.compile(
    r"https://www\.google\.com/s2/favicons\?domain=([^&\"']+)(?:&amp;|&)?sz=128"
)

duck_pattern = re.compile(
    r"https://icons\.duckduckgo\.com/ip3/([^\"']+?)\.ico"
)


def icon_horse(domain: str) -> str:
    return f"https://icon.horse/icon/{domain}"


def repl_google(match: re.Match[str]) -> str:
    return icon_horse(match.group(1))


def repl_duck(match: re.Match[str]) -> str:
    return icon_horse(match.group(1))


for path in TARGETS:
    text = path.read_text(encoding="utf-8")
    new_text, google_count = google_pattern.subn(repl_google, text)
    new_text, duck_count = duck_pattern.subn(repl_duck, new_text)
    if google_count or duck_count:
        path.write_text(new_text, encoding="utf-8")
    print(
        f"{path.name}: replaced {google_count} Google + {duck_count} DuckDuckGo favicon URLs"
    )
