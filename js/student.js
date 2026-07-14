const toolsSearch = document.getElementById("toolsSearch");
const toolsModeToggle = document.getElementById("toolsModeToggle");
const toolsDirectory = document.querySelector(".tools-directory");
const categorySections = window.FUTCategoryLoader?.sections?.length
  ? window.FUTCategoryLoader.sections
  : toolsDirectory
    ? Array.from(toolsDirectory.querySelectorAll(".tool-category"))
    : Array.from(document.querySelectorAll(".tool-category"));

function getToolLinks() {
  return toolsDirectory
    ? Array.from(toolsDirectory.querySelectorAll(".tool-link"))
    : Array.from(document.querySelectorAll(".tool-link"));
}const toggleOptions = Array.from(
  document.querySelectorAll(".tools-toggle-option"),
);
let currentMode = "free";
const CATEGORY_VISIBLE_LIMIT = 10;
const expandedCategories = new Set();

// Free mode: free | free-tier | limited. Paid mode: paid | limited | free-tier.
function matchesPricingMode(pricing, mode) {
  if (mode === "free") {
    return (
      pricing === "free" || pricing === "free-tier" || pricing === "limited"
    );
  }
  if (mode === "paid") {
    return (
      pricing === "paid" || pricing === "limited" || pricing === "free-tier"
    );
  }
  return false;
}

