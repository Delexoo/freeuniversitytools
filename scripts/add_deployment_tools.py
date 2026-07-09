"""Add Deployment category with hosting, CI/CD, and platform tools."""
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
HTML_PATH = ROOT / "student.html"
JS_PATH = ROOT / "js" / "student.js"

HREF_RE = re.compile(r'href="([^"]+)"')
SECTION_INSERT_BEFORE = "devops-containers"

DEPLOYMENT_TOOLS = [
    ("https://github.com/", "GitHub", "free"),
    ("https://github.com/features/actions", "GitHub Actions", "free-tier"),
    ("https://pages.github.com/", "GitHub Pages", "free"),
    ("https://vercel.com/", "Vercel", "free-tier"),
    ("https://www.netlify.com/", "Netlify", "free-tier"),
    ("https://render.com/", "Render", "free-tier"),
    ("https://railway.app/", "Railway", "free-tier"),
    ("https://fly.io/", "Fly.io", "free-tier"),
    ("https://pages.cloudflare.com/", "Cloudflare Pages", "free"),
    ("https://workers.cloudflare.com/", "Cloudflare Workers", "free-tier"),
    ("https://www.heroku.com/", "Heroku", "free-tier"),
    ("https://www.digitalocean.com/products/app-platform", "DigitalOcean App Platform", "free-tier"),
    ("https://aws.amazon.com/amplify/", "AWS Amplify", "free-tier"),
    ("https://firebase.google.com/products/hosting", "Firebase Hosting", "free-tier"),
    ("https://cloud.google.com/run", "Google Cloud Run", "free-tier"),
    ("https://azure.microsoft.com/en-us/products/app-service/static", "Azure Static Web Apps", "free-tier"),
    ("https://supabase.com/", "Supabase", "free-tier"),
    ("https://deno.com/deploy", "Deno Deploy", "free-tier"),
    ("https://surge.sh/", "Surge", "free"),
    ("https://glitch.com/", "Glitch", "free-tier"),
    ("https://replit.com/", "Replit Deploy", "free-tier"),
    ("https://caprover.com/", "CapRover", "free"),
    ("https://dokku.com/", "Dokku", "free"),
    ("https://dokploy.com/", "Dokploy", "free"),
    ("https://easypanel.io/", "Easypanel", "free-tier"),
    ("https://github.com/coollabsio/coolify", "Coolify", "free"),
    ("https://porter.run/", "Porter", "free-tier"),
    ("https://www.koyeb.com/", "Koyeb", "free-tier"),
    ("https://northflank.com/", "Northflank", "free-tier"),
    ("https://zeabur.com/", "Zeabur", "free-tier"),
    ("https://about.gitlab.com/", "GitLab", "free-tier"),
    ("https://circleci.com/", "CircleCI", "free-tier"),
    ("https://www.jenkins.io/", "Jenkins", "free"),
    ("https://bitbucket.org/product/features/pipelines", "Bitbucket Pipelines", "free-tier"),
    ("https://www.oracle.com/cloud/free/", "Oracle Cloud Free Tier", "free-tier"),
    ("https://www.linode.com/", "Linode", "paid"),
    ("https://www.scaleway.com/", "Scaleway", "free-tier"),
    ("https://appwrite.io/", "Appwrite", "free-tier"),
    ("https://www.cloudflare.com/developer-platform/products/workers-kv/", "Cloudflare KV", "free-tier"),
]

REMOVE_FROM_WEBSITE_BUILDERS = [
    "https://pages.github.com/",
    "https://vercel.com/",
    "https://www.netlify.com/",
]

DEPLOYMENT_KEYWORDS = [
    "deployment",
    "deploy",
    "hosting",
    "vercel",
    "netlify",
    "render",
    "railway",
    "fly.io",
    "github pages",
    "github actions",
    "cloudflare pages",
    "heroku",
    "amplify",
    "firebase hosting",
    "cloud run",
    "azure static",
    "deno deploy",
    "coolify",
    "dokploy",
    "caprover",
    "ci/cd",
    "continuous integration",
]


