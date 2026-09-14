"""Correct pricing tags for well-known tools based on public free/paid models."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HTML_PATH = ROOT / "data" / "student-directory.html"

# domain fragment (lower) -> pricing tag
# Research notes (2026): public free/paid models for common student tools.
PRICING = {
    # Fully free / open source / no signup
    "excalidraw.com": "free",
    "app.diagrams.net": "free",
    "draw.io": "free",
    "hoppscotch.io": "free",
    "regexr.com": "free",
    "regex101.com": "free",
    "jspaint.app": "free",
    "photopea.com": "free",
    "photopea.com/": "free",
    "cyberchef.org": "free",
    "gchq.github.io": "free",
    "privacy.sexy": "free",
    "it-tools.tech": "free",
    "pairdrop.net": "free",
    "webllm": "free",
    "vscode.dev": "free",
    "stackedit.io": "free",
    "dillinger.io": "free",
    "marktext": "free",
    "tinypng.com": "free",
    "remove.bg": "free-tier",
    # Free tier / freemium
    "notion.so": "free-tier",
    "canva.com": "free-tier",
    "figma.com": "free-tier",
    "chatgpt.com": "free-tier",
    "chat.openai.com": "free-tier",
    "claude.ai": "free-tier",
    "gemini.google.com": "free-tier",
    "perplexity.ai": "free-tier",
    "grammarly.com": "limited",
    "quillbot.com": "limited",
    "elevenlabs.io": "free-tier",
    "gamma.app": "free-tier",
    "linkedin.com": "free-tier",
    "airtable.com": "free-tier",
    "miro.com": "free-tier",
    "slack.com": "free-tier",
    "zoom.us": "free-tier",
    "dropbox.com": "free-tier",
    "protonvpn.com": "free-tier",
    "windscribe.com": "free-tier",
    "bitwarden.com": "free-tier",
    "1password.com": "paid",
    "mullvad.net": "paid",
    "github.com/features/copilot": "paid",
    "openai.com/chatgpt/pricing": "paid",
    "adobe.com": "paid",
    "microsoft.com/microsoft-365": "free-tier",
    "office.com": "free-tier",
    "desmos.com": "free",
    "geogebra.org": "free",
    "khanacademy.org": "free",
    "zotero.org": "free",
    "obsidian.md": "free-tier",
    "overleaf.com": "free-tier",
    "replit.com": "free-tier",
    "vercel.com": "free-tier",
    "netlify.com": "free-tier",
    "cloudflare.com": "free-tier",
    "supabase.com": "free-tier",
    "spotify.com": "free-tier",
    "youtube.com": "free",
    "wikipedia.org": "free",
    "archive.org": "free",
}


def main() -> None:
    html = HTML_PATH.read_text(encoding="utf-8")
    changed = 0

    def replacer(match: re.Match) -> str:
        nonlocal changed
        before = match.group(0)
        href = match.group(1)
        pricing = match.group(2)
        href_l = href.lower()
        new_p = None
        for needle, tag in PRICING.items():
            if needle in href_l:
                new_p = tag
                break
        if not new_p or new_p == pricing:
            return before
        changed += 1
        return before.replace(f'data-pricing="{pricing}"', f'data-pricing="{new_p}"', 1)

    # Match tool links with pricing near href
    pattern = re.compile(
        r'<a\s+href="(https?://[^"]+)"([^>]*)data-pricing="([^"]+)"',
        re.IGNORECASE,
    )

    def replacer2(m: re.Match) -> str:
        nonlocal changed
        href, mid, pricing = m.group(1), m.group(2), m.group(3)
        href_l = href.lower()
        new_p = None
        for needle, tag in sorted(PRICING.items(), key=lambda x: -len(x[0])):
            if needle in href_l:
                new_p = tag
                break
        if not new_p or new_p == pricing:
            return m.group(0)
        changed += 1
        return f'<a href="{href}"{mid}data-pricing="{new_p}"'

    html2, n = pattern.subn(replacer2, html)
    HTML_PATH.write_text(html2, encoding="utf-8")
    print(f"Updated pricing on {changed} tool links")


if __name__ == "__main__":
    main()
