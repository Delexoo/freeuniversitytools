(function () {
  const STORAGE_KEY = "fut-saved-tools";
  const DATA_URL = "data/scroll-tools.json";
  const FALLBACK_ICON =
    "https://raw.githubusercontent.com/Delexoo/freeuniversitytools/refs/heads/main/doc/FreeUniversityTools.png";

  const els = {
    stage: document.getElementById("scrollStage"),
    card: document.getElementById("scrollCard"),
    dock: document.getElementById("scrollDock"),
    loading: document.getElementById("scrollLoading"),
    empty: document.getElementById("scrollEmpty"),
    progress: document.getElementById("scrollProgress"),
    progressBar: document.getElementById("scrollProgressBar"),
    tabs: Array.from(document.querySelectorAll(".scroll-tab[data-mode]")),
    savedBadge: document.getElementById("scrollSavedBadge"),
    prevBtn: document.getElementById("scrollPrev"),
    nextBtn: document.getElementById("scrollNext"),
  };

  let allTools = [];
  let feedTools = [];
  let index = 0;
  let mode = "discover";
  let saved = loadSaved();
  let animating = false;
  let touchStartY = 0;
  let touchStartX = 0;
  const iconPreloads = new Map();
  const iconWaiters = new Map();
  let panelBuilt = false;
  let panel = null;

  function networkIconForTool(tool) {
    if (!tool?.domain) return "";
    if (tool.url?.includes("github.com")) {
      try {
        const owner = new URL(tool.url).pathname.split("/").filter(Boolean)[0];
        if (owner) return `https://github.com/${owner}.png?size=64`;
      } catch {
        /* fall through */
      }
    }
    return `https://icon.horse/icon/${encodeURIComponent(tool.domain)}`;
  }

  function resolveIconUrl(tool) {
    const icon = (tool?.icon || "").trim();
    if (icon && /FreeUniversityTools\.png|\/doc\//i.test(icon)) return icon;
    return networkIconForTool(tool) || FALLBACK_ICON;
  }

  function warmIcon(url) {
    const src = url || FALLBACK_ICON;
    const state = iconPreloads.get(src);
    if (state === "loaded") return Promise.resolve(src);
    if (state === "error") return Promise.resolve(FALLBACK_ICON);
    if (state === "pending") {
      return new Promise((resolve) => {
        const list = iconWaiters.get(src) || [];
        list.push(resolve);
        iconWaiters.set(src, list);
      });
    }

    return new Promise((resolve) => {
      const img = new Image();
      img.referrerPolicy = "no-referrer";
      img.decoding = "async";
      img.onload = () => {
        iconPreloads.set(src, "loaded");
        resolve(src);
        (iconWaiters.get(src) || []).forEach((fn) => fn(src));
        iconWaiters.delete(src);
      };
      img.onerror = () => {
        iconPreloads.set(src, "error");
        resolve(FALLBACK_ICON);
        (iconWaiters.get(src) || []).forEach((fn) => fn(FALLBACK_ICON));
        iconWaiters.delete(src);
      };
      iconPreloads.set(src, "pending");
      img.src = src;
    });
  }

  function warmIconsForTools(tools) {
    tools.forEach((tool) => {
      warmIcon(resolveIconUrl(tool));
    });
  }

  function preloadAdjacentIcons() {
    const list = currentList();
    if (!list.length) return;
    [-3, -2, -1, 0, 1, 2, 3, 4, 5].forEach((offset) => {
      const tool = list[index + offset];
      if (tool) warmIcon(resolveIconUrl(tool));
    });
  }

  function hintIconPreload(url) {
    if (!url || document.querySelector(`link[data-scroll-icon="${url}"]`)) return;
    const link = document.createElement("link");
    link.rel = "preload";
    link.as = "image";
    link.href = url;
    link.dataset.scrollIcon = url;
    document.head.appendChild(link);
  }

  function applyIcon(img, tool) {
    if (!img) return;
    const url = resolveIconUrl(tool);
    img.dataset.pendingIcon = url;
    hintIconPreload(url);

    if (iconPreloads.get(url) === "loaded") {
      img.src = url;
      img.dataset.iconUrl = url;
      return;
    }

    if (img.dataset.iconUrl && img.complete && img.naturalWidth > 0) {
      warmIcon(url).then((ready) => {
        if (img.dataset.pendingIcon !== url) return;
        img.src = ready;
        img.dataset.iconUrl = ready;
      });
      return;
    }

    warmIcon(url).then((ready) => {
      if (img.dataset.pendingIcon !== url) return;
      img.src = ready;
      img.dataset.iconUrl = ready;
    });
  }

  function loadSaved() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      return new Set(raw ? JSON.parse(raw) : []);
    } catch {
      return new Set();
    }
  }

  function persistSaved() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify([...saved]));
    updateSavedBadge();
  }

  function updateSavedBadge() {
    const count = saved.size;
    document.querySelectorAll(".scroll-tab-badge").forEach((badge) => {
      badge.textContent = String(count);
      badge.hidden = count === 0;
    });
  }

  function pricingLabel(pricing) {
    const map = {
      free: "Free",
      "free-tier": "Free tier",
      limited: "Limited",
      paid: "Paid",
    };
    return map[pricing] || "Free";
  }

  const BAD_TOOL_NAMES = new Set(["\u2014", "\u2013", "-", "–", "—"]);

  function isBadToolName(name) {
    const value = String(name || "").trim();
    if (!value) return true;
    if (BAD_TOOL_NAMES.has(value)) return true;
    return /^[\s\u2014\u2013\-–—]+$/.test(value);
  }

  function normalizeTool(raw) {
    return {
      id: raw.id,
      name: raw.n || raw.name,
      url: raw.u || raw.url,
      icon: raw.i || raw.icon,
      fallback: raw.f || raw.fallback,
      pricing: raw.p || raw.pricing || "free",
      category: raw.c || raw.category,
      categorySlug: raw.s || raw.categorySlug,
      domain: raw.d || raw.domain,
      desc:
        raw.x ||
        raw.desc ||
        `Student tool in ${raw.c || "the directory"}. Visit ${raw.d || "the site"} to use it.`,
    };
  }

  function shuffle(list) {
    const arr = list.slice();
    for (let i = arr.length - 1; i > 0; i -= 1) {
      const j = Math.floor(Math.random() * (i + 1));
      [arr[i], arr[j]] = [arr[j], arr[i]];
    }
    return arr;
  }

  function currentList() {
    if (mode === "saved") {
      return allTools.filter((tool) => saved.has(tool.id));
    }
    return feedTools;
  }

  function setMode(nextMode) {
    if (mode === nextMode) return;
    mode = nextMode;
    index = 0;
    els.tabs.forEach((tab) => {
      const active = tab.dataset.mode === mode;
      tab.classList.toggle("active", active);
      tab.setAttribute("aria-selected", active ? "true" : "false");
    });
    refreshView(true);
  }

  function toggleSave() {
    const tool = currentList()[index];
    if (!tool) return;
    if (saved.has(tool.id)) {
      saved.delete(tool.id);
    } else {
      saved.add(tool.id);
    }
    persistSaved();
    renderCard(tool);
    if (mode === "saved") {
      const list = currentList();
      if (list.length === 0) {
        refreshView(true);
        return;
      }
      if (index >= list.length) {
        index = Math.max(0, list.length - 1);
        refreshView(true);
      }
    }
  }

  function iconFallback(img) {
    if (img.src !== FALLBACK_ICON) img.src = FALLBACK_ICON;
    img.dataset.iconUrl = FALLBACK_ICON;
  }

  function ensurePanel() {
    if (panelBuilt || !els.card) return;
    els.card.innerHTML = `
      <div class="scroll-panel">
        <header class="scroll-panel-header">
          <span class="scroll-panel-eyebrow"></span>
          <span class="scroll-pricing tool-pricing-label"></span>
        </header>
        <div class="scroll-panel-hero">
          <div class="scroll-icon-wrap">
            <img class="scroll-icon" alt="" loading="eager" fetchpriority="high" decoding="sync" referrerpolicy="no-referrer">
          </div>
          <div class="scroll-panel-identity">
            <h1 class="scroll-name"></h1>
            <a class="scroll-domain" target="_blank" rel="noopener noreferrer"></a>
          </div>
        </div>
        <div class="scroll-panel-body">
          <p class="scroll-about"></p>
        </div>
        <div class="scroll-panel-actions">
          <a class="btn-primary" target="_blank" rel="noopener noreferrer">
            Open tool
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
              <path d="M7 17L17 7M17 7H9M17 7V15" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </a>
          <button type="button" class="scroll-save" aria-label="Save tool" aria-pressed="false">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
              <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/>
            </svg>
            <span class="scroll-save-label">Save</span>
          </button>
        </div>
      </div>
    `;

    panel = {
      eyebrow: els.card.querySelector(".scroll-panel-eyebrow"),
      pricing: els.card.querySelector(".scroll-pricing"),
      icon: els.card.querySelector(".scroll-icon"),
      name: els.card.querySelector(".scroll-name"),
      domain: els.card.querySelector(".scroll-domain"),
      about: els.card.querySelector(".scroll-about"),
      open: els.card.querySelector(".btn-primary"),
      save: els.card.querySelector(".scroll-save"),
      saveLabel: els.card.querySelector(".scroll-save-label"),
      saveIcon: els.card.querySelector(".scroll-save svg"),
    };

    panel.icon?.addEventListener("error", () => iconFallback(panel.icon), { once: false });
    panel.save?.addEventListener("click", toggleSave);
    panelBuilt = true;
  }

  function aboutText(tool) {
    const short = CATEGORY_BLURBS[tool.categorySlug];
    if (short) return short.split(".")[0].trim() + ".";
    if (tool.category) return `Listed under ${tool.category}.`;
    return "From the student tools directory.";
  }

  function renderCard(tool) {
    if (!tool || !els.card) return;

    ensurePanel();
    if (!panel) return;

    const isSaved = saved.has(tool.id);
    const pricing = tool.pricing || "free";

    panel.eyebrow.textContent = tool.category || "";
    panel.pricing.textContent = pricingLabel(pricing);
    panel.pricing.dataset.label = pricing;
    panel.name.textContent = tool.name || "";
    panel.domain.textContent = tool.domain || "";
    panel.domain.href = tool.url || "#";
    panel.about.textContent = aboutText(tool);
    panel.open.href = tool.url || "#";

    panel.save.classList.toggle("is-saved", isSaved);
    panel.save.setAttribute("aria-label", isSaved ? "Remove from saved" : "Save tool");
    panel.save.setAttribute("aria-pressed", isSaved ? "true" : "false");
    if (panel.saveLabel) panel.saveLabel.textContent = isSaved ? "Saved" : "Save";
    if (panel.saveIcon) {
      panel.saveIcon.setAttribute("fill", isSaved ? "currentColor" : "none");
    }

    applyIcon(panel.icon, tool);
    preloadAdjacentIcons();
  }

  function updateChrome() {
    const list = currentList();
    const total = list.length;
    const hasItems = total > 0;

    if (els.loading) els.loading.hidden = true;
    if (els.empty) els.empty.hidden = hasItems;
    if (els.card) els.card.hidden = !hasItems;
    if (els.dock) els.dock.hidden = !hasItems;
    if (els.progress) {
      els.progress.textContent = hasItems ? `${index + 1} / ${total}` : "";
    }
    if (els.progressBar && hasItems) {
      els.progressBar.style.width = `${((index + 1) / total) * 100}%`;
    } else if (els.progressBar) {
      els.progressBar.style.width = "0%";
    }
    if (els.prevBtn) els.prevBtn.disabled = !hasItems || index <= 0;
    if (els.nextBtn) els.nextBtn.disabled = !hasItems || index >= total - 1;
  }

  function refreshView(animate) {
    const list = currentList();
    updateChrome();
    if (!list.length) return;

    if (index >= list.length) index = list.length - 1;
    if (index < 0) index = 0;

    const tool = list[index];
    if (!animate) {
      renderCard(tool);
      return;
    }

    renderCard(tool);
    els.card.classList.remove("is-enter-from-bottom", "is-enter-from-top", "is-exit-up", "is-exit-down");
    void els.card.offsetWidth;
    els.card.classList.add("is-enter-from-bottom");
    requestAnimationFrame(() => {
      els.card.classList.remove("is-enter-from-bottom");
    });
  }

  function navigate(direction) {
    if (animating) return;
    const list = currentList();
    if (!list.length) return;

    const nextIndex = index + direction;
    if (nextIndex < 0 || nextIndex >= list.length) return;

    const nextTool = list[nextIndex];
    if (nextTool) warmIcon(resolveIconUrl(nextTool));

    animating = true;
    const exitClass = direction > 0 ? "is-exit-up" : "is-exit-down";
    const enterClass = direction > 0 ? "is-enter-from-bottom" : "is-enter-from-top";

    els.card.classList.remove("is-enter-from-bottom", "is-enter-from-top", "is-exit-up", "is-exit-down");
    els.card.classList.add(exitClass);

    window.setTimeout(() => {
      index = nextIndex;
      renderCard(list[index]);
      updateChrome();
      els.card.classList.remove(exitClass);
      els.card.classList.add(enterClass);
      requestAnimationFrame(() => {
        els.card.classList.remove(enterClass);
        animating = false;
      });
    }, 180);
  }

  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function escapeAttr(value) {
    return escapeHtml(value).replace(/'/g, "&#39;");
  }

  const CATEGORY_BLURBS = {
    "must-try": "Standout pick from the directory, worth trying first.",
    "github-powerhouses": "Popular open-source project on GitHub for learning and building.",
    "free-books": "Find free textbooks, PDFs, and ebooks for coursework and reading.",
    courses: "Courses, tutorials, and learning platforms for self-paced study.",
    study: "Study aids: flashcards, notes, quizzes, and exam prep.",
    ai: "AI assistant or chat tool for questions, writing, and productivity.",
    "ai-study-tools": "AI-powered homework help, quizzes, and study workflows.",
    research: "Research and lookup tools for papers, sources, and deep answers.",
    "essay-tools": "Writing, citations, grammar, and essay workflow tools.",
    "free-movies": "Streaming and media sites for movies, shows, and entertainment.",
    "free-stuff": "Free resources, alternatives, and discovery hubs for students.",
    design: "Design, UI, fonts, and creative tools for projects and portfolios.",
    programming: "Coding references, docs, practice, and developer utilities.",
    "programming-ai": "AI coding assistants, completions, and dev-focused AI tools.",
    pdf: "PDF viewing, editing, conversion, and document utilities.",
    utilities: "Handy everyday utilities: converters, helpers, and small tools.",
    productivity: "Productivity apps for focus, planning, and getting work done.",
    security: "Security, privacy, and safety tools for your accounts and devices.",
    "open-source": "Open-source software discovery and FOSS community resources.",
    "chrome-extension": "Browser extensions that add features inside Chrome.",
    "browser-extensions": "Browser add-ons for privacy, media, and productivity.",
    cloud: "File sharing, storage, and sync for documents and media.",
    "generative-ai": "Generative AI for images, audio, video, and creative output.",
    "local-ai": "Run or chat with AI models locally on your own machine.",
    "osint-tools": "Open-source intelligence and online research utilities.",
  };

  const PRICING_INTRO = {
    free: "Free to use",
    "free-tier": "Free tier available",
    limited: "Limited free access",
    paid: "Paid service",
  };

  function setLoadingMessage(text) {
    const msg = els.loading?.querySelector("p");
    if (msg) msg.textContent = text;
  }

  function normId(url) {
    try {
      const p = new URL(url);
      return `${p.hostname.replace(/^www\./, "")}${p.pathname.replace(/\/$/, "")}`.toLowerCase();
    } catch {
      return url.toLowerCase();
    }
  }

  function domainFrom(url) {
    try {
      return new URL(url).hostname.replace(/^www\./, "");
    } catch {
      return "";
    }
  }

  function makeBlurb(name, catSlug, catTitle, pricing, url, domain) {
    if (CATEGORY_BLURBS[catSlug]) return CATEGORY_BLURBS[catSlug];
    const intro = PRICING_INTRO[pricing] || "Free to use";
    const title = (catTitle || "student tools").toLowerCase();
    if (url.includes("github.com")) {
      return `${intro}, open-source project under ${catTitle}. Explore repos, docs, and releases on GitHub.`;
    }
    if (catSlug.startsWith("osint-")) {
      return `${intro}, research tool for ${title}. Useful for online lookup and investigation.`;
    }
    return `${intro} for ${title}. Core functions live at ${domain}.`;
  }

  function parseToolsFromDocument(doc) {
    const tools = [];
    const seen = new Set();

    doc.querySelectorAll(".tool-category").forEach((section) => {
      const catTitle = section.querySelector(".category-title")?.textContent?.trim() || "";
      const catSlug = section.dataset.category || "";
      section.querySelectorAll("a.tool-link").forEach((link) => {
        const url = link.getAttribute("href") || "";
        if (!url.startsWith("http")) return;
        const id = normId(url);
        if (seen.has(id)) return;
        seen.add(id);
        const name = link.querySelector(".tool-link-name")?.textContent?.trim() || domainFrom(url);
        if (isBadToolName(name)) return;
        const icon = link.querySelector("img")?.getAttribute("src") || "";
        const fallback = link.querySelector("img")?.getAttribute("data-fallback") || "";
        const pricing = link.dataset.pricing || "free";
        const domain = domainFrom(url);
        tools.push({
          id,
          name,
          url,
          icon: icon || `https://icon.horse/icon/${domain}`,
          fallback: fallback || `https://icon.horse/icon/${domain}`,
          pricing,
          category: catTitle,
          categorySlug: catSlug,
          domain,
          desc: makeBlurb(name, catSlug, catTitle, pricing, url, domain),
        });
      });
    });

    return tools;
  }

  async function loadToolsFromJson() {
    const res = await fetch(DATA_URL);
    if (!res.ok) throw new Error(`JSON ${res.status}`);
    const data = await res.json();
    if (!Array.isArray(data) || !data.length) throw new Error("Empty JSON");
    return data.map(normalizeTool).filter((tool) => !isBadToolName(tool.name));
  }

  async function loadToolsFromStudentHtml() {
    setLoadingMessage("Loading directory…");
    const res = await fetch("student.html");
    if (!res.ok) throw new Error(`student.html ${res.status}`);
    const html = await res.text();
    setLoadingMessage("Preparing tools…");
    const doc = new DOMParser().parseFromString(html, "text/html");
    const tools = parseToolsFromDocument(doc);
    if (!tools.length) throw new Error("No tools parsed");
    return tools;
  }

  async function loadTools() {
    try {
      allTools = await loadToolsFromJson();
    } catch (jsonErr) {
      console.warn("Scroll JSON unavailable, using student.html:", jsonErr);
      allTools = await loadToolsFromStudentHtml();
    }
    allTools = allTools.filter((tool) => !isBadToolName(tool.name));
    feedTools = shuffle(allTools);
  }

  function bindEvents() {
    els.tabs.forEach((tab) => {
      tab.addEventListener("click", () => setMode(tab.dataset.mode || "discover"));
    });

    if (els.prevBtn) els.prevBtn.addEventListener("click", () => navigate(-1));
    if (els.nextBtn) els.nextBtn.addEventListener("click", () => navigate(1));

    const emptyDiscover = document.getElementById("scrollEmptyDiscover");
    if (emptyDiscover) {
      emptyDiscover.addEventListener("click", () => setMode("discover"));
    }

    window.addEventListener("keydown", (e) => {
      if (e.key === "ArrowDown" || e.key === "PageDown" || e.key === "j") {
        e.preventDefault();
        navigate(1);
      } else if (e.key === "ArrowUp" || e.key === "PageUp" || e.key === "k") {
        e.preventDefault();
        navigate(-1);
      }
    });

    let wheelLocked = false;
    els.stage?.addEventListener(
      "wheel",
      (e) => {
        if (Math.abs(e.deltaY) < 18) return;
        e.preventDefault();
        if (wheelLocked) return;
        wheelLocked = true;
        navigate(e.deltaY > 0 ? 1 : -1);
        window.setTimeout(() => {
          wheelLocked = false;
        }, 420);
      },
      { passive: false },
    );

    els.stage?.addEventListener(
      "touchstart",
      (e) => {
        touchStartY = e.changedTouches[0]?.clientY || 0;
        touchStartX = e.changedTouches[0]?.clientX || 0;
      },
      { passive: true },
    );

    els.stage?.addEventListener(
      "touchend",
      (e) => {
        const endY = e.changedTouches[0]?.clientY || 0;
        const endX = e.changedTouches[0]?.clientX || 0;
        const deltaY = touchStartY - endY;
        const deltaX = Math.abs(touchStartX - endX);
        if (deltaX > 40) return;
        if (deltaY > 55) navigate(1);
        else if (deltaY < -55) navigate(-1);
      },
      { passive: true },
    );
  }

  async function init() {
    updateSavedBadge();
    bindEvents();
    warmIcon(FALLBACK_ICON);

    if (window.location.protocol === "file:") {
      if (els.loading) {
        els.loading.innerHTML =
          "<p>Open this page through a local server (not as a file). From the project folder run: <code>python -m http.server 8080</code> then visit <code>http://localhost:8080/scroll.html</code></p>";
      }
      return;
    }

    try {
      await loadTools();
      const first = feedTools[0];
      if (first) {
        setLoadingMessage("Loading icons…");
        await warmIcon(resolveIconUrl(first));
      }
      warmIconsForTools(feedTools.slice(0, 24));
      refreshView(false);
    } catch (err) {
      if (els.loading) {
        els.loading.hidden = false;
        els.loading.innerHTML =
          '<p>Could not load tools. <a href="student.html">Browse the directory</a> instead.</p>';
      }
      console.error(err);
    }
  }

  init();
})();
