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
        const slug = section.dataset.category;
        if (
          window.FUTCategoryLoader &&
          slug &&
          window.FUTCategoryLoader.isDeferred(section)
        ) {
          window.FUTCategoryLoader.ensureCategory(slug);
        }
        const target = document.getElementById(id);
        if (!target) return;
        const y =
          target.getBoundingClientRect().top + window.scrollY - HEADER_OFFSET;
        window.scrollTo({ top: y, left: 0, behavior: "smooth" });
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
      if (window.scrollY < 80 && links[0]) {
        setActiveLink(links[0].link, false);
      }
    },
    { passive: true },
  );
})();