const CATEGORY_KEYWORDS = {
  ai: [
    "ai",
    "claude",
    "chatgpt",
    "gemini",
    "perplexity",
    "copilot",
    "grok",
    "deepai",
    "deepseek",
    "qwen",
    "cluely",
    "assistant",
  ],
  "ai-agents": [
    "ai agent",
    "crewai",
    "langflow",
    "flowise",
    "dify",
    "workflow",
    "automation",
    "llm",
    "openhands",
    "lobechat",
  ],
  accessibility: [
    "accessibility",
    "a11y",
    "wave",
    "contrast",
    "screen reader",
    "wcag",
    "color oracle",
    "axe",
  ],
  "ai-browser": [
    "browser",
    "ai",
    "manus",
    "google disco",
    "kortix",
    "arc",
    "opera",
    "brave",
    "vivaldi",
  ],
  "ai-image-editing": [
    "ai image",
    "photo edit",
    "photoroom",
    "cleanup",
    "upscale",
    "pixlr",
    "fotor",
    "background",
  ],
  "ai-notetakers": [
    "notes",
    "notion",
    "evernote",
    "note",
    "taking",
    "obsidian",
    "granola",
    "mem",
  ],
  "ai-pdf-chat": [
    "pdf chat",
    "chatpdf",
    "humata",
    "pdf ai",
    "document ai",
    "ask pdf",
    "lightpdf",
  ],
  "ai-study-tools": [
    "ai study",
    "homework",
    "notebooklm",
    "perplexity",
    "quiz",
    "flashcards",
    "studyfetch",
    "revisely",
    "socratic",
    "brainly",
  ],
  "ai-video": [
    "ai video",
    "video generator",
    "runway",
    "pika",
    "kling",
    "veed",
    "haiper",
    "text to video",
  ],
  "ai-voice": [
    "ai voice",
    "text to speech",
    "transcribe",
    "transcript",
    "speech to text",
    "elevenlabs",
    "suno",
    "udio",
    "music generator",
    "tts",
    "audio",
  ],
  "all-in-one-tools": [
    "toolfk",
    "tinywow",
    "10015",
    "all in one",
    "online tools",
    "pdf24",
    "convertio",
    "aspose",
  ],
  "api-mocking": [
    "api mock",
    "mockoon",
    "beeceptor",
    "webhook",
    "httpbin",
    "jsonplaceholder",
    "fake api",
  ],
  "api-testing": [
    "api",
    "postman",
    "hoppscotch",
    "insomnia",
    "swagger",
    "rest",
    "http",
    "reqbin",
  ],
  "browser-extensions": [
    "extension",
    "ublock",
    "adblock",
    "sponsorblock",
    "dark reader",
    "onetab",
    "toby",
    "clearurls",
    "privacy badger",
    "reddit enhancement",
    "clickbait remover",
    "fastforward",
    "return youtube dislike",
    "old reddit",
    "buster",
    "hover zoom",
    "violentmonkey",
    "cookies",
    "canvas fingerprint",
    "consent-o-matic",
    "hush",
    "malsync",
    "aniskip",
    "premid",
    "discord activity",
  ],
  analytical: [
    "analysis",
    "data",
    "claude",
    "gemini",
    "perplexity",
    "analytical",
  ],
  audio: [
    "audio",
    "mp3",
    "convert",
    "vocal",
    "music",
    "audacity",
    "remover",
    "123apps",
  ],
  "browser-games": [
    "games",
    "minecraft",
    "subway",
    "fancy",
    "temple",
    "kizi",
    "poki",
    "play",
    "crazygames",
    "cool math",
    "itch",
  ],
  "chrome-extension": [
    "chrome",
    "extension",
    "browser",
    "grammarly",
    "adblock",
    "lastpass",
    "manus",
    "redirect",
    "ublock",
    "sponsorblock",
    "dark reader",
  ],
  "art-drawing": [
    "draw",
    "art",
    "sketch",
    "kleki",
    "pixilart",
    "autodraw",
    "digital art",
    "paint",
  ],
  automation: [
    "automation",
    "ifttt",
    "zapier",
    "n8n",
    "make",
    "workflow",
    "activepieces",
    "home assistant",
    "smart home",
  ],
  "bookmarks-rss": [
    "bookmark",
    "rss",
    "feed",
    "pocket",
    "raindrop",
    "feedly",
    "inoreader",
    "instapaper",
  ],
  "cheat-sheets": [
    "cheat sheet",
    "reference",
    "devdocs",
    "quickref",
    "docs",
    "api reference",
  ],
  cloud: ["free for developers", "free cloud tier", 
    "collaborate",
    "share",
    "drive",
    "dropbox",
    "mega",
    "icloud",
    "onedrive",
    "team",
    "file sharing",
    "wetransfer",
    "box",
    "cloud",
    "storage",
    "pcloud",
    "syncthing",
    "sync",
    "tresorit",
  ],
  "cloud-storage-sync": [
    "cloud sync",
    "backup",
    "storage",
    "box",
    "mediafire",
    "idrive",
    "duplicati",
    "immich",
    "self hosted photos",
  ],
  "cms-blogging": [
    "cms",
    "blog",
    "ghost",
    "hugo",
    "jekyll",
    "medium",
    "substack",
    "static site",
  ],
  "code-editors": [
    "code editor",
    "online ide",
    "codesandbox",
    "stackblitz",
    "codepen",
    "jsfiddle",
    "vscode",
    "sandbox",
  ],
  collaboration: [
    "collaborate",
    "slack",
    "discord",
    "zoom",
    "teams",
    "jitsi",
    "meeting",
    "chat",
  ],
  "color-tools": [
    "color",
    "palette",
    "coolors",
    "contrast",
    "adobe color",
    "design",
  ],
  "css-web-dev": [
    "css",
    "web dev",
    "flexbox",
    "grid",
    "caniuse",
    "mdn",
    "w3schools",
    "html",
  ],
  cybersecurity: [
    "cybersecurity",
    "hacking",
    "security",
    "tryhackme",
    "hack the box",
    "ctf",
    "pentest",
    "cybrary",
  ],
  conversation: [
    "chat",
    "ai",
    "character",
    "talk",
    "conversation",
    "magichour",
    "hume",
    "venice",
  ],
  converters: [
    "convert",
    "compress",
    "freeconvert",
    "cloudconvert",
    "tinypng",
    "handbrake",
    "zamzar",
    "convertio",
  ],
  courses: [
    "course",
    "learn",
    "coursera",
    "edx",
    "udemy",
    "khan",
    "mit",
    "freecodecamp",
    "odin",
    "mindluster",
    "courses",
    "microsoft",
    "azure",
    "cybersecurity",
    "power bi",
    "full stack",
    "linkedin",
    "ibm",
    "skillsbuild",
    "google",
    "cert",
    "badge",
    "udacity",
    "openlearn",
    "futurelearn",
    "skillshare",
    "lynda",
    "w3schools",
    "mdn",
    "mozilla",
    "geeksforgeeks",
    "stackoverflow",
    "github",
    "python",
    "r project",
    "dataquest",
    "kaggle",
    "data science",
    "quora",
    "reddit",
    "learnprogramming",
    "pluralsight",
    "code.org",
    "cs50",
    "harvard",
    "datacamp",
    "analytics vidhya",
    "learnpython",
    "learn anything",
    "learning paths",
    "knowledge maps",
    "mind maps",
  ],
  "creator-tools": [
    "creator",
    "youtube",
    "thumbnail",
    "instagram",
    "reel",
    "transcript",
    "transcribe",
    "speakapp",
    "bass",
    "visualizer",
    "download",
    "canva",
    "capcut",
    "invideo",
  ],
  "data-science": [
    "data science",
    "notebook",
    "colab",
    "kaggle",
    "jupyter",
    "deepnote",
    "tableau",
    "analytics",
    "python",
  ],
  deployment: ["paas", "free hosting", "cicd free tier", 
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
  ],
  "devops-containers": [
    "devops",
    "docker",
    "container",
    "kubernetes",
    "portainer",
    "coolify",
    "kodekloud",
    "uptime kuma",
    "monitoring",
  ],
  "diff-format-tools": [
    "diff",
    "format",
    "prettier",
    "jsonlint",
    "codebeautify",
    "compare text",
    "json formatter",
  ],
  databases: [
    "database",
    "sql",
    "supabase",
    "neon",
    "postgres",
    "sqlite",
    "dbdiagram",
    "drawsql",
  ],
  diagramming: [
    "diagram",
    "flowchart",
    "draw.io",
    "mermaid",
    "excalidraw",
    "eraser",
    "lucidchart",
    "chart",
  ],
  design: [
    "design",
    "canva",
    "gimp",
    "figma",
    "photopea",
    "inkscape",
    "mui",
    "material",
    "21st",
    "react",
    "uiverse",
    "css",
    "components",
    "lunacy",
    "penpot",
    "krita",
    "refero",
    "react bits",
    "font tester",
    "design.md",
  ],
  email: ["transactional email free", "free smtp", 
    "email",
    "form",
    "formspree",
    "contact",
    "gmail",
    "proton",
    "web3forms",
    "getform",
  ],
  "email-marketing": [
    "email marketing",
    "newsletter",
    "mailchimp",
    "mailerlite",
    "brevo",
    "sendpulse",
    "mailjet",
  ],
  "encode-hash-tools": [
    "encode",
    "hash",
    "base64",
    "jwt",
    "uuid",
    "md5",
    "url encoder",
    "decoder",
  ],
  "exam-test-prep": [
    "exam",
    "test prep",
    "sat",
    "act",
    "gre",
    "magoosh",
    "khan",
    "college board",
    "practice test",
  ],
  english: [
    "english",
    "writing",
    "grammar",
    "quillbot",
    "claude",
    "chatgpt",
    "gemini",
    "dictionary",
    "thesaurus",
  ],
  "ebooks-textbooks": [
    "textbook",
    "ebook",
    "open textbook",
    "libretexts",
    "wikibooks",
    "saylor",
    "openstax",
    "gutenberg",
    "open library",
    "oer",
  ],
  "essay-tools": [
    "essay",
    "writing",
    "word counter",
    "citation",
    "paper",
    "grammar",
    "quillbot",
    "zotero",
    "mendeley",
    "detector",
  ],
  "free-books": [
    "books",
    "read",
    "library",
    "anna",
    "ocean",
    "openstax",
    "libgen",
    "gutenberg",
    "open library",
    "archive",
    "z-library",
    "zlib",
    "manga",
    "rivestream",
    "liber3",
    "audiobook",
    "tokybook",
    "fulllength",
  ],
  "free-movies": [
    "movies",
    "stream",
    "tubi",
    "pluto",
    "soap",
    "flix",
    "watch",
    "vip",
    "free movies",
    "bitcine",
    "lordflix",
    "xprime",
    "fmovies",
    "cinegram",
    "1337x",
    "docplus",
    "documentary",
    "primewire",
    "cineby",
    "flixer",
  ],
  "live-streaming": [
    "live",
    "stream",
    "sports",
    "tv",
    "iptv",
    "m3u8",
    "streameast",
    "sporty",
    "watch sports",
    "streamed",
    "tvpass",
    "livehdtv",
    "hdtv",
  ],
  "music-podcasts": [
    "music",
    "mp3",
    "download",
    "podcast",
    "audiobook",
    "cobalt",
    "lucida",
    "ncs",
    "bandcamp",
    "racoon",
    "megathread",
    "spotify",
    "sound",
    "soundcloud",
    "youtube music",
  ],
  "note-taking": [
    "notes",
    "note taking",
    "onenote",
    "joplin",
    "obsidian",
    "keep",
    "standard notes",
  ],
  "file-sharing": [
    "file",
    "share",
    "upload",
    "transfer",
    "send",
    "pixeldrain",
    "wetransfer",
    "localsend",
    "airdrop",
  ],
  "finance-budgeting": [
    "finance",
    "budget",
    "money",
    "splitwise",
    "wave",
    "credit",
    "expense",
  ],
  "focus-productivity": [
    "focus",
    "pomodoro",
    "timer",
    "time tracking",
    "pomofocus",
    "forest",
    "toggl",
    "productivity",
  ],
  "fonts-typography": [
    "font",
    "typography",
    "google fonts",
    "dafont",
    "typeface",
  ],
  "free-stuff": [
    "free",
    "fmhy",
    "alternativeto",
    "product hunt",
    "discovery",
    "awesome",
    "deepweb",
    "internet tools",
    "system tools",
    "champagne wiki",
    "premid downloads",
    "opensource builders",
    "openalternative",
    "switching software",
    "oss gallery",
    "similarsites",
    "alternative.me",
    "sites like",
    "freesiteslike",
    "libre projects",
    "libre selfhosted",
    "top similar sites",
    "app discovery",
    "free for dev",
    "osint4all",
  ],
  "generative-ai": [
    "generative",
    "ai",
    "magic",
    "character",
    "hume",
    "venice",
    "modelslab",
    "models",
    "image",
    "video",
    "skyreels",
    "skywork",
    "film",
    "ideogram",
    "leonardo",
    "huggingface",
    "bing image",
    "playground",
    "hugging chat",
    "fooocus",
    "automatic1111",
    "invokeai",
    "diffusionbee",
    "chainner",
    "stability matrix",
  ],
  "gif-converters": ["gif", "ezgif", "animate", "convert", "gifmaker"],
  "github-powerhouses": [
    "github",
    "open source",
    "open-webui",
    "browser-use",
    "stirling",
    "pdf",
    "godmode",
    "generative",
    "ruflo",
    "agent",
    "swarm",
    "self-host",
    "ollama",
    "skyreels",
    "skywork",
    "video",
    "film",
    "langchain",
  ],
  "grammar-writing-ai": [
    "grammar",
    "writing",
    "ai writing",
    "deepl write",
    "languagetool",
    "wordtune",
    "rytr",
    "paraphrase",
  ],
  image: [
    "image",
    "photo",
    "remove bg",
    "resize",
    "crop",
    "convert",
    "ocr",
    "watermark",
    "compress",
    "iloveimg",
    "tinywow",
    "round corner",
    "rounded corners",
    "imageonline",
  ],
  "immersive-reader": [
    "reader",
    "read",
    "text to speech",
    "eleven",
    "speechify",
    "accessibility",
    "natural",
    "aloud",
    "ttsreader",
  ],
  "health-wellness": [
    "health",
    "wellness",
    "fitness",
    "meditation",
    "workout",
    "myfitnesspal",
    "strava",
    "insight timer",
  ],
  "language-learning": [
    "language",
    "duolingo",
    "hello",
    "tandem",
    "memrise",
    "busuu",
    "lingq",
    "clozemaster",
    "italki",
  ],
  "math-science": [
    "math",
    "science",
    "desmos",
    "geogebra",
    "phet",
    "wolfram",
    "calculator",
    "graph",
  ],
  mathematics: [
    "math",
    "algebra",
    "calculus",
    "equation",
    "symbolab",
    "mathbot",
    "numbers",
    "wolfram",
    "mathos",
  ],
  "mind-mapping": [
    "mind map",
    "diagram",
    "draw.io",
    "coggle",
    "whimsical",
    "mindmeister",
    "miro",
    "brainstorm",
  ],
  "must-try": [
    "compare",
    "ai",
    "redirect",
    "vocal",
    "blocker",
    "uncensored",
    "cluely",
    "essential",
    "top",
    "freebuff",
    "emergent",
    "claude",
    "oss",
    "open source",
    "fmhy",
    "ublock",
  ],
  notepad: [
    "notepad",
    "notes",
    "notion",
    "simple",
    "text",
    "evernote",
    "simplenote",
    "onenote",
    "standard notes",
    "affine",
    "notes workspace",
  ],
  "online-poll": [
    "poll",
    "survey",
    "vote",
    "feedback",
    "forms",
    "typeform",
    "surveymonkey",
    "mentimeter",
    "kahoot",
  ],
  "geography-history": [
    "geography",
    "history",
    "seterra",
    "geoguessr",
    "maps",
    "world data",
    "britannica",
  ],
  "gradient-css": [
    "gradient",
    "css generator",
    "neumorphism",
    "glassmorphism",
    "uigradients",
    "webgradients",
  ],
  "hackathons-events": [
    "hackathon",
    "devpost",
    "mlh",
    "eventbrite",
    "meetup",
    "luma",
    "competition",
    "event",
  ],
  "git-version-control": [
    "git",
    "version control",
    "gitlab",
    "gitea",
    "gitkraken",
    "sourcetree",
    "github",
  ],
  "icons-illustrations": [
    "icons",
    "illustrations",
    "icons8",
    "flaticon",
    "undraw",
    "humaaans",
    "iconscout",
  ],
  internships: [
    "internship",
    "handshake",
    "wayup",
    "linkedin jobs",
    "chegg",
    "entry level",
    "career",
  ],
  journaling: [
    "journal",
    "diary",
    "journey",
    "penzu",
    "day one",
    "reflect",
    "daily log",
  ],
  "latex-docs": [
    "latex",
    "math",
    "overleaf",
    "papeeria",
    "document",
    "tables generator",
  ],
  "local-ai": [
    "local ai",
    "ollama",
    "lm studio",
    "gpt4all",
    "localai",
    "offline",
    "self-hosted llm",
    "jan ai",
    "koboldcpp",
    "sillytavern",
    "h2o gpt",
    "text gen webui",
    "lollms",
  ],
  "logo-branding": [
    "logo",
    "branding",
    "favicon",
    "hatchful",
    "logomakr",
    "looka",
    "brandcrowd",
  ],
  "markdown-tools": [
    "markdown",
    "md",
    "hackmd",
    "dillinger",
    "stackedit",
    "notes",
  ],
  "maps-gis": [
    "maps",
    "gis",
    "openstreetmap",
    "qgis",
    "google earth",
    "openrailwaymap",
    "aerial",
  ],
  "mockups-templates": [
    "mockup",
    "template",
    "freepik",
    "mockuphone",
    "smartmockups",
    "placeit",
  ],
  "music-production": [
    "music production",
    "daw",
    "bandlab",
    "lmms",
    "audiotool",
    "soundation",
    "beat",
  ],
  "open-source": [
    "open source",
    "foss",
    "f-droid",
    "github trending",
    "awesome",
    "osi",
    "free software directory",
    "prism break",
    "open hub",
    "awesome selfhosted",
    "public apis",
    "build your own x",
    "roadmap",
    "shadcn",
    "learn anything",
    "awesome oss apps",
    "awesome foss apps",
  ],
  "online-whiteboard": [
    "whiteboard",
    "draw",
    "board",
    "miro",
    "canva",
    "figma",
    "excalidraw",
    "diagrams",
  ],
  pdf: [
    "pdf",
    "merge",
    "split",
    "convert",
    "tinywow",
    "ilovepdf",
    "lightpdf",
    "smallpdf",
    "pdf.io",
    "stirling",
    "sejda",
    "pdf24",
  ],
  "placeholder-design": [
    "placeholder",
    "lorem ipsum",
    "dummy image",
    "picsum",
    "placehold",
    "mock text",
  ],
  productivity: [
    "notepad",
    "notes",
    "notion",
    "ticktick",
    "todo",
    "productivity",
  ],
  presentation: [
    "presentation",
    "slides",
    "powerpoint",
    "prezi",
    "slide",
    "deck",
    "gamma",
    "beautiful.ai",
  ],
  "privacy-tools": [
    "privacy",
    "anonymous",
    "duckduckgo",
    "signal",
    "cryptomator",
    "simplelogin",
    "private",
    "encrypt",
    "librewolf",
    "ungoogled chromium",
    "rethinkdns",
    "private dns",
  ],
  programming: [
    "code",
    "learn",
    "freecodecamp",
    "odin",
    "programming",
    "sololearn",
    "qwen",
    "replit",
    "leetcode",
    "exercism",
    "codewars",
    "scratch",
    "zed",
    "code editor",
  ],
  "programming-ai": [
    "code",
    "coding",
    "developer",
    "claude",
    "cursor",
    "github",
    "programming",
    "dyad",
    "aistudio",
    "copilot",
    "design arena",
    "freebuff",
    "coding agent",
    "tabby",
    "continue",
    "code completion",
    "openhands",
    "lobechat",
    "firecrawl",
    "opencode",
  ],
  "remote-jobs": [
    "remote",
    "jobs",
    "work",
    "remotasks",
    "neevo",
    "hivemicro",
    "clickworker",
    "appen",
    "pareto",
    "upwork",
    "freelancer",
    "weworkremotely",
  ],
  "resume-career": [
    "resume",
    "cv",
    "career",
    "job",
    "linkedin",
    "portfolio",
    "interview",
  ],
  research: [
    "research",
    "search",
    "perplexity",
    "claude",
    "chatgpt",
    "papers",
    "academic",
    "gemini",
    "deepseek",
    "grok",
    "copilot",
  ],
  "open-courseware": [
    "courseware",
    "course",
    "edx",
    "futurelearn",
    "yale",
    "openlearn",
    "class central",
    "learn",
    "university",
    "coursera",
    "khan",
    "codecademy",
  ],
  "regex-devtools": [
    "regex",
    "regular expression",
    "json",
    "cron",
    "debug",
    "formatter",
    "devtools",
  ],
  scholarships: [
    "scholarship",
    "financial aid",
    "fastweb",
    "college",
    "unigo",
    "cappex",
    "bigfuture",
  ],
  scheduling: [
    "schedule",
    "calendar",
    "calendly",
    "cal.com",
    "when2meet",
    "doodle",
    "meeting time",
    "world time",
  ],
  science: [
    "science",
    "chemistry",
    "chemistry guide",
    "pubchem",
    "nasa",
    "periodic table",
    "khan",
  ],
  "screen-recording": [
    "screen record",
    "recording",
    "obs",
    "sharex",
    "loom",
    "screencast",
    "cap",
    "screen recorder",
  ],
  secret: [
    "12ft",
    "paywall",
    "bypass",
    "read",
    "archive",
    "ladder",
    "outline",
    "wayback",
  ],
  security: [
    "password",
    "security",
    "generator",
    "keepass",
    "bitwarden",
    "pwned",
    "monitor",
    "adguard",
    "tor",
    "breach",
  ],
  vpn: ["vpn", "protonvpn", "windscribe", "mullvad", "proxy"],
  "social-media": [
    "social media",
    "buffer",
    "linktree",
    "instagram",
    "reel",
    "transcript",
    "transcribe",
    "speakapp",
    "schedule post",
    "metricool",
    "later",
  ],
  spreadsheets: ["spreadsheet", "excel", "sheets", "table", "csv", "airtable"],
  "speed-network": [
    "speed test",
    "network",
    "dns",
    "fast.com",
    "speedtest",
    "cloudflare",
    "whatsmydns",
  ],
  "stock-media": [
    "stock",
    "photo",
    "video",
    "unsplash",
    "pexels",
    "pixabay",
    "royalty free",
    "mixkit",
  ],
  "tech-communities": [
    "tech community",
    "dev.to",
    "hacker news",
    "stackoverflow",
    "reddit",
    "hashnode",
    "forum",
    "lemmy",
    "fediverse",
    "selfhosted",
    "search lemmy",
    "opensource",
  ],
  study: [
    "study",
    "flashcards",
    "quiz",
    "learn",
    "learning",
    "exam",
    "memorize",
    "school",
    "homework",
    "knowt",
    "quizlet",
    "anki",
    "studocu",
    "cluely",
    "youlearn",
    "khan",
    "coursera",
    "goblin tools",
    "brainscape",
    "cram",
    "learn anything",
    "learning paths",
  ],
  "student-discounts": [
    "student discount",
    "unidays",
    "student beans",
    "honey",
    "coupon",
    "deal",
    "save money",
  ],
  "3d-animation": [
    "3d",
    "animation",
    "blender",
    "tinkercad",
    "freecad",
    "spline",
    "sketchup",
    "model",
    "godot",
    "game engine",
  ],
  "todo-list": [
    "todo",
    "task",
    "list",
    "productivity",
    "ticktick",
    "todoist",
    "microsoft",
    "minimalist",
  ],
  translation: [
    "translate",
    "translation",
    "deepl",
    "google translate",
    "reverso",
    "language",
    "libretranslate",
  ],
  "typing-practice": [
    "typing",
    "keyboard",
    "wpm",
    "monkeytype",
    "keybr",
    "typeracer",
    "speed",
    "practice",
  ],
  utilities: [
    "utility",
    "qr",
    "password",
    "random",
    "url",
    "shortener",
    "barcode",
    "tinyurl",
    "toolfk",
    "ifixit",
    "fix",
    "cheat sheet",
    "rustdesk",
    "remote desktop",
  ],
  video: [
    "video",
    "convert",
    "youtube",
    "download",
    "clipchamp",
    "cnvmp3",
    "online convert",
    "vsave",
    "openshot",
    "shotcut",
    "kapwing",
    "flexclip",
    "opencut",
    "video editor",
  ],
  "website-builders": [
    "website",
    "builder",
    "emergent",
    "deploy",
    "formspree",
    "forms",
    "vercel",
    "netlify",
    "github pages",
    "carrd",
    "wordpress",
  ],
  writing: [
    "writing",
    "word counter",
    "hemingway",
    "scribbr",
    "writers digest",
  ],
  citations: ["citation", "zotero", "mendeley", "bibme", "refworks", "cite"],

  "osint-username": [
    "osint",
    "username",
    "whatsmyname web",
    "whatsmyname t",
    "sylva identity discovery t",
    "sherlock t",
    "namechk",
    "thats them",
  ],
  "osint-email-address": [
    "osint",
    "email-address",
    "sylva identity discovery t",
    "thatsthem",
    "hunter",
    "email to address r",
    "voilanorbert",
    "ghunt t",
  ],
  "osint-domain-name": [
    "osint",
    "domain-name",
    "domain dossier",
    "domainiq",
    "domaintools whois",
    "switch internet domains whois ch",
    "whoisology",
    "whois arin",
  ],
  "osint-cloud-infrastructure": [
    "osint",
    "cloud-infrastructure",
    "awsbucketdump t",
    "cloud enum t",
    "subfinder t",
    "aadinternals t",
    "gcpbucketbrute t",
    "microburst t",
  ],
  "osint-ip-mac-address": [
    "osint",
    "ip-mac-address",
    "maxmind demo",
    "ipv4 ipv6 lists by country code",
    "ip2location com",
    "ip fingerprints",
    "db ip",
    "ip location finder",
  ],
  "osint-image-search": [
    "osint",
    "image search",
    "reverse image",
    "google images",
    "bing images",
    "face search",
    "pimeyes",
  ],
  "osint-video-search": ["osint", "video search", "youtube", "footage"],
  "osint-document-search": ["osint", "document search", "pdf", "slides"],
  "osint-social-networks": [
    "osint",
    "social-networks",
    "fb email search",
    "recover fb account",
    "facebook photos by id m",
    "fb lookup id",
    "fediverse observer",
    "fediverse osint t",
  ],
  "osint-instant-messaging": [
    "osint",
    "instant-messaging",
    "comms analyzer toolbox t",
    "disboard",
    "discordosint t",
    "awesome osint",
    "osint industries",
    "slackpirate t",
  ],
  "osint-people-search-engines": [
    "osint",
    "people-search-engines",
    "infoflow public people search in chilean",
    "thatsthem",
    "melissa data people finder r",
    "peekyou",
    "webmii",
    "snitch name",
  ],
  "osint-dating": [
    "osint",
    "dating",
    "ayi com",
    "plenty of fish com",
    "eharmony",
    "farmers only",
    "tinder r",
    "bumble r",
  ],
  "osint-telephone-numbers": [
    "osint",
    "telephone-numbers",
    "slydial",
    "numbering plans",
    "numberway",
    "callerid test",
    "twilio lookup",
    "true caller",
  ],
  "osint-public-records": [
    "osint",
    "public-records",
    "melissa data property viewer r",
    "regrid us only",
    "neighbor report",
    "redfin",
    "nationwide county court records",
    "world legal information institute",
  ],
  "osint-compliance-risk-intelligence": [
    "osint",
    "compliance-risk-intelligence",
    "opensanctions",
    "ofac sanctions list search",
    "eu sanctions tool d",
    "dilisense",
    "namescan",
    "openscreening",
  ],
  "osint-business-records": [
    "osint",
    "business-records",
    "annualreports com",
    "public register online",
    "public register s annual report service",
    "international registries",
    "commercial register worldwide",
    "sec gov edgar",
  ],
  "osint-transportation": [
    "osint",
    "transportation",
    "myaccident traffic accident map",
    "nhtsa vehicle api",
    "findbyplate",
    "carvertical vin decoder",
    "autodna vin lookup",
    "vindecodr",
  ],
  "osint-geolocation-tools-maps": [
    "osint",
    "geolocation-tools-maps",
    "astrometry",
    "suncalc",
    "geospy",
    "gpsvisualizer",
    "military grid reference system coordinates",
  ],
  "osint-search-engines": [
    "osint",
    "search-engines",
    "google",
    "bing",
    "duckduckgo",
    "yahoo advanced web search",
    "startpage",
    "yandex",
  ],
  "osint-online-communities": [
    "osint",
    "online-communities",
    "live journal seek",
    "blog search engine",
    "discord bot list",
    "reconxplorer t",
    "top gg",
    "boardreader",
  ],
  "osint-archives": [
    "osint",
    "archives",
    "anna s archive",
    "archive is",
    "cached pages",
    "cached view",
    "common crawl",
    "internet archive wayback machine",
  ],
  "osint-language-translation": [
    "osint",
    "language-translation",
    "bing translate",
    "cambridge dictionary",
    "deepl translator",
    "free translation",
    "google input tools",
    "google translate",
  ],
  "osint-mobile-osint": [
    "osint",
    "mobile-osint",
    "genymotion t",
    "bluestacks 2 t",
    "nox app player",
    "apk online",
    "facebook t",
    "linkedin t",
  ],
  "osint-dark-web": [
    "osint",
    "dark-web",
    "reddit deep web",
    "reddit onions",
    "reddit darknet",
    "tor download t",
    "freenet project t",
    "i2p anonymous network t",
  ],
  "osint-disinformation-media-verification": [
    "osint",
    "disinformation-media-verification",
    "deepfake detect",
    "deepsafe",
    "deepfakebench",
    "deepfakedetector",
    "faceforensics",
    "invid weverify verification plugin",
  ],
  "osint-blockchain-cryptocurrency": [
    "osint",
    "blockchain-cryptocurrency",
    "bitcoin who s who",
    "bitref",
    "blockonomics",
    "orbit t",
    "wallet explorer",
    "bitcoin abuse database",
  ],
  "osint-classifieds": [
    "osint",
    "classifieds",
    "craigslist",
    "kijiji canada classifieds",
    "quikr india classifieds",
    "ebay",
    "offerup",
    "goofbid",
  ],
  "osint-encoding-decoding": [
    "osint",
    "encoding-decoding",
    "clearimage barcode reader",
    "js beautifier",
    "spidermonkey t",
    "kahu revelo t",
    "javascript deobfuscator t",
    "ddecode php decoder",
  ],
  "osint-tools": [
    "osint",
    "tools",
    "omnibus t",
    "photon t",
    "ifttt",
    "slash",
    "osrframework t",
    "intrec pack t",
  ],
  "osint-ai-tools": [
    "osint",
    "ai-tools",
    "ai or not",
    "copyleaks",
    "decopy ai image detector",
    "deepai ai image detector",
    "deepseek",
    "docmind ai",
  ],
  "osint-malicious-file-analysis": [
    "osint",
    "malicious-file-analysis",
    "decalage malware search",
    "virusshare com",
    "totalhash",
    "vx vault",
    "id ransomware",
    "national software reference library",
  ],
  "osint-cyber-threat-intelligence": [
    "osint",
    "cyber-threat-intelligence",
    "vulert updated open source vulnerability database",
    "securityfocus",
    "nvd nist",
    "osv vulnerability library",
    "cve details",
    "cve mitre",
  ],
  "osint-opsec": [
    "osint",
    "opsec",
    "fake name generator",
    "fake identity generator",
    "this person does not exist",
    "random user generator",
    "tor download t",
    "freenet project t",
  ],
  "osint-documentation-evidence-capture": [
    "osint",
    "documentation-evidence-capture",
    "forensic osint t",
    "fiddler t",
    "burp suite t",
    "page2images t",
    "archive is",
    "web page saver",
  ],
  "osint-training": [
    "osint",
    "training",
    "geoguesser",
    "verif cation quiz bot",
    "forensic osint kb guides",
    "open source intelligence techniques",
    "plessas",
    "the osintion",
  ],
};

