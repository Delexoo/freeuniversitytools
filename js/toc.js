(function () {
  const toc = document.getElementById("pageToc");
  const toggle = document.getElementById("pageTocToggle");
  const header = document.getElementById("pageTocHeader");
  const panel = document.getElementById("pageTocPanel");
  const backdrop = document.getElementById("pageTocBackdrop");
  const meta = document.getElementById("pageTocMeta");
  const list = document.getElementById("pageTocList");
  const directory = document.querySelector(".tools-directory");

  if (!toc || !toggle || !panel || !list || !directory) return;

  const HEADER_OFFSET = 72;
  const FEATURED = new Set(["must-try", "github-powerhouses"]);
  const DESKTOP_MQ = window.matchMedia("(min-width: 1024px)");

  let sections = [];
  let links = [];
  let spyObserver = null;
  let panelExpanded = DESKTOP_MQ.matches;
  let pendingScrollId = null;
  let pendingScrollTimers = [];
  let pendingScrollFrame = 0;

  function isDesktop() {
    return DESKTOP_MQ.matches;
  }

  function setPanelExpanded(expanded) {
    panelExpanded = expanded;
    toggle.setAttribute("aria-expanded", expanded ? "true" : "false");
    if (header) header.setAttribute("aria-expanded", expanded ? "true" : "false");
    toc.classList.toggle("is-expanded", expanded);

    if (isDesktop()) {
      toc.classList.add("is-desktop");
      toc.classList.remove("is-open");
      panel.hidden = false;
      if (backdrop) backdrop.hidden = true;
      return;
    }

    toc.classList.remove("is-desktop");
    panel.hidden = false;
    toc.classList.toggle("is-open", expanded);
    if (backdrop) backdrop.hidden = !expanded;
  }

  function syncLayout() {
    setPanelExpanded(panelExpanded);
  }

  function ensureSectionId(section) {
    const slug = section.dataset.category;
    if (!slug) return null;
    const id = `category-${slug}`;
    section.id = id;
    return id;
  }

  function updateMeta(showAll) {
    if (!meta) return;
    const count = showAll
      ? links.length
      : links.filter(
          ({ section }) => !section.classList.contains("is-hidden"),
        ).length;
    meta.textContent = count > 0 ? `${count} sections` : "";
  }

  function clearPendingScrollWork() {
    if (pendingScrollFrame) {
      cancelAnimationFrame(pendingScrollFrame);
      pendingScrollFrame = 0;
    }
    pendingScrollTimers.forEach((id) => window.clearTimeout(id));
    pendingScrollTimers = [];
  }

  function getHeaderOffset() {
    const headerEl = document.getElementById("header");
    if (!headerEl) return HEADER_OFFSET;
    return Math.max(HEADER_OFFSET, Math.ceil(headerEl.getBoundingClientRect().height) + 12);
  }

  function scrollToCategory(id, options = {}) {
    const target = document.getElementById(id);
    if (!target) return;

    pendingScrollId = id;
    clearPendingScrollWork();

    const runScroll = (behavior) => {
      const el = document.getElementById(id);
      if (!el || pendingScrollId !== id) return;
      const y =
        el.getBoundingClientRect().top + window.scrollY - getHeaderOffset();
      window.scrollTo({
        top: Math.max(0, y),
        left: 0,
        behavior: behavior || "auto",
      });
    };

    // Instant jump after layout settles — smooth scroll fights expanding sections
    const settleAndScroll = () => {
      pendingScrollFrame = requestAnimationFrame(() => {
        runScroll("auto");
        pendingScrollFrame = requestAnimationFrame(() => {
          runScroll("auto");
          pendingScrollFrame = 0;
        });
      });

      pendingScrollTimers.push(window.setTimeout(() => runScroll("auto"), 50));
      pendingScrollTimers.push(window.setTimeout(() => runScroll("auto"), 150));
      pendingScrollTimers.push(
        window.setTimeout(() => {
          runScroll("auto");
          if (pendingScrollId === id) pendingScrollId = null;
        }, 320),
      );
    };

    if (options.waitForLoad) {
      // Path already loaded synchronously; wait for collapse/pricing layout
      settleAndScroll();
      return;
    }

    settleAndScroll();
  }

  function buildList() {
    list.innerHTML = "";
    links = [];

    sections = Array.from(directory.querySelectorAll(".tool-category"));
    sections.forEach((section) => {
      const slug = section.dataset.category;
      const titleEl = section.querySelector(".category-title");
      if (!slug || !titleEl) return;

      const id = ensureSectionId(section);
      const li = document.createElement("li");
      li.className = "page-toc-item";
      if (FEATURED.has(slug)) li.classList.add("page-toc-item--featured");
      li.dataset.category = slug;

      const a = document.createElement("a");
      a.className = "page-toc-link";
      a.href = `#${id}`;
      a.textContent = titleEl.textContent.trim();
      a.addEventListener("click", (event) => {
        event.preventDefault();
        if (
          window.FUTStudentSearch &&
          window.FUTStudentSearch.getQuery().trim()
        ) {
          window.FUTStudentSearch.setQuery("", true);
        }

        const categorySlug = section.dataset.category;
        let needsLoad = false;

        if (window.FUTCategoryLoader && categorySlug) {
          // Load target + all categories above it so heights don't shift mid-scroll
          if (typeof window.FUTCategoryLoader.ensureCategoryPath === "function") {
            needsLoad = window.FUTCategoryLoader.ensureCategoryPath(categorySlug);
          } else if (window.FUTCategoryLoader.isDeferred(section)) {
            needsLoad = window.FUTCategoryLoader.ensureCategory(categorySlug, {
              immediate: true,
            });
          }
        }

        history.replaceState(null, "", `#${id}`);
        scrollToCategory(id, { waitForLoad: needsLoad, slug: categorySlug });
        setActiveLink(a, true);
        if (!isDesktop()) setPanelExpanded(false);
      });

      li.appendChild(a);
      list.appendChild(li);
      links.push({ section, link: a, item: li });
    });

    updateMeta(false);
  }

  function setActiveLink(active, scrollTocPanel) {
    links.forEach(({ link }) => {
      link.classList.toggle("is-active", link === active);
    });

    if (active && isDesktop() && scrollTocPanel) {
      active.scrollIntoView({ block: "nearest", behavior: "instant" });
    }
  }

  function syncVisibility(showAll) {
    links.forEach(({ section, item }) => {
      const hidden =
        !showAll && section.classList.contains("is-hidden");
      item.classList.toggle("is-hidden", hidden);
    });
    updateMeta(showAll);
  }

  function setupSpy(showAll) {
    if (spyObserver) spyObserver.disconnect();

    const visibleLinks = showAll
      ? links
      : links.filter(
          ({ section }) => !section.classList.contains("is-hidden"),
        );
    if (visibleLinks.length === 0) return;

    let spyFrame = 0;

    spyObserver = new IntersectionObserver(
      (entries) => {
        // Don't fight an in-progress TOC jump
        if (pendingScrollId) return;
        if (spyFrame) return;
        spyFrame = requestAnimationFrame(() => {
          spyFrame = 0;
          const visible = entries
            .filter((entry) => entry.isIntersecting)
            .sort(
              (a, b) => a.boundingClientRect.top - b.boundingClientRect.top,
            );

          if (visible.length === 0) return;

          const id = visible[0].target.id;
          const match = links.find(({ section }) => section.id === id);
          if (match) setActiveLink(match.link, false);
        });
      },
      {
        root: null,
        rootMargin: `-${HEADER_OFFSET}px 0px -55% 0px`,
        threshold: 0,
      },
    );

    visibleLinks.forEach(({ section }) => spyObserver.observe(section));
  }

  function enable(showAll) {
    toc.hidden = false;
    syncLayout();
    syncVisibility(showAll);
    setupSpy(showAll);
  }

  function disable() {
    toc.hidden = true;
    if (spyObserver) spyObserver.disconnect();
  }

  function refresh() {
    enable(false);
  }

  function showAllSections() {
    if (links.length === 0) return;
    syncVisibility(true);
    setupSpy(true);
  }

  buildList();
  refresh();

  window.updatePageToc = refresh;
  window.resetPageTocVisibility = showAllSections;

  toggle.addEventListener("click", () => {
    if (isDesktop()) return;
    setPanelExpanded(true);
  });

  if (header) {
    header.addEventListener("click", () => {
      setPanelExpanded(!panelExpanded);
    });
  }

  if (backdrop) {
    backdrop.addEventListener("click", () => setPanelExpanded(false));
  }

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && panelExpanded) setPanelExpanded(false);
  });

  document.addEventListener("click", (e) => {
    if (isDesktop() || !panelExpanded) return;
    const target = e.target;
    if (!(target instanceof Node)) return;
    if (toc.contains(target)) return;
    setPanelExpanded(false);
  });

  DESKTOP_MQ.addEventListener("change", syncLayout);

  window.addEventListener(
    "scroll",
    () => {
      if (links.length === 0) return;
      if (pendingScrollId) {
        // Clear lock once we're near the target
        const el = document.getElementById(pendingScrollId);
        if (el) {
          const top = el.getBoundingClientRect().top;
          if (top >= 40 && top <= getHeaderOffset() + 80) {
            pendingScrollId = null;
          }
        }
        return;
      }
      if (window.scrollY < 80 && links[0]) {
        setActiveLink(links[0].link, false);
      }
    },
    { passive: true },
  );
})();
