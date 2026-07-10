(function () {
  const INITIAL_COUNT = 8;
  const ROOT_MARGIN = "480px 0px 640px 0px";

  const directory = document.querySelector(".tools-directory");
  if (!directory) return;

  const sections = Array.from(directory.querySelectorAll(".tool-category"));
  const cache = new Map();
  const loaded = new Set();
  const entryByKey = new Map();
  const searchIndex = [];

  let scrollObserver = null;
  const loadQueue = [];
  let loadScheduled = false;
  let loading = false;

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

  function linkKey(link) {
    const name =
      link.querySelector(".tool-link-name")?.textContent?.trim() || "";
    const href = link.getAttribute("href") || "";
    return `${href}|${name}`;
  }

  function buildMetadataEntry(link, section) {
    const name =
      link.querySelector(".tool-link-name")?.textContent?.trim() || "";
    const categorySlug = section.dataset.category || "";
    const categoryTitle =
      section.querySelector(".category-title")?.textContent?.trim() || "";
    const href = link.getAttribute("href") || "";
    const domain = extractDomain(href);
    const pricing = link.dataset.pricing || "free";

    const nameNorm = normalizeSearchText(name);
    const categoryNorm = normalizeSearchText(
      [categoryTitle, categorySlug.replace(/-/g, " ")].join(" "),
    );
    const domainNorm = normalizeSearchText(domain.replace(/\./g, " "));
    const fullText = normalizeSearchText(
      [name, categoryTitle, categorySlug, domain].join(" "),
    );

    return {
      el: link,
      name,
      nameNorm,
      categorySlug,
      categoryNorm,
      domain,
      domainNorm,
      fullText,
      keywordNorm: "",
      pricing,
      section,
      linkKey: linkKey(link),
    };
  }

  function captureSectionEntries(section) {
    section.querySelectorAll(".tool-link").forEach((link) => {
      const entry = buildMetadataEntry(link, section);
      searchIndex.push(entry);
      entryByKey.set(entry.linkKey, entry);
    });
  }

  function deferSection(section) {
    const slug = section.dataset.category;
    const tools = section.querySelector(".category-tools");
    if (!slug || !tools) return;

    cache.set(slug, tools.innerHTML);
    tools.innerHTML = "";
    section.classList.add("is-deferred");
    section.dataset.deferred = "true";

    searchIndex.forEach((entry) => {
      if (entry.section === section) entry.el = null;
    });
  }

  function bindLoadedLinks(section) {
    section.querySelectorAll(".tool-link").forEach((link) => {
      const key = linkKey(link);
      const entry = entryByKey.get(key);
      if (entry) entry.el = link;
    });
  }

  function notifyCategoryLoaded(section, slug, immediate) {
    const run = () => {
      window.dispatchEvent(
        new CustomEvent("fut:category-loaded", {
          detail: { section, slug },
        }),
      );
    };

    if (immediate) {
      run();
      return;
    }

    if ("requestIdleCallback" in window) {
      window.requestIdleCallback(run, { timeout: 250 });
    } else {
      window.setTimeout(run, 0);
    }
  }

  function loadCategory(section, options = {}) {
    const slug = section.dataset.category;
    if (!slug || loaded.has(slug)) {
      return false;
    }

    const tools = section.querySelector(".category-tools");
    const html = cache.get(slug);
    if (!tools || html == null) return false;

    tools.innerHTML = html;
    section.classList.remove("is-deferred", "is-loading");
    section.removeAttribute("data-deferred");
    loaded.add(slug);

    bindLoadedLinks(section);

    if (scrollObserver) scrollObserver.unobserve(section);

    notifyCategoryLoaded(section, slug, Boolean(options.immediate));
    return true;
  }

  function getSectionBySlug(slug) {
    return sections.find((section) => section.dataset.category === slug) || null;
  }

  function ensureCategory(slug, options = {}) {
    const section = getSectionBySlug(slug);
    if (!section) return false;
    return loadCategory(section, options);
  }

  /** Load target + every deferred category before it so scroll positions stay stable. */
  function ensureCategoryPath(slug) {
    const targetIndex = sections.findIndex(
      (section) => section.dataset.category === slug,
    );
    if (targetIndex < 0) return false;

    let loadedAny = false;
    for (let i = 0; i <= targetIndex; i += 1) {
      const section = sections[i];
      if (!section.classList.contains("is-deferred")) continue;
      if (loadCategory(section, { immediate: true })) loadedAny = true;
    }
    return loadedAny;
  }

  function queueDeferredSections(targetSections) {
    targetSections.forEach((section) => {
      if (
        section.classList.contains("is-deferred") &&
        !loadQueue.includes(section)
      ) {
        loadQueue.push(section);
      }
    });
    scheduleLoadDrain();
  }

  function scheduleLoadDrain() {
    if (loadScheduled || loadQueue.length === 0) return;
    loadScheduled = true;
    requestAnimationFrame(drainLoadQueue);
  }

  function drainLoadQueue() {
    loadScheduled = false;
    if (loading || loadQueue.length === 0) return;

    loading = true;
    const section = loadQueue.shift();
    loadCategory(section);
    loading = false;

    if (loadQueue.length > 0) {
      scheduleLoadDrain();
    }
  }

  function loadAllDeferred() {
    queueDeferredSections(
      sections.filter((section) => section.classList.contains("is-deferred")),
    );
  }

  function setupScrollObserver() {
    scrollObserver = new IntersectionObserver(
      (entries) => {
        const pending = entries
          .filter((entry) => entry.isIntersecting)
          .map((entry) => entry.target);
        if (pending.length === 0) return;
        queueDeferredSections(pending);
      },
      { root: null, rootMargin: ROOT_MARGIN, threshold: 0 },
    );

    sections.forEach((section, index) => {
      if (index >= INITIAL_COUNT) {
        scrollObserver.observe(section);
      }
    });
  }

  sections.forEach((section, index) => {
    captureSectionEntries(section);
    if (index >= INITIAL_COUNT) {
      deferSection(section);
    } else {
      loaded.add(section.dataset.category || String(index));
    }
  });

  setupScrollObserver();

  function handleInitialHash() {
    const hash = window.location.hash.slice(1);
    if (!hash.startsWith("category-")) return;
    const slug = hash.slice("category-".length);
    ensureCategoryPath(slug);
    const section = getSectionBySlug(slug);
    if (!section) return;

    const scrollToHash = () => {
      const headerEl = document.getElementById("header");
      const offset = headerEl
        ? Math.max(72, Math.ceil(headerEl.getBoundingClientRect().height) + 12)
        : 72;
      const y = section.getBoundingClientRect().top + window.scrollY - offset;
      window.scrollTo({ top: Math.max(0, y), left: 0, behavior: "auto" });
    };

    requestAnimationFrame(() => {
      scrollToHash();
      window.setTimeout(scrollToHash, 50);
      window.setTimeout(scrollToHash, 150);
      window.setTimeout(scrollToHash, 320);
    });
  }

  handleInitialHash();
  window.addEventListener("hashchange", handleInitialHash);

  window.FUTCategoryLoader = {
    sections,
    searchIndex,
    loaded,
    loadCategory,
    ensureCategory,
    ensureCategoryPath,
    loadAllDeferred,
    isDeferred(section) {
      return section.classList.contains("is-deferred");
    },
    isLoaded(slug) {
      return loaded.has(slug);
    },
  };
})();