function isLinkVisible(link) {
  return link.style.display !== "none";
}

function getVisibleLinksInSection(section) {
  return Array.from(section.querySelectorAll(".tool-link")).filter(
    isLinkVisible,
  );
}

function measureCollapsedToolsHeight(section, visibleLinks) {
  const tools = section.querySelector(".category-tools");
  if (!tools || visibleLinks.length <= CATEGORY_VISIBLE_LIMIT) {
    return tools ? tools.scrollHeight : 0;
  }
  const lastVisible = visibleLinks[CATEGORY_VISIBLE_LIMIT - 1];
  const toolsTop = tools.getBoundingClientRect().top;
  const lastBottom = lastVisible.getBoundingClientRect().bottom;
  return Math.ceil(lastBottom - toolsTop + 12);
}

function updateSeeMoreButton(section, visibleCount) {
  const btn = section.querySelector(".category-see-more");
  if (!btn) return;
  const extra = visibleCount - CATEGORY_VISIBLE_LIMIT;
  const isExpanded = section.classList.contains("is-expanded");
  btn.textContent = isExpanded ? "Show less" : `See more (${extra})`;
  btn.setAttribute("aria-expanded", isExpanded ? "true" : "false");
}

function expandCategory(section) {
  const tools = section.querySelector(".category-tools");
  if (!tools) return;

  const startHeight = tools.getBoundingClientRect().height;
  section.classList.add("is-expanded");
  section.classList.remove("is-collapsed");
  tools.style.maxHeight = `${startHeight}px`;

  requestAnimationFrame(() => {
    tools.style.maxHeight = `${tools.scrollHeight}px`;
  });

  const onEnd = (event) => {
    if (event.propertyName !== "max-height") return;
    tools.removeEventListener("transitionend", onEnd);
    if (section.classList.contains("is-expanded")) {
      tools.style.maxHeight = "none";
    }
    updateSeeMoreButton(section, getVisibleLinksInSection(section).length);
  };
  tools.addEventListener("transitionend", onEnd);
}

