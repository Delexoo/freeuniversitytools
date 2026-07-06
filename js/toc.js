(function () {
  const toc = document.getElementById('pageToc');
  const toggle = document.getElementById('pageTocToggle');
  const panel = document.getElementById('pageTocPanel');
  const list = document.getElementById('pageTocList');
  const directory = document.querySelector('.tools-directory');

  if (!toc || !toggle || !panel || !list || !directory) return;

  const HEADER_OFFSET = 72;
  const FEATURED = new Set(['must-try', 'github-powerhouses']);

  let sections = [];
  let links = [];
  let spyObserver = null;

  function setPanelOpen(open) {
    panel.hidden = !open;
    toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
  }

  function ensureSectionId(section) {
    const slug = section.dataset.category;
    if (!slug) return null;
    const id = `category-${slug}`;
    section.id = id;
    return id;
  }

  function buildList() {
    list.innerHTML = '';
    links = [];

    sections = Array.from(directory.querySelectorAll('.tool-category'));
    sections.forEach((section) => {
      const slug = section.dataset.category;
      const titleEl = section.querySelector('.category-title');
      if (!slug || !titleEl) return;

      const id = ensureSectionId(section);
      const li = document.createElement('li');
      li.className = 'page-toc-item';
      if (FEATURED.has(slug)) li.classList.add('page-toc-item--featured');
      li.dataset.category = slug;

      const a = document.createElement('a');
      a.className = 'page-toc-link';
      a.href = `#${id}`;
      a.textContent = titleEl.textContent.trim();
      a.addEventListener('click', (event) => {
        event.preventDefault();
        const target = document.getElementById(id);
        if (!target) return;
        const y = target.getBoundingClientRect().top + window.scrollY - HEADER_OFFSET;
        window.scrollTo({ top: y, left: 0, behavior: 'smooth' });
        setActiveLink(a);
        setPanelOpen(false);
      });

      li.appendChild(a);
      list.appendChild(li);
      links.push({ section, link: a, item: li });
    });
  }

  function setActiveLink(active) {
    links.forEach(({ link }) => {
      link.classList.toggle('is-active', link === active);
    });
  }

  function syncVisibility() {
    links.forEach(({ section, item }) => {
      const hidden = section.classList.contains('is-hidden');
      item.classList.toggle('is-hidden', hidden);
    });
  }

  function setupSpy() {
    if (spyObserver) spyObserver.disconnect();

    const visibleLinks = links.filter(({ section }) => !section.classList.contains('is-hidden'));
    if (visibleLinks.length === 0) return;

    spyObserver = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((entry) => entry.isIntersecting)
          .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top);

        if (visible.length === 0) return;

        const id = visible[0].target.id;
        const match = links.find(({ section }) => section.id === id);
        if (match) setActiveLink(match.link);
      },
      {
        root: null,
        rootMargin: `-${HEADER_OFFSET}px 0px -55% 0px`,
        threshold: 0,
      }
    );

    visibleLinks.forEach(({ section }) => spyObserver.observe(section));
  }

  function enable() {
    toc.hidden = false;
    setPanelOpen(false);
    syncVisibility();
    setupSpy();
  }

  function disable() {
    toc.hidden = true;
    if (spyObserver) spyObserver.disconnect();
  }

  function refresh() {
    enable();
    syncVisibility();
    setupSpy();
  }

  buildList();
  refresh();

  window.updatePageToc = refresh;

  toggle.addEventListener('click', () => {
    setPanelOpen(panel.hidden);
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') setPanelOpen(false);
  });

  document.addEventListener('click', (e) => {
    if (panel.hidden) return;
    const target = e.target;
    if (!(target instanceof Node)) return;
    if (toc.contains(target)) return;
    setPanelOpen(false);
  });

  window.addEventListener('resize', () => {
    // keep panel usable if the viewport changes
    if (!panel.hidden) setPanelOpen(true);
  }, { passive: true });

  window.addEventListener('scroll', () => {
    if (links.length === 0) return;
    if (window.scrollY < 80 && links[0]) {
      setActiveLink(links[0].link);
    }
  }, { passive: true });
})();
