"""Add GitHub powerhouses and curated dev/AI tools from user batch."""
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
HTML_PATH = ROOT / "student.html"
JS_PATH = ROOT / "js" / "student.js"

SECTION_RE = re.compile(
    r'(<section class="tool-category" data-category="([^"]+)">.*?<div class="category-tools">)(.*?)(</div>\s*</section>)',
    re.DOTALL,
)
HREF_RE = re.compile(r'href="([^"]+)"')


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
    if owner:
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


ADDITIONS = {
    "github-powerhouses": [
        ("https://github.com/ifixai-ai/iFixAi", "iFixAI"),
        ("https://github.com/kamranahmedse/developer-roadmap", "Developer Roadmap"),
        ("https://github.com/EbookFoundation/free-programming-books", "Free Programming Books"),
        ("https://github.com/donnemartin/system-design-primer", "System Design Primer"),
        ("https://github.com/jwasham/coding-interview-university", "Coding Interview University"),
        ("https://github.com/jlevy/the-art-of-command-line", "The Art of Command Line"),
        ("https://github.com/practical-tutorials/project-based-learning", "Project-Based Learning"),
        ("https://github.com/getify/You-Dont-Know-JS", "You Don't Know JS"),
        ("https://github.com/trimstray/the-book-of-secret-knowledge", "Book of Secret Knowledge"),
        ("https://github.com/yangshun/tech-interview-handbook", "Tech Interview Handbook"),
        ("https://github.com/trekhleb/javascript-algorithms", "JavaScript Algorithms"),
        ("https://github.com/Chalarangelo/30-seconds-of-code", "30 Seconds of Code"),
        ("https://github.com/github/gitignore", "Gitignore Templates"),
        ("https://github.com/n8n-io/n8n", "n8n GitHub"),
        ("https://github.com/openclaw/openclaw", "OpenClaw"),
        ("https://github.com/mem0ai/mem0", "Mem0"),
        ("https://github.com/FoundationAgents/MetaGPT", "MetaGPT"),
        ("https://github.com/microsoft/autogen", "AutoGen"),
        ("https://github.com/Aider-AI/aider", "Aider"),
        ("https://github.com/microsoft/markitdown", "MarkItDown"),
        ("https://github.com/soxoj/maigret", "Maigret"),
        ("https://github.com/TauricResearch/TradingAgents", "TradingAgents"),
        ("https://github.com/browserbase/stagehand", "Stagehand"),
        ("https://github.com/huggingface/transformers", "Transformers"),
        ("https://github.com/vllm-project/vllm", "vLLM"),
        ("https://github.com/ggml-org/llama.cpp", "llama.cpp"),
        ("https://github.com/run-llama/llama_index", "LlamaIndex"),
        ("https://github.com/karpathy/nanochat", "nanochat"),
        ("https://github.com/infiniflow/ragflow", "RAGFlow"),
        ("https://github.com/zilliztech/claude-context", "Claude Context"),
        ("https://github.com/supermemoryai/supermemory", "Supermemory"),
        ("https://github.com/ComposioHQ/awesome-claude-skills", "Awesome Claude Skills"),
        ("https://github.com/multica-ai/andrej-karpathy-skills", "Karpathy Agent Skills"),
        ("https://github.com/perplexityai/bumblebee", "Bumblebee"),
        ("https://github.com/comfyanonymous/ComfyUI", "ComfyUI"),
        ("https://github.com/deepseek-ai/DeepSeek-V4", "DeepSeek V4"),
        ("https://github.com/lobehub/lobe-chat", "Lobe Chat"),
        ("https://github.com/freeCodeCamp/freeCodeCamp", "freeCodeCamp GitHub"),
        ("https://github.com/openai/whisper", "Whisper"),
        ("https://github.com/penpot/penpot", "Penpot GitHub"),
        ("https://github.com/calcom/cal.com", "Cal.com GitHub"),
        ("https://github.com/bitwarden/clients", "Bitwarden Clients"),
        ("https://github.com/AppFlowy-IO/AppFlowy", "AppFlowy"),
        ("https://github.com/langgenius/dify", "Dify GitHub"),
        ("https://github.com/langflow-ai/langflow", "Langflow GitHub"),
        ("https://github.com/plausible/analytics", "Plausible Analytics"),
    ],
    "video": [
        ("https://github.com/yt-dlp/yt-dlp", "yt-dlp"),
    ],
    "css-web-dev": [
        ("https://animejs.com/", "Anime.js"),
        ("https://motion.dev/", "Motion"),
    ],
    "design": [
        ("https://kokonutui.com/", "Kokonut UI"),
        ("https://bklit.com/", "Bklit UI"),
    ],
    "ai-browser": [
        ("https://manus.im/", "Manus AI"),
    ],
}

