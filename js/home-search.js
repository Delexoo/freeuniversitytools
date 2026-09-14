(function () {
  const DATA_URL = "data/scroll-tools.json";
  const CATS_URL = "data/home-categories.json";
  const FALLBACK =
    "https://raw.githubusercontent.com/Delexoo/freeuniversitytools/refs/heads/main/doc/FreeUniversityTools.png";
  const PAGE_SIZE = 40;
  const CAT_PAGE_DESKTOP = 72;
  const CAT_PAGE_MOBILE = 24;
  const SUGGEST_LIMIT = 8;

  function catPageSize() {
    return window.matchMedia("(max-width: 768px)").matches
      ? CAT_PAGE_MOBILE
      : CAT_PAGE_DESKTOP;
  }

  const SYNONYMS = {
    ai: ["artificial intelligence", "llm", "gpt", "chatbot", "machine learning"],
    ml: ["machine learning", "ai"],
    pdf: ["document", "acrobat"],
    vpn: ["virtual private network", "privacy", "proxy"],
    note: [
      "notes",
      "notetaking",
      "note taking",
      "notebook",
      "notepad",
      "notetaker",
      "notetakers",
      "notion",
      "onenote",
      "obsidian",
      "simplenote",
      "google keep",
      "keep",
    ],
    notes: [
      "note",
      "notetaking",
      "note taking",
      "notebook",
      "notepad",
      "notetaker",
      "notetakers",
      "notion",
      "onenote",
      "obsidian",
      "simplenote",
      "google keep",
      "keep",
    ],
    study: ["learning", "homework", "exam", "flashcards", "school"],
    video: ["movie", "stream", "youtube", "clip", "mp4", "mp3"],
    image: ["photo", "picture", "png", "jpg", "jpeg", "webp", "gif"],
    audio: ["music", "sound", "mp3", "wav", "song"],
    code: ["programming", "developer", "ide", "coding"],
    math: ["mathematics", "calculator", "algebra"],
    write: ["writing", "essay", "grammar", "citation"],
    writing: ["write", "essay", "grammar", "citation", "notes"],
    design: ["ui", "figma", "canva", "graphics"],
    email: ["mail", "inbox"],
    free: ["gratis", "no cost", "opensource", "open source"],
    security: ["password", "privacy", "antivirus", "breach"],
    osint: ["open source intelligence", "investigation", "lookup"],
    convert: [
      "converter",
      "converters",
      "conversion",
      "converting",
      "transcode",
      "transcoder",
      "transform",
    ],
    converter: [
      "convert",
      "converters",
      "conversion",
      "converting",
      "transcode",
      "transcoder",
    ],
    converters: ["convert", "converter", "conversion"],
    conversion: ["convert", "converter", "converting"],
  };

  const PRICING_LABEL = {
    free: "Free",
    "free-tier": "Free Tier",
    limited: "Limited",
    paid: "Paid",
  };

  const KIND_LABEL = {
    website: "Website",
    ai: "AI",
    app: "App",
    extension: "Extension",
    github: "GitHub",
  };

  const els = {
    input: document.getElementById("homeSearch"),
    clear: document.getElementById("homeSearchClear"),
    go: document.getElementById("homeSearchGo"),
    suggestions: document.getElementById("homeSuggestions"),
    chips: document.getElementById("homeChips"),
    thumb: document.getElementById("homeFiltersThumb"),
    kindChips: document.getElementById("homeKindChips"),
    kindThumb: document.getElementById("homeKindThumb"),
    cats: document.getElementById("homeCategories"),
    catsMore: document.getElementById("homeCatsMore"),
    catMeta: document.getElementById("homeCatMeta"),
    results: document.getElementById("homeResults"),
    resultsHead: document.getElementById("homeResultsHead"),
    more: document.getElementById("homeMore"),
    loading: document.getElementById("homeLoading"),
  };

  let tools = [];
  let categories = [];
  let query = "";
  let pricingFilter = "all";
  let kindFilter = "all";
  let categoryFilter = "";
  let visible = PAGE_SIZE;
  let visibleCats = catPageSize();
  let activeSuggest = -1;
  let debounceTimer = null;

  function normalize(value) {
    return (value || "")
      .toLowerCase()
      .replace(/[''`]/g, "")
      .replace(/[^a-z0-9]+/g, " ")
      .trim();
  }

  /** Aggressive light stem so converter/converting/notes match convert/note. */
  function stem(term) {
    let t = normalize(term);
    if (t.length < 3) return t;

    if (t.length > 5 && t.endsWith("ies")) t = t.slice(0, -3) + "y";
    else if (t.length > 5 && t.endsWith("ves")) t = t.slice(0, -3) + "f";
    else if (t.length > 4 && t.endsWith("ses")) t = t.slice(0, -2);
    else if (t.length > 5 && t.endsWith("ers")) t = t.slice(0, -1);
    else if (t.length > 5 && t.endsWith("ors")) t = t.slice(0, -1);
    else if (t.length > 4 && t.endsWith("s") && !t.endsWith("ss") && !t.endsWith("us")) {
      t = t.slice(0, -1);
    }

    if (t.length > 6 && t.endsWith("ation")) t = t.slice(0, -5);
    else if (t.length > 6 && t.endsWith("ition")) t = t.slice(0, -5);
    else if (t.length > 5 && t.endsWith("sion")) t = t.slice(0, -4);
    else if (t.length > 5 && t.endsWith("tion")) t = t.slice(0, -4);

    if (t.length > 5 && t.endsWith("ing")) {
      t = t.slice(0, -3);
      if (t.length > 3 && t.endsWith(t[t.length - 1])) t = t.slice(0, -1);
    } else if (t.length > 4 && t.endsWith("er")) t = t.slice(0, -2);
    else if (t.length > 4 && t.endsWith("or")) t = t.slice(0, -2);
    else if (t.length > 4 && t.endsWith("ed")) {
      t = t.slice(0, -2);
      if (t.length > 3 && t.endsWith(t[t.length - 1])) t = t.slice(0, -1);
    }

    return t;
  }

  /** Morphological + synonym OR-set for one query word. */
  function variantsFor(word) {
    const base = normalize(word);
    if (!base) return [];
    const rooted = stem(base);
    const alts = new Set([base, rooted]);

    // Common surface forms so either side of a pair can match
    [rooted, base].forEach((root) => {
      if (root.length < 3) return;
      alts.add(root + "s");
      alts.add(root + "er");
      alts.add(root + "ers");
      alts.add(root + "or");
      alts.add(root + "ing");
      alts.add(root + "ed");
      alts.add(root + "ion");
      alts.add(root + "ions");
      alts.add(root + "ation");
      if (root.endsWith("e")) {
        alts.add(root.slice(0, -1) + "ing");
        alts.add(root + "r");
        alts.add(root + "rs");
      } else {
        alts.add(root + "eing");
      }
    });

    const syns = [
      ...(SYNONYMS[base] || []),
      ...(SYNONYMS[rooted] || []),
    ];
    syns.forEach((s) => {
      const n = normalize(s);
      if (!n) return;
      alts.add(n);
      alts.add(stem(n));
    });

    return Array.from(alts).filter((t) => t && t.length >= 2);
  }

  function termGroups(queryText) {
    return queryText
      .split(/\s+/)
      .filter(Boolean)
      .map((word) => variantsFor(word))
      .filter((group) => group.length);
  }

  /** Split CamelCase / digits so FreeConvert / CNVmp3 become searchable parts. */
  function splitCompounds(value) {
    return normalize(
      String(value || "")
        .replace(/([a-z])([A-Z])/g, "$1 $2")
        .replace(/([a-zA-Z])(\d)/g, "$1 $2")
        .replace(/(\d)([a-zA-Z])/g, "$1 $2")
    );
  }

  function buildSearchIndex(tool) {
    const name = normalize(tool.n);
    const nameParts = splitCompounds(tool.n);
    const domainRaw = (tool.d || "").toLowerCase().replace(/^www\./, "");
    const domain = normalize(domainRaw.replace(/\./g, " "));
    const domainNoTld = normalize(domainRaw.replace(/\.[a-z]{2,24}$/i, "").replace(/\./g, " "));
    const cat = normalize(`${tool.c || ""} ${(tool.s || "").replace(/-/g, " ")}`);
    const blurb = normalize(tool.x || "");
    const kind = normalize(toolKind(tool));
    const url = normalize((tool.u || "").replace(/https?:\/\//, "").replace(/[/?#=&._-]+/g, " "));

    const blob = [name, nameParts, domain, domainNoTld, cat, blurb, kind, url]
      .filter(Boolean)
      .join(" ");

    const tokens = new Set();
    const stems = new Set();
    blob.split(/\s+/).forEach((tok) => {
      if (!tok) return;
      tokens.add(tok);
      stems.add(stem(tok));
      // Keep long compounds for substring checks
      if (tok.length >= 6) tokens.add(tok);
    });

    return { name, domain, domainNoTld, cat, blurb, blob, tokens, stems };
  }

  function ensureIndex(tool) {
    if (!tool._idx) tool._idx = buildSearchIndex(tool);
    return tool._idx;
  }

  function iconFor(tool) {
    const icon = (tool.i || "").trim();
    if (icon && !/FreeUniversityTools\.png/i.test(icon)) return icon;
    if (tool.d) return `https://icon.horse/icon/${encodeURIComponent(tool.d)}`;
    return tool.f || FALLBACK;
  }

  function pricingLabel(p) {
    return PRICING_LABEL[p] || "Free";
  }

  function kindLabel(t) {
    return KIND_LABEL[t] || "Website";
  }

  function toolKind(tool) {
    return tool.t || "website";
  }

  function toolMatchesPricing(tool, filter) {
    if (filter === "all") return true;
    if (filter === "free") {
      return tool.p === "free" || tool.p === "free-tier" || tool.p === "limited";
    }
    if (filter === "paid") {
      return tool.p === "paid" || tool.p === "limited" || tool.p === "free-tier";
    }
    return tool.p === filter;
  }

  function matchesPricing(tool) {
    return toolMatchesPricing(tool, pricingFilter);
  }

  function updatePricingChipCounts() {
    if (!els.chips) return;
    const keys = ["all", "free", "free-tier", "limited", "paid"];
    const counts = Object.fromEntries(keys.map((k) => [k, 0]));
    counts.all = tools.length;
    for (const tool of tools) {
      if (toolMatchesPricing(tool, "free")) counts.free += 1;
      if (toolMatchesPricing(tool, "free-tier")) counts["free-tier"] += 1;
      if (toolMatchesPricing(tool, "limited")) counts.limited += 1;
      if (toolMatchesPricing(tool, "paid")) counts.paid += 1;
    }

    keys.forEach((key) => {
      const el = els.chips.querySelector(`[data-price-count="${key}"]`);
      if (!el) return;
      const n = counts[key];
      el.textContent = n.toLocaleString();
      const btn = el.closest("[data-price]");
      if (btn) {
        const label = btn.querySelector(".home-filter-label")?.textContent || key;
        btn.setAttribute("aria-label", `${label}, ${n.toLocaleString()} tools`);
      }
    });
  }

  function matchesKind(tool) {
    if (kindFilter === "all") return true;
    return toolKind(tool) === kindFilter;
  }

  function scoreTermAgainst(term, idx) {
    if (!term || term.length < 2) return 0;
    const rooted = stem(term);

    if (idx.name === term || idx.name === rooted) return 130;
    if (idx.name.startsWith(term) || idx.name.startsWith(rooted)) return 95;
    if (idx.name.includes(term) || idx.name.includes(rooted)) return 70;

    if (
      idx.domain === term ||
      idx.domainNoTld === term ||
      idx.domain.includes(term) ||
      idx.domainNoTld.includes(term) ||
      idx.domain.includes(rooted) ||
      idx.domainNoTld.includes(rooted)
    ) {
      return 55;
    }

    if (idx.tokens.has(term) || idx.tokens.has(rooted)) return 48;
    if (idx.stems.has(rooted) || idx.stems.has(term)) return 42;

    if (idx.cat.includes(term) || idx.cat.includes(rooted)) return 34;
    if (idx.blurb.includes(term) || idx.blurb.includes(rooted)) return 28;

    // Compound domains/names: freeconvert contains convert
    if (rooted.length >= 4) {
      for (const tok of idx.tokens) {
        if (tok.length >= rooted.length && tok.includes(rooted)) return 24;
      }
      if (idx.blob.includes(rooted)) return 18;
    } else if (idx.blob.includes(term)) {
      return 14;
    }

    return 0;
  }

  function scoreTool(tool, groups) {
    if (!groups.length) {
      let score = 1;
      if (tool.s === "must-try") score += 200;
      else if (tool.s === "ai") score += 40;
      else if (tool.s === "study" || tool.s === "courses" || tool.s === "notepad") score += 30;
      else if (tool.s === "security" || tool.s === "vpn") score += 25;
      else if (tool.s === "pdf" || tool.s === "writing" || tool.s === "design") score += 20;
      else if (tool.s === "utilities" || tool.s === "github-powerhouses") score -= 5;
      // Category Top 3 float to the front when browsing a shelf
      if (tool.r === 1) score += 300;
      else if (tool.r === 2) score += 290;
      else if (tool.r === 3) score += 280;
      return score;
    }

    const idx = ensureIndex(tool);
    let score = 0;

    // AND across query words; OR across morph/synonym variants
    for (const group of groups) {
      let best = 0;
      for (const term of group) {
        best = Math.max(best, scoreTermAgainst(term, idx));
      }
      if (!best) return 0;
      score += best;
    }
    if (tool.s === "must-try") score += 8;
    if (tool.s === "notepad") score += 6;
    if (/(convert|compress|transcode)/i.test(tool.s || "") || /convert/i.test(tool.c || "")) {
      score += 4;
    }
    // Mild boost so Top 3 still surface in keyword results
    if (tool.r === 1) score += 12;
    else if (tool.r === 2) score += 8;
    else if (tool.r === 3) score += 5;
    return score;
  }

  function filteredTools() {
    const groups = termGroups(query);
    const list = [];
    for (const tool of tools) {
      if (!matchesPricing(tool)) continue;
      if (!matchesKind(tool)) continue;
      if (categoryFilter && tool.s !== categoryFilter) continue;
      const score = scoreTool(tool, groups);
      if (!score) continue;
      list.push({ tool, score });
    }
    list.sort((a, b) => {
      // Within a category view, hard-pin Top 3 order first
      if (categoryFilter && !groups.length) {
        const ar = a.tool.r || 99;
        const br = b.tool.r || 99;
        if (ar !== br) return ar - br;
      }
      return b.score - a.score || a.tool.n.localeCompare(b.tool.n);
    });
    return list.map((x) => x.tool);
  }

  function liveCategories() {
    const counts = new Map();
    for (const tool of tools) {
      if (!matchesPricing(tool)) continue;
      if (!matchesKind(tool)) continue;
      if (!tool.s) continue;
      counts.set(tool.s, (counts.get(tool.s) || 0) + 1);
    }
    return categories
      .map((c) => ({
        ...c,
        count: counts.get(c.slug) || 0,
      }))
      .filter((c) => c.count > 0);
  }

  function syncCategoryFilter(liveCats) {
    if (categoryFilter && !liveCats.some((c) => c.slug === categoryFilter)) {
      categoryFilter = "";
    }
  }

  function closeSuggestions() {
    els.suggestions.classList.remove("is-open");
    els.suggestions.innerHTML = "";
    els.input?.closest(".home-search-shell")?.classList.remove("has-suggestions");
    activeSuggest = -1;
  }

  function suggestionsWanted() {
    return (
      Boolean(query.trim()) &&
      document.activeElement === els.input
    );
  }

  function renderSuggestions(list) {
    if (!suggestionsWanted() || !list.length) {
      closeSuggestions();
      return;
    }
    const items = list.slice(0, SUGGEST_LIMIT);
    els.suggestions.innerHTML = `<ul>${items
      .map(
        (t, i) => `<li>
        <button type="button" data-idx="${i}" data-url="${escapeAttr(t.u)}">
          <img src="${escapeAttr(iconFor(t))}" alt="" loading="lazy" onerror="this.src='${FALLBACK}'">
          <span>
            <span class="s-name">${escapeHtml(t.n)}</span>
            <span class="s-meta">${escapeHtml(t.x || t.c || "")}</span>
          </span>
        </button>
      </li>`
      )
      .join("")}</ul>`;
    els.suggestions.classList.add("is-open");
    els.input?.closest(".home-search-shell")?.classList.add("has-suggestions");
    activeSuggest = -1;
  }

  function totalMatchingTools() {
    let count = 0;
    for (const tool of tools) {
      if (!matchesPricing(tool)) continue;
      if (!matchesKind(tool)) continue;
      count += 1;
    }
    return count;
  }

  function renderCategories({ animate = false } = {}) {
    const liveCats = liveCategories();
    syncCategoryFilter(liveCats);
    const slice = liveCats.slice(0, visibleCats);
    const allActive = !categoryFilter;
    const allCount = totalMatchingTools();
    const allCard = `<a class="home-cat-card home-cat-card--all${allActive ? " is-active" : ""}" href="#results" data-cat="all">
          <span class="home-cat-icon home-cat-icon--all" aria-hidden="true"></span>
          <span class="home-cat-name">All tools</span>
          <span class="home-cat-count">${allCount.toLocaleString()}</span>
        </a>`;

    els.cats.innerHTML =
      allCard +
      slice
        .map((c) => {
          const icon =
            c.icon && !/FreeUniversityTools\.png/i.test(c.icon)
              ? c.icon
              : c.domain
                ? `https://icon.horse/icon/${encodeURIComponent(c.domain)}`
                : FALLBACK;
          return `<a class="home-cat-card${categoryFilter === c.slug ? " is-active" : ""}" href="#results" data-cat="${escapeAttr(c.slug)}">
          <img class="home-cat-icon" src="${escapeAttr(icon)}" alt="" loading="lazy" onerror="this.src='${FALLBACK}'">
          <span class="home-cat-name">${escapeHtml(c.name)}</span>
          <span class="home-cat-count">${c.count.toLocaleString()}</span>
        </a>`;
        })
        .join("");

    if (animate) {
      els.cats.classList.remove("is-swapping");
      void els.cats.offsetWidth;
      els.cats.classList.add("is-swapping");
    }

    if (els.catMeta) {
      els.catMeta.textContent = `${slice.length} of ${liveCats.length}`;
    }
    if (els.catsMore) {
      els.catsMore.hidden = slice.length >= liveCats.length;
      els.catsMore.textContent =
        slice.length >= liveCats.length
          ? "All categories"
          : `Show more categories (${liveCats.length - slice.length} left)`;
    }
  }

  function moveFilterThumb(activeBtn, thumbEl, chipsEl) {
    const thumb = thumbEl || els.thumb;
    const chips = chipsEl || els.chips;
    if (!thumb || !chips || !activeBtn) return;
    const parent = chips.getBoundingClientRect();
    const btn = activeBtn.getBoundingClientRect();
    const left = btn.left - parent.left;
    thumb.style.width = `${btn.width}px`;
    thumb.style.transform = `translateX(${left}px)`;
  }

  function animateResultsSwap() {
    if (!els.results) return;
    els.results.classList.remove("is-swapping");
    // Force reflow so animation can replay
    void els.results.offsetWidth;
    els.results.classList.add("is-swapping");
  }

  function renderResults({ animate = false } = {}) {
    const list = filteredTools();
    const slice = list.slice(0, visible);
    const q = query.trim();
    const catName = categoryFilter
      ? categories.find((c) => c.slug === categoryFilter)?.name || categoryFilter
      : "";

    if (els.resultsHead) {
      els.resultsHead.textContent = q
        ? `Results for “${q}”`
        : catName
          ? catName
          : "Tools";
    }

    if (!slice.length) {
      els.results.innerHTML =
        '<div class="home-empty">No tools matched. Try a broader keyword like “pdf”, “vpn”, or “ai”.</div>';
      els.more.hidden = true;
      if (suggestionsWanted()) renderSuggestions([]);
      else closeSuggestions();
      if (animate) animateResultsSwap();
      return;
    }

    const showTopIntro = Boolean(categoryFilter && !q);
    const topCount = showTopIntro
      ? Math.min(3, slice.filter((t) => t.r === 1 || t.r === 2 || t.r === 3).length)
      : 0;

    els.results.innerHTML =
      (showTopIntro && topCount
        ? `<div class="home-top3-label">Top ${topCount} in ${escapeHtml(catName)}</div>`
        : "") +
      slice
        .map((t, idx) => {
          const rank = t.r === 1 || t.r === 2 || t.r === 3 ? t.r : 0;
          const rankBadge = rank
            ? `<span class="home-badge home-badge--rank" data-r="${rank}" title="Top ${rank} in ${escapeAttr(
                t.c || "this category"
              )}">#${rank}</span>`
            : "";
          const topClass = rank ? " is-top" : "";
          const divider =
            showTopIntro && topCount && idx === topCount
              ? `<div class="home-top3-divider">All in ${escapeHtml(catName)}</div>`
              : "";
          const kind = toolKind(t);
          const price = t.p || "free";
          return `${divider}<div class="home-result${topClass}">
        <a class="home-result-cover" href="${escapeAttr(t.u)}" target="_blank" rel="noopener noreferrer" aria-label="${escapeAttr(t.n)}"></a>
        <img src="${escapeAttr(iconFor(t))}" alt="" loading="lazy" onerror="this.src='${FALLBACK}'">
        <span class="home-result-body">
          <span class="home-result-top">
            <span class="home-result-name">${escapeHtml(t.n)}</span>
            <span class="home-badges">
              ${rankBadge}
              <a class="home-badge home-badge--kind" href="#results" data-kind="${escapeAttr(kind)}" data-t="${escapeAttr(kind)}" title="Filter: ${escapeAttr(kindLabel(kind))}">${escapeHtml(kindLabel(kind))}</a>
              <a class="home-badge home-badge--price" href="#results" data-price="${escapeAttr(price)}" data-p="${escapeAttr(price)}" title="Filter: ${escapeAttr(pricingLabel(price))}">${escapeHtml(pricingLabel(price))}</a>
            </span>
          </span>
          <span class="home-result-meta">${escapeHtml(t.x || t.c || "")}</span>
        </span>
      </div>`;
        })
        .join("");

    els.more.hidden = slice.length >= list.length;
    if (suggestionsWanted()) renderSuggestions(list);
    else closeSuggestions();
    if (animate) animateResultsSwap();
  }

  function escapeHtml(value) {
    return String(value || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function escapeAttr(value) {
    return escapeHtml(value).replace(/'/g, "&#39;");
  }

  function setQuery(next, { render = true } = {}) {
    query = next;
    els.input.value = next;
    els.clear.hidden = !next;
    visible = PAGE_SIZE;
    if (render) renderResults();
  }

  function runSearch(scroll) {
    setQuery(els.input.value);
    closeSuggestions();
    els.input.blur();
    if (scroll) {
      document.getElementById("results")?.scrollIntoView({ behavior: "smooth" });
    }
  }

  function bind() {
    const form = document.getElementById("homeSearchForm");
    const shell = els.input?.closest(".home-search-shell");

    els.input.addEventListener("input", () => {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => {
        setQuery(els.input.value);
      }, 60);
    });

    els.input.addEventListener("focus", () => {
      if (query.trim()) renderSuggestions(filteredTools());
    });

    els.input.addEventListener("blur", () => {
      // Allow suggestion click to register before closing
      setTimeout(() => {
        if (!shell?.contains(document.activeElement)) closeSuggestions();
      }, 120);
    });

    els.input.addEventListener("keydown", (e) => {
      const buttons = Array.from(
        els.suggestions.querySelectorAll("button[data-url]")
      );
      if (e.key === "ArrowDown" && buttons.length) {
        e.preventDefault();
        activeSuggest = Math.min(activeSuggest + 1, buttons.length - 1);
        buttons.forEach((b, i) => b.classList.toggle("is-active", i === activeSuggest));
      } else if (e.key === "ArrowUp" && buttons.length) {
        e.preventDefault();
        activeSuggest = Math.max(activeSuggest - 1, 0);
        buttons.forEach((b, i) => b.classList.toggle("is-active", i === activeSuggest));
      } else if (e.key === "Enter") {
        if (activeSuggest >= 0 && buttons[activeSuggest]) {
          e.preventDefault();
          window.open(buttons[activeSuggest].dataset.url, "_blank", "noopener");
          closeSuggestions();
        }
      } else if (e.key === "Escape") {
        closeSuggestions();
      }
    });

    els.clear.addEventListener("click", () => {
      setQuery("");
      closeSuggestions();
      els.input.focus();
    });

    if (form) {
      form.addEventListener("submit", (e) => {
        e.preventDefault();
        runSearch(true);
      });
    } else if (els.go) {
      els.go.addEventListener("click", () => runSearch(true));
    }

    els.suggestions.addEventListener("mousedown", (e) => {
      // Keep focus long enough for click without blur-closing first
      e.preventDefault();
    });

    els.suggestions.addEventListener("click", (e) => {
      const btn = e.target.closest("button[data-url]");
      if (!btn) return;
      window.open(btn.dataset.url, "_blank", "noopener");
      closeSuggestions();
    });

    function setPricingFilter(next) {
      pricingFilter = next || "all";
      const chip =
        els.chips?.querySelector(`[data-price="${pricingFilter}"]`) ||
        els.chips?.querySelector('[data-price="all"]');
      Array.from(els.chips?.querySelectorAll(".home-filter") || []).forEach((c) => {
        c.classList.toggle("is-active", c === chip);
      });
      if (chip) moveFilterThumb(chip, els.thumb, els.chips);
      visible = PAGE_SIZE;
      visibleCats = catPageSize();
      renderCategories({ animate: true });
      renderResults({ animate: true });
    }

    function setKindFilter(next) {
      kindFilter = next || "all";
      const chip =
        els.kindChips?.querySelector(`[data-kind="${kindFilter}"]`) ||
        els.kindChips?.querySelector('[data-kind="all"]');
      Array.from(els.kindChips?.querySelectorAll(".home-filter") || []).forEach((c) => {
        c.classList.toggle("is-active", c === chip);
      });
      if (chip) moveFilterThumb(chip, els.kindThumb, els.kindChips);
      visible = PAGE_SIZE;
      visibleCats = catPageSize();
      renderCategories({ animate: true });
      renderResults({ animate: true });
    }

    els.chips.addEventListener("click", (e) => {
      const chip = e.target.closest("[data-price]");
      if (!chip) return;
      setPricingFilter(chip.dataset.price);
    });

    if (els.kindChips) {
      els.kindChips.addEventListener("click", (e) => {
        const chip = e.target.closest("[data-kind]");
        if (!chip) return;
        setKindFilter(chip.dataset.kind);
      });
    }

    els.results.addEventListener("click", (e) => {
      const priceBadge = e.target.closest("a.home-badge[data-price]");
      if (priceBadge) {
        e.preventDefault();
        setPricingFilter(priceBadge.dataset.price);
        return;
      }
      const kindBadge = e.target.closest("a.home-badge[data-kind]");
      if (kindBadge) {
        e.preventDefault();
        setKindFilter(kindBadge.dataset.kind);
      }
    });

    els.cats.addEventListener("click", (e) => {
      const card = e.target.closest("[data-cat]");
      if (!card) return;
      e.preventDefault();
      const slug = card.dataset.cat;
      if (slug === "all") {
        categoryFilter = "";
      } else {
        categoryFilter = categoryFilter === slug ? "" : slug;
      }
      visible = PAGE_SIZE;
      renderCategories();
      renderResults({ animate: true });
      document.getElementById("results")?.scrollIntoView({ behavior: "smooth" });
    });

    if (els.catsMore) {
      els.catsMore.addEventListener("click", () => {
        const total = liveCategories().length;
        visibleCats = Math.min(visibleCats + catPageSize(), total);
        renderCategories();
      });
    }

    els.more.addEventListener("click", () => {
      visible += PAGE_SIZE;
      renderResults();
    });

    window.addEventListener("resize", () => {
      const active = els.chips?.querySelector(".home-filter.is-active");
      if (active) moveFilterThumb(active, els.thumb, els.chips);
      const kindActive = els.kindChips?.querySelector(".home-filter.is-active");
      if (kindActive) moveFilterThumb(kindActive, els.kindThumb, els.kindChips);
    });

    document.addEventListener("click", (e) => {
      if (!e.target.closest(".home-search-shell")) {
        closeSuggestions();
      }
    });

    document.addEventListener("keydown", (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        els.input.focus();
        els.input.select();
      }
    });
  }

  async function init() {
    bind();
    try {
      const [toolsRes, catsRes] = await Promise.all([
        fetch(DATA_URL),
        fetch(CATS_URL),
      ]);
      tools = await toolsRes.json();
      categories = await catsRes.json();
      // Prebuild search indexes once for fast keyword matching
      for (let i = 0; i < tools.length; i += 1) ensureIndex(tools[i]);
      els.loading.hidden = true;
      updatePricingChipCounts();
      renderCategories();
      renderResults();
      requestAnimationFrame(() => {
        const active = els.chips?.querySelector(".home-filter.is-active");
        if (active) moveFilterThumb(active, els.thumb, els.chips);
        const kindActive = els.kindChips?.querySelector(".home-filter.is-active");
        if (kindActive) moveFilterThumb(kindActive, els.kindThumb, els.kindChips);
      });
    } catch (err) {
      els.loading.textContent =
        "Could not load tools index. Open this site via a local server or check data/scroll-tools.json.";
      console.error(err);
    }
  }

  init();
})();