function collapseCategory(section) {
  const tools = section.querySelector(".category-tools");
  if (!tools) return;

  const visible = getVisibleLinksInSection(section);
  const targetHeight = measureCollapsedToolsHeight(section, visible);
  const startHeight = tools.getBoundingClientRect().height;

  section.classList.remove("is-expanded");
  section.classList.add("is-collapsed");
  tools.style.maxHeight = `${startHeight}px`;

  requestAnimationFrame(() => {
    tools.style.maxHeight = `${targetHeight}px`;
  });

  const onEnd = (event) => {
    if (event.propertyName !== "max-height") return;
    tools.removeEventListener("transitionend", onEnd);
    updateSeeMoreButton(section, visible.length);
  };
  tools.addEventListener("transitionend", onEnd);
}

function toggleCategoryExpand(section) {
  const categoryId = section.dataset.category;
  if (!categoryId) return;

  if (section.classList.contains("is-expanded")) {
    expandedCategories.delete(categoryId);
    collapseCategory(section);
    return;
  }

  expandedCategories.add(categoryId);
  expandCategory(section);
}

function initLoadedCategory(section) {
  if (section.querySelector(".category-see-more")) return;
  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "category-see-more";
  btn.hidden = true;
  btn.setAttribute("aria-expanded", "false");
  btn.addEventListener("click", () => toggleCategoryExpand(section));
  section.appendChild(btn);
}

