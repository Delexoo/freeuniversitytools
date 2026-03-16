#!/usr/bin/env python3
"""
Download tool/service logos and save as PNG in the doc/ folder.
Uses Clearbit Logo API first, then Google Favicon as fallback.
Converts to PNG when needed (requires Pillow for non-PNG sources).
"""
import os
import re
import sys
import urllib.request
from urllib.parse import urlparse

# (domain for logo fetch, output filename without extension)
LOGO_MAP = [
    ("annas-archive.se", "AnnasArchive"),
    ("oceanofpdf.com", "OceanOfPDF"),
    ("openstax.org", "OpenStax"),
    ("libgen.ac", "Libgen"),
    ("tubitv.com", "Tubi"),
    ("pluto.tv", "PlutoTV"),
    ("fmhy.net", "FMHY"),
    ("deepwebnest.com", "Deepwebnest"),
    ("alternativeto.net", "AlternativeTo"),
    ("uncensored.ai", "UncensoredAI"),
    ("magichour.ai", "MagicHour"),
    ("toolfk.com", "ToolFK"),
    ("passwordgenerator.net", "PasswordGenerator"),
    ("x.ai", "Grok"),
    ("deepai.org", "DeepAI"),
    ("google.com", "AiStudio"),  # AiStudio is Google
    ("microsoft.com", "MicrosoftToDo"),
    ("todoist.com", "Todoist"),
    ("elevenlabs.io", "ElevenLabs"),
    ("mathbot.com", "MathBot"),
    ("symbolab.com", "Symbolab"),
    ("chemguide.co.uk", "ChemGuide"),
    ("edx.org", "EdX"),
    ("downloadgram.org", "DownloadGram"),
    ("bassbooster.io", "BassBooster"),
    ("musicviz.app", "MusicViz"),
    ("random.org", "RandomOrg"),
    ("tec-it.com", "BarcodeGenerator"),
    ("tinyurl.com", "TinyURL"),
    ("fixanything.io", "FixAnything"),
    ("quickref.me", "QuickRef"),
    ("minecraft.net", "Minecraft"),
    ("poki.com", "Poki"),
    ("coolmathgames.com", "CoolmathGames"),
    ("createm.xyz", "CreateM"),
    ("grammarly.com", "Grammarly"),
    ("watermarkremover.io", "WatermarkRemover"),
    ("tinypng.com", "TinyPNG"),
    ("yt1s.com", "YT1s"),
    ("kapwing.com", "Kapwing"),
    ("loader.to", "LoaderTo"),
    ("pdf.io", "PDFio"),
    ("online-audio-converter.com", "OnlineAudioConverter"),
    ("cloudconvert.com", "CloudConvert"),
    ("handbrake.fr", "HandBrake"),
    ("gimp.org", "GIMP"),
    ("wolframalpha.com", "WolframAlpha"),
    ("remotasks.com", "RemoTasks"),
    ("neevo.ai", "Neevo"),
    ("hivemicro.com", "HiveMicro"),
    ("rws.com", "Rws"),
    ("clickworker.com", "ClickWorker"),
    ("pareto.io", "Pareto"),
    ("appen.com", "Appen"),
    ("kizi.com", "Kizi"),
    ("fancypantsadventures.com", "Fancypants"),
    ("squarespace.com", "Soap2Day"),  # used for Soap2Day / VIP Stream
    ("coolmathgames.com", "RedBall4"),  # Red Ball 4
    ("poki.com", "TempleRun"),  # Temple Run (same Poki for Subway Surfers)
]

# Optional: override domain for Clearbit (some need parent domain)
DOMAIN_OVERRIDE = {
    "aistudio.google.com": "google.com",
    "todo.microsoft.com": "microsoft.com",
}

DOC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "doc")
FAVICON_SIZE = 128


def get_domain_from_url(url):
    """Extract clean domain from URL for Clearbit."""
    try:
        parsed = urlparse(url if url.startswith("http") else "https://" + url)
        host = parsed.netloc or url
        return host.lower().split(":")[0]
    except Exception:
        return url


def fetch_url(url, timeout=10):
    """Fetch URL and return (bytes, content_type) or (None, None)."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; LogoDownloader/1.0)"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read(), resp.headers.get("Content-Type", "")
    except Exception as e:
        print(f"  Fetch error: {e}", file=sys.stderr)
        return None, None


def save_png(data, content_type, out_path):
    """Save image data as PNG. Converts with Pillow if available."""
    if not data or len(data) < 100:
        return False
    try:
        if "png" in (content_type or "").lower():
            with open(out_path, "wb") as f:
                f.write(data)
            return True
        try:
            from PIL import Image
            import io
            img = Image.open(io.BytesIO(data))
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGBA")
            else:
                img = img.convert("RGB")
            img.save(out_path, "PNG")
            return True
        except ImportError:
            if "jpeg" in (content_type or "").lower() or "jpg" in (content_type or "").lower():
                print("  Install Pillow (pip install Pillow) to convert JPEG to PNG", file=sys.stderr)
            with open(out_path, "wb") as f:
                f.write(data)
            return True
    except Exception as e:
        print(f"  Save error: {e}", file=sys.stderr)
        return False


def download_logo(domain, filename):
    """Try Clearbit then Google favicon; save as doc/filename.png."""
    out_path = os.path.join(DOC_DIR, f"{filename}.png")
    if os.path.isfile(out_path):
        print(f"  Skip (exists): {filename}.png")
        return True

    # Clearbit (company logos, high quality)
    url_clearbit = f"https://logo.clearbit.com/{domain}"
    data, ct = fetch_url(url_clearbit)
    if data and save_png(data, ct, out_path):
        print(f"  OK Clearbit: {filename}.png")
        return True

    # Google favicon fallback
    url_favicon = f"https://www.google.com/s2/favicons?domain={domain}&sz={FAVICON_SIZE}"
    data, ct = fetch_url(url_favicon)
    if data and save_png(data, ct or "image/png", out_path):
        print(f"  OK Favicon: {filename}.png")
        return True

    print(f"  FAIL: {filename}.png (tried Clearbit + Favicon for {domain})", file=sys.stderr)
    return False


def main():
    os.makedirs(DOC_DIR, exist_ok=True)
    print(f"Saving logos to: {DOC_DIR}\n")
    ok = 0
    for domain, filename in LOGO_MAP:
        print(f"{filename} ({domain}):")
        if download_logo(domain, filename):
            ok += 1
    print(f"\nDone: {ok}/{len(LOGO_MAP)} logos saved to doc/")
    return 0 if ok == len(LOGO_MAP) else 1


if __name__ == "__main__":
    sys.exit(main())
