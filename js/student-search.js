(function () {
  const SYNONYMS = {
    ai: ["artificial intelligence", "llm", "gpt", "chatbot", "machine learning"],
    ml: ["machine learning", "ai"],
    pdf: ["document", "acrobat"],
    vpn: ["virtual private network", "privacy"],
    notes: ["notetaking", "note taking", "notebook"],
    deploy: ["deployment", "hosting", "vercel", "netlify"],
    deployment: ["deploy", "hosting", "ci cd"],
    devops: ["docker", "kubernetes", "container"],
    osint: ["open source intelligence", "investigation"],
    study: ["learning", "homework", "exam", "flashcards"],
    video: ["movie", "stream", "youtube"],
    image: ["photo", "picture", "png", "jpg"],
    code: ["programming", "developer", "ide"],
    math: ["mathematics", "calculator", "algebra"],
    write: ["writing", "essay", "grammar"],
    design: ["ui", "figma", "canva", "graphics"],
    email: ["mail", "inbox"],
    free: ["gratis", "no cost"],
    torrent: ["magnet", "p2p"],
    torrents: ["magnet", "p2p"],
  };

  const RECENT_KEY = "fut-recent-searches";
  const MAX_RECENT = 6;
  const SUGGEST_LIMIT = 8;
  const DEBOUNCE_MS = 60;

  let toolLinks = [];
  let categorySections = [];
  let categoryKeywords = {};
  let getMode = () => "free";
  let matchesPricingMode = () => true;
  let onFilterComplete = () => {};
  let searchInput = null;
  let searchIndex = [];
  let debounceTimer = null;
  let activeSuggestion = -1;
  let ui = {};

  function normalizeSearchText(value) {
    return (value || "")
      .toLowerCase()
      .replace(/[''`]/g, "")
      .replace(/[^a-z0-9]+/g, " ")
      .trim();
  }

  function extractDomain(href) {
    try {
      const host = new URL(href, window.location.href).hostname;
      return host.replace(/^www\./, "");
    } catch {
      return "";
    }
  }

  function expandTerms(terms) {
    const expanded = new Set();
    terms.forEach((term) => {
      const norm = normalizeSearchText(term);
      if (!norm) return;
      expanded.add(norm);
      const syns = SYNONYMS[norm];
      if (syns) {
        syns.forEach((s) => expanded.add(normalizeSearchText(s)));
      }
    });
    return Array.from(expanded);
  }

  function levenshtein(a, b) {
    if (a === b) return 0;
    if (!a.length) return b.length;
    if (!b.length) return a.length;
    const row = Array.from({ length: b.length + 1 }, (_, i) => i);
    for (let i = 1; i <= a.length; i += 1) {
      let prev = i;
      for (let j = 1; j <= b.length; j += 1) {
        const cost = a[i - 1] === b[j - 1] ? 0 : 1;
        const next = Math.min(row[j] + 1, prev + 1, row[j - 1] + cost);
        row[j - 1] = prev;
        prev = next;
      }
      row[b.length] = prev;
    }
    return row[b.length];
  }

  function termMatchesInText(text, term) {
    if (!term) return true;
    if (text.includes(term)) return true;
    if (term.length < 4) return false;
    return text.split(" ").some((word) => {
      if (word.length < 3) return false;
      return levenshtein(word, term) <= 1;
    });
  }

  function tokenizeQuery(raw) {
    const tokens = [];
    const input = (raw || "").trim();
    let i = 0;
    while (i < input.length) {
      if (input[i] === '"') {
        const end = input.indexOf('"', i + 1);
        if (end > i) {
          tokens.push({ type: "phrase", value: input.slice(i + 1, end) });
          i = end + 1;
          continue;
        }
      }
      if (/\s/.test(input[i])) {
        i += 1;
        continue;
      }
      let j = i;
      while (j < input.length && !/\s/.test(input[j])) j += 1;
      tokens.push({ type: "word", value: input.slice(i, j) });
      i = j;
    }
    return tokens;
  }

  function parseQuery(raw) {
    const result = {
      raw: (raw || "").trim(),
      must: [],
      mustNot: [],
      phrases: [],
      category: null,
      domain: null,
      pricing: null,
    };

    tokenizeQuery(raw).forEach((token) => {
      if (token.type === "phrase") {
        const phrase = normalizeSearchText(token.value);
        if (phrase) result.phrases.push(phrase);
        return;
      }

      const word = token.value;
      const lower = word.toLowerCase();
      const colon = lower.indexOf(":");

      if (colon > 0) {
        const key = lower.slice(0, colon);
        const val = normalizeSearchText(word.slice(colon + 1));
        if ((key === "cat" || key === "category") && val) {
          result.category = val;
          return;
        }
        if (key === "domain" && val) {
          result.domain = val;
          return;
        }
        if (key === "pricing" && val) {
          result.pricing = val;
          return;
        }
      }

      if (lower === "free" || lower === "paid" || lower === "tier" || lower === "limited") {
        result.pricing = lower === "tier" ? "free-tier" : lower;
        return;
      }

      if (word.startsWith("-") && word.length > 1) {
        const excluded = normalizeSearchText(word.slice(1));
        if (excluded) result.mustNot.push(excluded);
        return;
      }

      const norm = normalizeSearchText(word);
      if (norm) result.must.push(norm);
    });

    result.must = expandTerms(result.must);
    return result;
  }

  function buildIndexEntry(linkEl) {
    const name =
      linkEl.querySelector(".tool-link-name")?.textContent?.trim() || "";
    const section = linkEl.closest(".tool-category");
    const categorySlug = section?.dataset?.category || "";
    const categoryTitle =
      section?.querySelector(".category-title")?.textContent?.trim() || "";
    const href = linkEl.getAttribute("href") || "";
    const domain = extractDomain(href);
    const pricing = linkEl.dataset.pricing || "free";
    const keywords = (categoryKeywords[categorySlug] || []).join(" ");

    const nameNorm = normalizeSearchText(name);
    const categoryNorm = normalizeSearchText(
      [categoryTitle, categorySlug.replace(/-/g, " ")].join(" "),
    );
    const domainNorm = normalizeSearchText(domain.replace(/\./g, " "));
    const keywordNorm = normalizeSearchText(keywords);
    const fullText = normalizeSearchText(
      [name, categoryTitle, categorySlug, domain, keywords].join(" "),
    );

    const nameEl = linkEl.querySelector(".tool-link-name");
    if (nameEl && !nameEl.dataset.searchOriginal) {
      nameEl.dataset.searchOriginal = name;
    }

    return {
      el: linkEl,
      name,
      nameNorm,
      categorySlug,
      categoryNorm,
      domain,
      domainNorm,
      fullText,
      keywordNorm,
      pricing,
      section,
    };
  }

  function scoreEntry(entry, parsed) {
    if (!parsed.raw) return 1;

    if (parsed.category) {
      const cat = parsed.category;
      const slug = normalizeSearchText(entry.categorySlug.replace(/-/g, " "));
      if (!slug.includes(cat) && !entry.categoryNorm.includes(cat)) {
        return -1;
      }
    }

    if (parsed.domain) {
      if (
        !entry.domainNorm.includes(parsed.domain) &&
        !entry.domain.includes(parsed.domain)
      ) {
        return -1;
      }
    }

    if (parsed.pricing && entry.pricing !== parsed.pricing) {
      if (parsed.pricing === "free" && entry.pricing !== "free") return -1;
      if (parsed.pricing === "paid" && entry.pricing === "free") return -1;
    }

    for (const phrase of parsed.phrases) {
      if (!entry.fullText.includes(phrase)) return -1;
    }

    for (const term of parsed.mustNot) {
      if (entry.fullText.includes(term)) return -1;
    }

    let score = 0;

    for (const term of parsed.must) {
      let matched = false;
      if (entry.nameNorm === term) {
        score += 200;
        matched = true;
      } else if (entry.nameNorm.startsWith(term)) {
        score += 140;
        matched = true;
      } else if (entry.nameNorm.includes(term)) {
        score += 100;
        matched = true;
      } else if (entry.domainNorm.includes(term) || entry.domain.includes(term)) {
        score += 80;
        matched = true;
      } else if (entry.categoryNorm.includes(term)) {
        score += 50;
        matched = true;
      } else if (entry.keywordNorm.includes(term)) {
        score += 35;
        matched = true;
      } else if (termMatchesInText(entry.fullText, term)) {
        score += 20;
        matched = true;
      }
      if (!matched) return -1;
    }

    if (parsed.must.length === 0 && parsed.phrases.length === 0) {
      if (parsed.category || parsed.domain || parsed.pricing) {
        score = 10;
      }
    }

    return score;
  }

  function escapeHtml(value) {
    return value
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function highlightName(entry, parsed) {
    const nameEl = entry.el.querySelector(".tool-link-name");
    if (!nameEl) return;
    const original = nameEl.dataset.searchOriginal || entry.name;
    if (!parsed.raw) {
      nameEl.textContent = original;
      return;
    }

    const terms = [
      ...parsed.phrases,
      ...parsed.must.filter((t) => t.length >= 2),
    ];
    if (terms.length === 0) {
      nameEl.textContent = original;
      return;
    }

    let html = escapeHtml(original);
    const sorted = [...terms].sort((a, b) => b.length - a.length);
    sorted.forEach((term) => {
      if (term.length < 2) return;
      const pattern = new RegExp(
        `(${term.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")})`,
        "gi",
      );
      html = html.replace(pattern, "<mark class=\"search-hit\">$1</mark>");
    });
    nameEl.innerHTML = html;
  }

  function clearHighlights() {
    searchIndex.forEach((entry) => {
      const nameEl = entry.el.querySelector(".tool-link-name");
      if (!nameEl) return;
      const original = nameEl.dataset.searchOriginal || entry.name;
      nameEl.textContent = original;
    });
  }

  function getRecentSearches() {
    try {
      const raw = localStorage.getItem(RECENT_KEY);
      const list = raw ? JSON.parse(raw) : [];
      return Array.isArray(list) ? list.slice(0, MAX_RECENT) : [];
    } catch {
      return [];
    }
  }

  function saveRecentSearch(query) {
    const trimmed = (query || "").trim();
    if (trimmed.length < 2) return;
    const recent = getRecentSearches().filter((q) => q !== trimmed);
    recent.unshift(trimmed);
    try {
      localStorage.setItem(
        RECENT_KEY,
        JSON.stringify(recent.slice(0, MAX_RECENT)),
      );
    } catch {
      /* ignore */
    }
  }

  function syncUrlQuery(query) {
    const url = new URL(window.location.href);
    if (query) {
      url.searchParams.set("q", query);
    } else {
      url.searchParams.delete("q");
    }
    window.history.replaceState({}, "", url);
  }

  function getSuggestions(parsed) {
    if (!parsed.raw) {
      return getRecentSearches().map((q) => ({
        type: "recent",
        label: q,
        query: q,
        score: 0,
      }));
    }

    const scored = [];
    const seen = new Set();

    searchIndex.forEach((entry) => {
      const score = scoreEntry(entry, parsed);
      if (score < 0) return;
      const key = entry.name;
      if (seen.has(key)) return;
      seen.add(key);
      scored.push({
        type: "tool",
        label: entry.name,
        sub: entry.categoryNorm,
        query: entry.name,
        score,
        entry,
      });
    });

    scored.sort((a, b) => b.score - a.score);
    return scored.slice(0, SUGGEST_LIMIT);
  }

  function positionSuggestions() {
    if (!ui.suggestions || !searchInput || ui.suggestions.hidden) return;
    const rect = searchInput.getBoundingClientRect();
    const isMobile = window.matchMedia("(max-width: 768px)").matches;
    if (isMobile) {
      ui.suggestions.style.top = `${rect.bottom + 6}px`;
      ui.suggestions.style.left = "12px";
      ui.suggestions.style.right = "12px";
    } else {
      ui.suggestions.style.top = "";
      ui.suggestions.style.left = "";
      ui.suggestions.style.right = "";
    }
  }

  function renderSuggestions(items) {
    if (!ui.suggestions) return;
    ui.suggestions.innerHTML = "";

    if (items.length === 0) {
      ui.suggestions.hidden = true;
      return;
    }

    const list = document.createElement("ul");
    list.className = "search-suggestions-list";
    list.setAttribute("role", "listbox");

    items.forEach((item, index) => {
      const li = document.createElement("li");
      li.className = "search-suggestion";
      li.setAttribute("role", "option");
      li.dataset.index = String(index);
      if (index === activeSuggestion) {
        li.classList.add("is-active");
        li.setAttribute("aria-selected", "true");
      }

      if (item.type === "recent") {
        li.innerHTML =
          '<span class="search-suggestion-tag">Recent</span>' +
          `<span class="search-suggestion-label">${escapeHtml(item.label)}</span>`;
      } else {
        li.innerHTML =
          `<span class="search-suggestion-label">${escapeHtml(item.label)}</span>` +
          `<span class="search-suggestion-sub">${escapeHtml(item.sub || "")}</span>`;
      }

      li.addEventListener("mousedown", (e) => {
        e.preventDefault();
        setQuery(item.query, true);
        hideSuggestions();
        searchInput?.blur();
      });

      list.appendChild(li);
    });

    ui.suggestions.appendChild(list);
    ui.suggestions.hidden = false;
    positionSuggestions();
  }

  function hideSuggestions() {
    activeSuggestion = -1;
    if (ui.suggestions) {
      ui.suggestions.hidden = true;
      ui.suggestions.innerHTML = "";
    }
  }

  function updateSearchStatus(visibleCount, parsed) {
    if (!ui.status || !ui.statusText) return;

    if (!parsed.raw) {
      ui.status.hidden = true;
      ui.statusText.textContent = "";
      return;
    }

    ui.status.hidden = false;
    if (visibleCount === 0) {
      ui.statusText.textContent = `No tools found for "${parsed.raw}"`;
      ui.status.classList.add("is-empty");
    } else {
      ui.statusText.textContent = `${visibleCount} tool${visibleCount === 1 ? "" : "s"} found`;
      ui.status.classList.remove("is-empty");
    }
  }

  function updateEmptyState(visibleCount, parsed) {
    if (!ui.empty) return;
    const show = Boolean(parsed.raw) && visibleCount === 0;
    ui.empty.hidden = !show;
    if (show && ui.emptyHint) {
      ui.emptyHint.textContent =
        'Try broader terms, synonyms like "ai" or "deploy", or filters like category:pdf or domain:github.com';
    }
  }

  function applyFilters() {
    const parsed = parseQuery(searchInput?.value || "");
    const mode = getMode();
    let visibleCount = 0;
    const sectionScores = new Map();
    const sectionsToLoad = new Set();
    const eagerLoad =
      window.FUTCategoryLoader && (Boolean(parsed.raw) || mode === "paid");

    if (eagerLoad) {
      searchIndex.forEach((entry) => {
        const score = scoreEntry(entry, parsed);
        const matchesQuery = score >= 0;
        const matchesMode = matchesPricingMode(entry.pricing, mode);
        if (matchesQuery && matchesMode) {
          sectionsToLoad.add(entry.section);
        }
      });
      sectionsToLoad.forEach((section) => {
        window.FUTCategoryLoader.loadCategory(section);
      });
    }

    searchIndex.forEach((entry) => {
      const score = scoreEntry(entry, parsed);
      const matchesQuery = score >= 0;
      const matchesMode = matchesPricingMode(entry.pricing, mode);
      const show = matchesQuery && matchesMode;

      if (entry.el) {
        entry.el.style.display = show ? "" : "none";
        entry.el.style.order = show && parsed.raw ? String(1000 - score) : "";

        if (show) {
          visibleCount += 1;
          highlightName(entry, parsed);
          const prev = sectionScores.get(entry.section) || 0;
          sectionScores.set(entry.section, Math.max(prev, score));
        } else {
          const nameEl = entry.el.querySelector(".tool-link-name");
          if (nameEl) {
            nameEl.textContent = nameEl.dataset.searchOriginal || entry.name;
          }
        }
      } else if (show) {
        visibleCount += 1;
        const prev = sectionScores.get(entry.section) || 0;
        sectionScores.set(entry.section, Math.max(prev, score));
      }
    });

    categorySections.forEach((section) => {
      const sectionEntries = searchIndex.filter(
        (entry) => entry.section === section,
      );
      const anyVisible = sectionEntries.some((entry) => {
        const score = scoreEntry(entry, parsed);
        const matchesQuery = score >= 0;
        const matchesMode = matchesPricingMode(entry.pricing, mode);
        return matchesQuery && matchesMode;
      });

      section.classList.toggle("is-hidden", !anyVisible);
      section.classList.toggle("is-search-active", Boolean(parsed.raw));

      if (parsed.raw && anyVisible) {
        const score = sectionScores.get(section) || 0;
        section.style.order = String(1000 - score);
      } else {
        section.style.order = "";
      }
    });

    if (toolsDirectory) {
      toolsDirectory.classList.toggle("has-search-query", Boolean(parsed.raw));
    }

    updateSearchStatus(visibleCount, parsed);
    updateEmptyState(visibleCount, parsed);
    syncUrlQuery(parsed.raw);
    onFilterComplete();

    return { visibleCount, parsed };
  }

  function scheduleFilter() {
    window.clearTimeout(debounceTimer);
    debounceTimer = window.setTimeout(() => {
      const result = applyFilters();
      if (document.activeElement === searchInput) {
        renderSuggestions(getSuggestions(result.parsed));
      }
    }, DEBOUNCE_MS);
  }

  function setQuery(value, runNow) {
    if (!searchInput) return;
    searchInput.value = value;
    if (runNow) {
      applyFilters();
      saveRecentSearch(value);
    } else {
      scheduleFilter();
    }
  }

  function getSearchPlaceholder() {
    return window.matchMedia("(max-width: 768px)").matches
      ? "Search tools…"
      : "Search tools, domains, categories…  (/ or Ctrl+K)";
  }

  function buildSearchUi() {
    const wrap = searchInput?.closest(".header-search-wrap");
    if (!wrap || !searchInput) return;

    searchInput.setAttribute("placeholder", getSearchPlaceholder());
    searchInput.setAttribute("autocomplete", "off");
    searchInput.setAttribute("spellcheck", "false");
    searchInput.setAttribute(
      "aria-describedby",
      "searchStatusText searchSuggestions",
    );

    const clearBtn = document.createElement("button");
    clearBtn.type = "button";
    clearBtn.className = "search-clear-btn";
    clearBtn.hidden = true;
    clearBtn.setAttribute("aria-label", "Clear search");
    clearBtn.innerHTML =
      '<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>';
    wrap.appendChild(clearBtn);

    const kbd = document.createElement("kbd");
    kbd.className = "search-kbd-hint";
    kbd.textContent = "/";
    wrap.appendChild(kbd);

    const suggestions = document.createElement("div");
    suggestions.id = "searchSuggestions";
    suggestions.className = "search-suggestions";
    suggestions.hidden = true;
    suggestions.setAttribute("role", "listbox");
    suggestions.setAttribute("aria-label", "Search suggestions");
    wrap.appendChild(suggestions);

    const status = document.createElement("div");
    status.id = "searchStatus";
    status.className = "search-status";
    status.hidden = true;
    status.setAttribute("aria-live", "polite");
    const statusText = document.createElement("span");
    statusText.id = "searchStatusText";
    status.appendChild(statusText);

    const directory = document.querySelector(".tools-directory");
    const contentContainer = directory?.closest(".content-container");

    const empty = document.createElement("div");
    empty.id = "searchEmpty";
    empty.className = "search-empty";
    empty.hidden = true;
    empty.innerHTML =
      '<p class="search-empty-title">No matching tools</p>' +
      '<p class="search-empty-hint" id="searchEmptyHint"></p>' +
      '<button type="button" class="search-empty-clear">Clear search</button>';
    if (directory) {
      directory.parentElement?.insertBefore(empty, directory);
    }
    if (contentContainer && directory) {
      contentContainer.insertBefore(status, directory);
    }

    ui = {
      wrap,
      clearBtn,
      kbd,
      suggestions,
      status,
      statusText,
      empty,
      emptyHint: empty.querySelector("#searchEmptyHint"),
      emptyClear: empty.querySelector(".search-empty-clear"),
    };

    clearBtn.addEventListener("click", () => {
      setQuery("", true);
      hideSuggestions();
      searchInput.focus();
    });

    ui.emptyClear?.addEventListener("click", () => {
      setQuery("", true);
      searchInput?.focus();
    });

    searchInput.addEventListener("input", () => {
      ui.clearBtn.hidden = !searchInput.value;
      ui.kbd.hidden = Boolean(searchInput.value);
      scheduleFilter();
    });

    searchInput.addEventListener("search", () => {
      applyFilters();
      saveRecentSearch(searchInput.value);
    });

    searchInput.addEventListener("focus", () => {
      const parsed = parseQuery(searchInput.value);
      renderSuggestions(getSuggestions(parsed));
      positionSuggestions();
    });

    searchInput.addEventListener("blur", () => {
      window.setTimeout(hideSuggestions, 120);
      if (searchInput.value.trim()) {
        saveRecentSearch(searchInput.value);
      }
    });

    searchInput.addEventListener("keydown", (e) => {
      const items = ui.suggestions?.querySelectorAll(".search-suggestion");
      if (!items || items.length === 0 || ui.suggestions.hidden) {
        if (e.key === "Escape") {
          if (searchInput.value) {
            setQuery("", true);
          } else {
            searchInput.blur();
          }
        }
        return;
      }

      if (e.key === "ArrowDown") {
        e.preventDefault();
        activeSuggestion = Math.min(activeSuggestion + 1, items.length - 1);
        renderSuggestions(getSuggestions(parseQuery(searchInput.value)));
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        activeSuggestion = Math.max(activeSuggestion - 1, 0);
        renderSuggestions(getSuggestions(parseQuery(searchInput.value)));
      } else if (e.key === "Enter" && activeSuggestion >= 0) {
        e.preventDefault();
        const parsed = parseQuery(searchInput.value);
        const suggestions = getSuggestions(parsed);
        const pick = suggestions[activeSuggestion];
        if (pick) {
          setQuery(pick.query, true);
          hideSuggestions();
        }
      } else if (e.key === "Escape") {
        hideSuggestions();
        if (searchInput.value) {
          setQuery("", true);
        }
      }
    });

    document.addEventListener("keydown", (e) => {
      const tag = (e.target?.tagName || "").toLowerCase();
      const inField =
        tag === "input" ||
        tag === "textarea" ||
        tag === "select" ||
        e.target?.isContentEditable;

      if (inField) return;

      if (e.key === "/" || ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k")) {
        e.preventDefault();
        searchInput.focus();
        searchInput.select();
      }
    });

    window.addEventListener(
      "resize",
      () => {
        searchInput.setAttribute("placeholder", getSearchPlaceholder());
        positionSuggestions();
      },
      { passive: true },
    );
  }

  let toolsDirectory = null;

  function enrichSearchIndex() {
    searchIndex.forEach((entry) => {
      const keywords = (categoryKeywords[entry.categorySlug] || []).join(" ");
      entry.keywordNorm = normalizeSearchText(keywords);
      entry.fullText = normalizeSearchText(
        [
          entry.name,
          entry.categoryNorm,
          entry.categorySlug,
          entry.domain,
          keywords,
        ].join(" "),
      );
      if (entry.el) {
        const nameEl = entry.el.querySelector(".tool-link-name");
        if (nameEl && !nameEl.dataset.searchOriginal) {
          nameEl.dataset.searchOriginal = entry.name;
        }
      }
    });
  }

  window.FUTStudentSearch = {
    init(options) {
      searchInput = options.input;
      categorySections =
        options.categorySections ||
        window.FUTCategoryLoader?.sections ||
        [];
      categoryKeywords = options.categoryKeywords || {};
      getMode = options.getMode || getMode;
      matchesPricingMode = options.matchesPricingMode || matchesPricingMode;
      onFilterComplete = options.onFilterComplete || onFilterComplete;
      toolsDirectory = document.querySelector(".tools-directory");

      if (options.searchIndex?.length) {
        searchIndex = options.searchIndex;
      } else {
        toolLinks = options.toolLinks || [];
        searchIndex = toolLinks.map(buildIndexEntry);
      }

      enrichSearchIndex();
      buildSearchUi();

      const urlQuery = new URLSearchParams(window.location.search).get("q");
      if (urlQuery) {
        searchInput.value = urlQuery;
        if (ui.clearBtn) ui.clearBtn.hidden = false;
        if (ui.kbd) ui.kbd.hidden = true;
      }

      applyFilters();
    },

    applyFilters,
    parseQuery,
    getQuery() {
      return searchInput?.value || "";
    },
    setQuery,
    clearHighlights,
  };
})();