function initCategorySeeMore() {
  categorySections.forEach((section) => {
    if (window.FUTCategoryLoader?.isDeferred(section)) return;
    initLoadedCategory(section);
  });
}

function onCategoryLoaded(event) {
  const section = event.detail?.section;
  if (!section) return;

  injectPricingLabelsIn(section);
  updatePricingLabelsIn(section);
  initLoadedCategory(section);

  section.querySelectorAll(".tool-link").forEach((link) => {
    const pricing = link.dataset.pricing || "free";
    link.style.display = matchesPricingMode(pricing, currentMode) ? "" : "none";
  });

  const anyVisible = getVisibleLinksInSection(section).length > 0;
  section.classList.toggle("is-hidden", !anyVisible);
  updateCategoryCollapseForSection(section);
}

function updateCategoryCollapseForSection(section) {
  const queryActive = Boolean((toolsSearch?.value || "").trim());
  const tools = section.querySelector(".category-tools");
  const btn = section.querySelector(".category-see-more");
  if (!tools || !btn) return;

  const visible = getVisibleLinksInSection(section);
  const categoryId = section.dataset.category;
  const shouldCollapse =
    !queryActive && visible.length > CATEGORY_VISIBLE_LIMIT;

  if (!shouldCollapse) {
    section.classList.remove("is-collapsed", "is-expanded");
    tools.style.maxHeight = "none";
    btn.hidden = true;
    if (categoryId) expandedCategories.delete(categoryId);
    return;
  }

  btn.hidden = false;
  const isExpanded = categoryId && expandedCategories.has(categoryId);

  if (isExpanded) {
    section.classList.add("is-expanded");
    section.classList.remove("is-collapsed");
    tools.style.maxHeight = "none";
  } else {
    section.classList.remove("is-expanded");
    section.classList.add("is-collapsed");
    tools.style.maxHeight = `${measureCollapsedToolsHeight(section, visible)}px`;
  }

  updateSeeMoreButton(section, visible.length);
}

