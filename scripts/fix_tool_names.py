"""Fix cryptic tool names (Microsoft Store IDs, locale stubs, path junk) in student.html."""
from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parent.parent
HTML_PATH = ROOT / "data" / "student-directory.html"

MS_STORE_NAMES = {
    "9mspc6mp8fm4": "Microsoft Whiteboard",
    "9nblggh33n0n": "WiFi Analyzer",
    "9pdzvj34ztxg": "FlairMax",
    "9p08t4jltqnk": "Aquile Reader",
    "9nblggh6c4bc": "Grover Podcast",
}

URL_NAME_OVERRIDES = {
    "creativecommons.org/publicdomain/zero/1.0": "CC0 Public Domain",
    "pi.ai": "Pi AI",
    "fmhy.net/ai": "FMHY AI",
    "tempr.email": "Tempr Email",
    "mail.awsl.uk": "AWSL Temp Mail",
    "cs.email": "CS Email",
    "muellmail.com": "Muellmail",
    "linshi-email.com": "Linshi Email",
    "sign-aip.net": "Sign AIP",
    "ji.taioan.org": "Ji Taioan",
    "oh.taigi.info": "Oh Taigi",
    "cn.chinadaily.com.cn": "China Daily",
    "saicord.com/hi": "Saicord Hindi",
    "oss.gallery/projects/ai": "OSS Gallery AI",
    "d.lib.msu.edu": "MSU Digital Library",
    "3d.si.edu": "Smithsonian 3D",
    "cs50.harvard.edu/x": "CS50x",
    "10minemail.com": "10 Minute Email",
    "48hr.email": "48 Hour Email",
    "33mail.com": "33 Mail",
    "911realtime.org": "911 Realtime",
    "90daykorean.com": "90 Day Korean",
}

LOCALE_STUBS = {
    "en", "cs", "hi", "cn", "ji", "oh", "ai", "pi", "fr", "de", "es", "pt",
    "ru", "ja", "ko", "zh", "ar", "it", "nl", "pl", "tr", "uk", "vi", "id", "th",
}

LINK_RE = re.compile(
    r'(<a\s+href="([^"]+)"[^>]*class="tool-link"[^>]*>)'
    r'(<img[^>]*>)'
    r'(<span class="tool-link-name">)([^<]*)(</span></a>)',
    re.IGNORECASE | re.DOTALL,
)


def title_from_slug(slug: str) -> str:
    slug = unquote(slug).strip("/").replace("_", "-")
    parts = [p for p in re.split(r"[-_+.]+", slug) if p]
    if not parts:
        return slug
    small = {"ai", "pdf", "vpn", "api", "css", "osint", "rss", "cms", "gis", "ide"}
    out = []
    for p in parts:
        if p.lower() in small:
            out.append(p.upper())
        elif p.isdigit():
            out.append(p)
        else:
            out.append(p[:1].upper() + p[1:])
    return " ".join(out)


def looks_like_store_id(name: str) -> bool:
    n = name.strip()
    if not re.fullmatch(r"9[A-Za-z0-9]{11}", n, re.I):
        return False
    return bool(re.search(r"\d", n)) and bool(re.search(r"[A-Za-z]", n))


def looks_like_hash(name: str) -> bool:
    n = name.strip().replace(" ", "")
    if re.fullmatch(r"[0-9a-fA-F-]{20,}", n):
        return True
    if re.fullmatch(r"[0-9A-Fa-f]{8,}", n) and len(n) >= 12:
        return True
    return False


def looks_like_version(name: str) -> bool:
    return bool(re.fullmatch(r"\d+(\.\d+)+", name.strip()))


def needs_rename(name: str) -> bool:
    n = (name or "").strip()
    if not n:
        return True
    if looks_like_store_id(n):
        return True
    if looks_like_hash(n):
        return True
    if looks_like_version(n):
        return True
    if n.lower() in LOCALE_STUBS:
        return True
    if len(n) <= 2:
        return True
    if n == "Microsoft Store App":
        return True
    if re.fullmatch(
        r"[0-9A-Fa-f]{8}(\s+[0-9A-Fa-f]{4}){3}\s+[0-9A-Fa-f]{12}",
        n.replace("-", " "),
    ):
        return True
    return False


def ms_product_id(url: str) -> str | None:
    host = urlparse(url).netloc.lower()
    if "apps.microsoft.com" not in host and "microsoft.com" not in host:
        return None
    if (
        "apps.microsoft.com" not in host
        and "/store/" not in url.lower()
        and "productid" not in url.lower()
    ):
        return None
    m = re.search(r"(?:productId/|detail/)([9][A-Za-z0-9]{10,})", url, re.I)
    if m:
        return m.group(1).lower()
    return None


def slug_from_ms_detail(url: str) -> str | None:
    m = re.search(r"/store/detail/([^/]+)/[9]", url, re.I)
    return m.group(1) if m else None


