"""Fix category titles left over from combined-category splits."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HTML_PATH = ROOT / "student.html"

TITLE_FIXES = {
    "writing": "Writing",
    "converters": "Converters",
    "spreadsheets": "Spreadsheets",
    "scheduling": "Scheduling",
    "ai-voice": "AI Voice",
    "data-science": "Data Science",
    "cheat-sheets": "Cheat Sheets",
    "scholarships": "Scholarships",
    "ai-agents": "AI Agents",
}


def main() -> None:
    html = HTML_PATH.read_text(encoding="utf-8")
    changes = 0
    for slug, title in TITLE_FIXES.items():
        pattern = re.compile(
            rf'(<section class="tool-category"[^>]*data-category="{re.escape(slug)}"[^>]*>\s*'
            rf'<h3 class="category-title">)[^<]*(</h3>)',
            re.DOTALL,
        )
        new_html, n = pattern.subn(rf"\1{title}\2", html, count=1)
        if n:
            html = new_html
            changes += 1
            print(f"Fixed title for '{slug}' -> '{title}'")

    if changes:
        HTML_PATH.write_text(html, encoding="utf-8")
        print(f"Updated {changes} titles.")
    else:
        print("No title fixes needed.")


if __name__ == "__main__":
    main()