function updateCategoryCollapse() {
  categorySections.forEach((section) => {
    updateCategoryCollapseForSection(section);
  });
}

let resizeTimer;
function scheduleCategoryCollapseUpdate() {
  window.clearTimeout(resizeTimer);
  resizeTimer = window.setTimeout(updateCategoryCollapse, 150);
}

function applyFilters() {
  if (window.FUTStudentSearch) {
    window.FUTStudentSearch.applyFilters();
    return;
  }
}

function getPaidLabelForLink(linkEl) {
  const name = (
    linkEl.querySelector(".tool-link-name")?.textContent || ""
  ).toLowerCase();
  if (name.includes("chatgpt")) return "Plus";
  if (name.includes("claude")) return "Pro";
  if (name.includes("grammarly")) return "Premium";
  if (name.includes("quillbot")) return "Premium";
  if (name.includes("notion")) return "Plus";
  return "Paid";
}

function injectPricingLabelsIn(root) {
  root.querySelectorAll(".tool-link").forEach((link) => {
    if (link.querySelector(".tool-pricing-label")) return;
    const span = document.createElement("span");
    span.className = "tool-pricing-label";
    link.appendChild(span);
  });
}

function injectPricingLabels() {
  injectPricingLabelsIn(document);
}

function updatePricingLabelsIn(root) {
  root.querySelectorAll(".tool-link").forEach((link) => {
    const pricing = link.dataset.pricing || "free";
    const labelEl = link.querySelector(".tool-pricing-label");
    if (!labelEl) return;

    let labelText = "Free";
    let labelKey = pricing;

    if (currentMode === "free") {
      if (pricing === "free") {
        labelText = "Free";
        labelKey = "free";
      } else if (pricing === "free-tier") {
        labelText = "Free Tier";
        labelKey = "free-tier";
      } else if (pricing === "limited") {
        labelText = "Limited";
        labelKey = "limited";
      } else if (pricing === "paid") {
        labelText = "Paid";
        labelKey = "paid";
      }
    } else if (pricing === "free") {
      labelText = "Free";
      labelKey = "free";
    } else if (
      pricing === "paid" ||
      pricing === "limited" ||
      pricing === "free-tier"
    ) {
      labelText = getPaidLabelForLink(link);
      labelKey = "paid";
    }

    labelEl.textContent = labelText;
    labelEl.setAttribute("data-label", labelKey);
  });
}