def norm_url(url: str) -> str:
    p = urlparse(url.strip().rstrip("/"))
    host = (p.netloc or "").lower().replace("www.", "")
    path = p.path.rstrip("/")
    return f"{host}{path}".lower()


def github_owner(url: str) -> str | None:
    p = urlparse(url)
    if p.netloc.lower().replace("www.", "") != "github.com":
        return None
    parts = [part for part in p.path.split("/") if part]
    return parts[0] if parts else None


def link(url: str, name: str, pricing: str = "free") -> str:
    owner = github_owner(url)
    domain = urlparse(url).netloc.replace("www.", "")
    if owner and p.path.strip("/") not in ("", "features", "features/actions"):
        icon = fb = f"https://github.com/{owner}.png?size=64"
    else:
        icon = f"https://www.google.com/s2/favicons?domain={domain}&amp;sz=128"
        fb = f"https://www.google.com/s2/favicons?domain={domain}&sz=128"
    safe = name.replace("&", "&amp;")
    return (
        f' <a href="{url}" target="_blank" rel="noopener noreferrer" class="tool-link" data-pricing="{pricing}">'
        f'<img src="{icon}" data-fallback="{fb}" alt="" class="tool-link-icon">'
        f'<span class="tool-link-name">{safe}</span></a>\n'
    )


def build_section(known: set[str]) -> tuple[str, int]:
    links = []
    added = 0
    for url, name, pricing in DEPLOYMENT_TOOLS:
        key = norm_url(url)
        if key in known:
            continue
        known.add(key)
        links.append(link(url, name, pricing))
        added += 1

    if not links:
        return "", 0

    body = "".join(links)
    section = (
        '\n <section class="tool-category" data-category="deployment">\n'
        " <h3 class=\"category-title\">Deployment</h3>\n"
        ' <div class="category-tools">\n'
        f"{body}"
        " </div>\n"
        " </section>\n"
    )
    return section, added


def remove_links(html: str, urls: list[str]) -> str:
    remove_keys = {norm_url(u) for u in urls}
    for match in list(HREF_RE.finditer(html)):
        href = match.group(1)
        if norm_url(href) not in remove_keys:
            continue
        start = html.rfind("<a ", 0, match.start())
        end = html.find("</a>", match.end())
        if start == -1 or end == -1:
            continue
        end += len("</a>")
        if html[start:end].count('class="tool-link"') == 1:
            html = html[:start] + html[end:]
    return html


def insert_section(html: str, section: str) -> str:
    marker = f'data-category="{SECTION_INSERT_BEFORE}"'
    idx = html.find(marker)
    if idx == -1:
        raise SystemExit(f"Could not find section {SECTION_INSERT_BEFORE}")
    section_start = html.rfind("<section", 0, idx)
    return html[:section_start] + section + html[section_start:]


def patch_keywords(js_text: str) -> str:
    if '"deployment"' in js_text or "'deployment'" in js_text:
        return js_text

    block = "  deployment: [\n    " + ",\n    ".join(f'"{w}"' for w in DEPLOYMENT_KEYWORDS) + ",\n  ],\n"
    needle = '  "devops-containers": ['
    if needle not in js_text:
        raise SystemExit("Could not find devops-containers in student.js")
    return js_text.replace(needle, block + needle, 1)


def main():
    html = HTML_PATH.read_text(encoding="utf-8")
    html = remove_links(html, REMOVE_FROM_WEBSITE_BUILDERS)

    known = {norm_url(u) for u in HREF_RE.findall(html)}

    if 'data-category="deployment"' not in html:
        section, added = build_section(known)
        if section:
            html = insert_section(html, section)
            print(f"Created Deployment category with {added} tools")
        else:
            print("Deployment category already complete")
    else:
        print("Deployment category already exists")

    HTML_PATH.write_text(html, encoding="utf-8", newline="\n")

    js_text = JS_PATH.read_text(encoding="utf-8")
    JS_PATH.write_text(patch_keywords(js_text), encoding="utf-8", newline="\n")
    print("Updated CATEGORY_KEYWORDS for deployment")


if __name__ == "__main__":
    main()