KEYWORD_PATCHES = {
    "github-powerhouses": [
        "ifixai",
        "developer roadmap",
        "free programming books",
        "system design primer",
        "coding interview university",
        "command line",
        "project based learning",
        "you dont know js",
        "secret knowledge",
        "tech interview handbook",
        "javascript algorithms",
        "30 seconds of code",
        "gitignore",
        "openclaw",
        "mem0",
        "metagpt",
        "autogen",
        "aider",
        "markitdown",
        "maigret",
        "tradingagents",
        "stagehand",
        "transformers",
        "vllm",
        "llama.cpp",
        "llamaindex",
        "nanochat",
        "ragflow",
        "claude context",
        "supermemory",
        "claude skills",
        "bumblebee",
        "comfyui",
        "deepseek v4",
        "lobe chat",
        "whisper",
        "appflowy",
        "plausible",
    ],
    "css-web-dev": ["anime.js", "motion", "animation library", "framer motion"],
    "design": ["kokonut ui", "bklit", "shadcn components", "chart components"],
    "ai-browser": ["manus ai", "manus.im"],
    "video": ["yt-dlp", "youtube download"],
}


def patch_keywords(js_text: str) -> str:
    for cat_id, words in KEYWORD_PATCHES.items():
        pattern = rf"('{cat_id}': \[)([^\]]*)(\],)"
        match = re.search(pattern, js_text)
        if not match:
            continue
        existing = match.group(2)
        additions = []
        for word in words:
            token = f"'{word}'"
            if token not in existing:
                additions.append(token)
        if additions:
            suffix = ", " if existing.strip() else " "
            js_text = (
                js_text[: match.start(2)]
                + existing
                + suffix
                + ", ".join(additions)
                + js_text[match.end(2) :]
            )
    return js_text


def main():
    html = HTML_PATH.read_text(encoding="utf-8")
    known = {norm_url(u) for u in HREF_RE.findall(html)}
    added = 0
    skipped = 0

    def replacer(match):
        nonlocal added, skipped
        cat = match.group(2)
        if cat not in ADDITIONS:
            return match.group(0)
        inner = match.group(3)
        new_links = []
        for item in ADDITIONS[cat]:
            url, name = item[0], item[1]
            pricing = item[2] if len(item) > 2 else "free"
            key = norm_url(url)
            if key in known:
                skipped += 1
                continue
            known.add(key)
            new_links.append(link(url, name, pricing))
            added += 1
        if not new_links:
            return match.group(0)
        inner_clean = inner.rstrip() + "\n"
        return match.group(1) + inner_clean + "".join(new_links) + " " + match.group(4)

    html = SECTION_RE.sub(replacer, html)
    HTML_PATH.write_text(html, encoding="utf-8", newline="\n")

    js_text = JS_PATH.read_text(encoding="utf-8")
    JS_PATH.write_text(patch_keywords(js_text), encoding="utf-8", newline="\n")
    print(f"Added {added} tools ({skipped} duplicates skipped).")


if __name__ == "__main__":
    main()