function updatePricingLabels() {
  updatePricingLabelsIn(document);
}

function setMode(nextMode) {
  if (nextMode !== "free" && nextMode !== "paid") return;
  currentMode = nextMode;
  if (document.body) {
    document.body.dataset.mode = nextMode;
  }
  if (toolsModeToggle) {
    toolsModeToggle.dataset.mode = nextMode;
  }
  toggleOptions.forEach((option) => {
    option.classList.toggle("active", option.dataset.mode === nextMode);
  });
  updatePricingLabels();
  applyFilters();
}

toggleOptions.forEach((option) => {
  option.addEventListener("click", () => setMode(option.dataset.mode));
});

injectPricingLabels();
updatePricingLabels();
initCategorySeeMore();

if (toolsSearch && window.FUTStudentSearch) {
  window.FUTStudentSearch.init({
    input: toolsSearch,
    searchIndex: window.FUTCategoryLoader?.searchIndex,
    toolLinks: getToolLinks(),
    categorySections,
    categoryKeywords: CATEGORY_KEYWORDS,
    getMode: () => currentMode,
    matchesPricingMode,
    onFilterComplete: () => {
      const hasSearch = Boolean(window.FUTStudentSearch?.getQuery()?.trim());
      if (hasSearch) {
        if (typeof window.resetPageTocVisibility === "function") {
          window.resetPageTocVisibility();
        }
      } else if (typeof window.updatePageToc === "function") {
        window.updatePageToc();
      }
      updateCategoryCollapse();
    },
  });
} else {
  applyFilters();
}

window.addEventListener("fut:category-loaded", onCategoryLoaded);

window.addEventListener("resize", scheduleCategoryCollapseUpdate);