def domain_label(host: str) -> str:
    host = host.lower().replace("www.", "")
    parts = host.split(".")
    if len(parts) >= 3 and parts[0] in LOCALE_STUBS:
        host = ".".join(parts[1:])
        parts = host.split(".")

    # compound TLDs: example.com.vn / example.co.uk
    if len(parts) >= 3 and parts[-2] in {"com", "co", "net", "org", "gov", "ac"}:
        base = parts[-3]
    elif len(parts) >= 2:
        base = parts[-2]
    else:
        base = parts[0]

    # Prefer brand subdomain when it is not a locale stub: tv.nrk.no → Nrk still OK,
    # but go.aftvnews.com → Aftvnews is fine via base
    return title_from_slug(base)


def humanize_from_url(url: str) -> str:
    try:
        p = urlparse(url)
    except Exception:
        return ""
    host = (p.netloc or "").lower().replace("www.", "")
    path = unquote(p.path or "").strip("/")
    parts = [x for x in path.split("/") if x and x.lower() not in LOCALE_STUBS]

    if "github.com" in host and parts:
        if parts[0] == "topics" and len(parts) > 1:
            return title_from_slug(parts[1])
        if parts[0] == "gist" or host.startswith("gist."):
            # gist.github.com/user/hash → user
            if host.startswith("gist.") and parts:
                return title_from_slug(parts[0])
            if len(parts) >= 2:
                return title_from_slug(parts[1] if parts[0] == "gist" else parts[0])
        if len(parts) >= 2:
            repo = parts[1]
            if repo.endswith(".git"):
                repo = repo[:-4]
            if looks_like_hash(repo) or repo.isdigit() or parts[1] in {"commit", "issues"}:
                # commit URL: owner/repo/commit/hash
                if len(parts) >= 3 and parts[2] == "commit":
                    return title_from_slug(parts[1])
                return title_from_slug(parts[0])
            return title_from_slug(repo)
        return title_from_slug(parts[0])

    if "greasyfork.org" in host and parts:
        for i, part in enumerate(parts):
            if part == "scripts" and i + 1 < len(parts):
                script = parts[i + 1]
                m = re.match(r"\d+-(.+)", script)
                if m:
                    return title_from_slug(m.group(1))
                return f"Greasy Fork {script}"

    if parts:
        last = parts[-1]
        if (
            not looks_like_hash(last)
            and not looks_like_version(last)
            and not looks_like_store_id(last)
            and last.lower() not in LOCALE_STUBS
            and not last.isdigit()
        ):
            return title_from_slug(last)

    return domain_label(host)


def resolve_name(url: str, current: str) -> str:
    url_l = url.lower()
    for needle, nice in URL_NAME_OVERRIDES.items():
        if needle in url_l:
            return nice

    pid = ms_product_id(url)
    if pid and pid in MS_STORE_NAMES:
        return MS_STORE_NAMES[pid]

    slug = slug_from_ms_detail(url)
    if slug and (looks_like_store_id(current) or needs_rename(current)):
        return title_from_slug(slug)

    if pid and (looks_like_store_id(current) or needs_rename(current)):
        return "Microsoft Store App"

    if needs_rename(current):
        return humanize_from_url(url) or current

    return current


def better_icon(url: str, img_tag: str) -> str:
    try:
        host = urlparse(url).netloc.lower().replace("www.", "")
    except Exception:
        return img_tag

    if "raw.githubusercontent.com" in img_tag and "/doc/" in img_tag:
        return img_tag

    if "apps.microsoft.com" in host or (
        "microsoft.com" in host and "/store/" in url.lower()
    ):
        icon = "https://icon.horse/icon/microsoft.com"
        return f'<img src="{icon}" data-fallback="{icon}" alt="" class="tool-link-icon">'

    if "github.com" in host:
        m = re.search(r"github\.com/([^/\"'?]+)", url, re.I)
        if m and m.group(1).lower() not in {"topics", "gist"}:
            owner = m.group(1)
            icon = f"https://github.com/{owner}.png?size=64"
            return f'<img src="{icon}" data-fallback="{icon}" alt="" class="tool-link-icon">'

    # Prefer site favicon when still on a generic placeholder
    if "FreeUniversityTools.png" in img_tag and host:
        icon = f"https://icon.horse/icon/{host}"
        return f'<img src="{icon}" data-fallback="{icon}" alt="" class="tool-link-icon">'

    return img_tag


def main() -> None:
    html = HTML_PATH.read_text(encoding="utf-8")
    changed = 0
    samples: list[tuple[str, str, str]] = []

    def repl(m: re.Match) -> str:
        nonlocal changed
        open_a, href, img, span_open, name, span_close = m.groups()
        new_name = resolve_name(href, name)
        new_img = better_icon(href, img)
        if new_name != name or new_img != img:
            changed += 1
            if len(samples) < 25 and new_name != name:
                samples.append((name, new_name, href))
            return f"{open_a}{new_img}{span_open}{new_name}{span_close}"
        return m.group(0)

    html2 = LINK_RE.sub(repl, html)
    HTML_PATH.write_text(html2, encoding="utf-8")
    print(f"Updated {changed} tool links")
    for old, new, href in samples:
        print(f"  {old!r} -> {new!r}")
        print(f"    {href}")


if __name__ == "__main__":
    main()
