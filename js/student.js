// Staggered scroll-reveal animations
const sectionObserver = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      const section = entry.target;

      const label = section.querySelector('.category-label');
      if (label) {
        label.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        label.style.opacity = '0';
        label.style.transform = 'translateY(10px)';
        requestAnimationFrame(() => {
          label.style.opacity = '1';
          label.style.transform = 'translateY(0)';
        });
      }

      section.classList.add('is-visible');
      section.style.transition = 'opacity 0.5s ease, transform 0.5s ease';

      const items = section.querySelectorAll('.tool-item');
      items.forEach((item, i) => {
        setTimeout(() => {
          item.classList.add('is-visible');
          item.style.transition = 'opacity 0.35s ease, transform 0.35s ease';
        }, 120 + i * 40);
      });

      sectionObserver.unobserve(section);
    }
  });
}, { threshold: 0.05, rootMargin: '0px 0px -50px 0px' });

document.querySelectorAll('.category-section').forEach(el => {
  sectionObserver.observe(el);
});

// --- 3-way toggle + search + filtering ---
const toolsSearch = document.getElementById('toolsSearch');
const toolsModeToggle = document.getElementById('toolsModeToggle');
const toggleOptions = Array.from(document.querySelectorAll('.tools-toggle-option'));
const mainTitle = document.getElementById('mainTitle');
const tocTimeline = document.getElementById('tocTimeline');
const allToolItems = Array.from(document.querySelectorAll('.tool-item'));
const allCategorySections = Array.from(document.querySelectorAll('.category-section'));
let currentMode = 'all';

function getItemPricing(item) {
  const tag = item.querySelector('.tool-tag');
  if (!tag) return 'free';
  if (tag.classList.contains('paid')) return 'paid';
  return 'free';
}

function applyFilters() {
  const query = (toolsSearch?.value || '').trim().toLowerCase();
  const isSearching = query.length > 0;

  if (tocTimeline) {
    tocTimeline.classList.toggle('is-searching', isSearching);
  }

  allToolItems.forEach((item) => {
    const name = (item.querySelector('.tool-name')?.textContent || '').toLowerCase();
    const matchesQuery = !isSearching || name.includes(query);
    const pricing = getItemPricing(item);
    const matchesMode = currentMode === 'all' || pricing === currentMode;
    const show = matchesQuery && matchesMode;
    item.style.display = show ? '' : 'none';
    if (show) item.classList.add('is-visible');
  });

  allCategorySections.forEach((section) => {
    const items = section.querySelectorAll('.tool-item');
    const anyVisible = Array.from(items).some((i) => i.style.display !== 'none');
    section.style.display = anyVisible ? '' : 'none';
    if (anyVisible) section.classList.add('is-visible');
  });

  const dividers = document.querySelectorAll('.section-divider');
  dividers.forEach((d) => d.style.display = isSearching ? 'none' : '');

  const aiContainer = document.querySelector('.top-ai-assistants-container');
  if (aiContainer) {
    if (isSearching || currentMode === 'paid') {
      const hasVisible = Array.from(aiContainer.querySelectorAll('.tool-item')).some(i => i.style.display !== 'none');
      aiContainer.style.display = hasVisible ? '' : 'none';
    } else {
      aiContainer.style.display = '';
    }
  }

  buildTocItems();
  scheduleTocUpdate();
}

function setMode(nextMode) {
  currentMode = nextMode;
  if (toolsModeToggle) toolsModeToggle.dataset.mode = nextMode;
  toggleOptions.forEach((opt) => {
    opt.classList.toggle('active', opt.dataset.mode === nextMode);
  });
  applyFilters();
}

if (toolsSearch) {
  toolsSearch.addEventListener('input', () => applyFilters());
}

toggleOptions.forEach((opt) => {
  opt.addEventListener('click', () => setMode(opt.dataset.mode));
});

applyFilters();

// --- Timeline TOC ---
const tocTrack = document.getElementById('tocTrack');
const tocProgress = document.getElementById('tocProgress');
let tocItems = [];

function buildTocItems() {
  tocItems = [];
  while (tocTrack.children.length > 1) {
    tocTrack.removeChild(tocTrack.lastChild);
  }

  const visibleSections = allCategorySections.filter((s) => {
    return s.style.display !== 'none';
  });

  const headerItem = document.createElement('div');
  headerItem.className = 'toc-item';
  const headerDot = document.createElement('div');
  headerDot.className = 'toc-dot';
  const headerLabel = document.createElement('span');
  headerLabel.className = 'toc-label';
  headerLabel.textContent = 'Student Tools';
  headerItem.appendChild(headerDot);
  headerItem.appendChild(headerLabel);
  tocTrack.appendChild(headerItem);
  headerItem.addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
  tocItems.push({ item: headerItem, section: mainTitle || document.body, alwaysVisible: true });

  visibleSections.forEach((section) => {
    const label = section.querySelector('.category-label');
    if (!label) return;
    const item = document.createElement('div');
    item.className = 'toc-item';
    const dot = document.createElement('div');
    dot.className = 'toc-dot';
    const lbl = document.createElement('span');
    lbl.className = 'toc-label';
    lbl.textContent = label.textContent;
    item.appendChild(dot);
    item.appendChild(lbl);
    tocTrack.appendChild(item);
    item.addEventListener('click', () => {
      section.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
    tocItems.push({ item, section });
  });
}

let tocRaf = 0;
function updateTocScroll() {
  const viewMid = window.innerHeight * 0.35;
  let activeIdx = -1;

  for (let i = tocItems.length - 1; i >= 0; i--) {
    const { section, item } = tocItems[i];
    if (item.classList.contains('is-hidden')) continue;
    if (section.offsetParent === null && !tocItems[i].alwaysVisible) continue;
    const rect = section.getBoundingClientRect();
    if (rect.top <= viewMid) {
      activeIdx = i;
      break;
    }
  }

  if (activeIdx === -1) {
    const first = tocItems.find(t => !t.item.classList.contains('is-hidden'));
    if (first) activeIdx = tocItems.indexOf(first);
  }

  tocItems.forEach(({ item }, i) => {
    item.classList.toggle('is-active', i === activeIdx);
  });

  if (tocProgress && tocTrack) {
    if (activeIdx >= 0) {
      const activeEl = tocItems[activeIdx].item;
      if (activeEl.offsetParent !== null) {
        const trackRect = tocTrack.getBoundingClientRect();
        const dotRect = activeEl.getBoundingClientRect();
        const h = (dotRect.top + dotRect.height / 2) - trackRect.top;
        tocProgress.style.height = Math.max(0, h) + 'px';
      } else {
        tocProgress.style.height = '0px';
      }
    } else {
      tocProgress.style.height = '0px';
    }
  }
}

function scheduleTocUpdate() {
  cancelAnimationFrame(tocRaf);
  tocRaf = requestAnimationFrame(updateTocScroll);
}

window.addEventListener('scroll', scheduleTocUpdate, { passive: true });
updateTocScroll();

// --- Draggable TOC ---
let isDragging = false;

function getVisibleTocItems() {
  return tocItems.filter(t => !t.item.classList.contains('is-hidden'));
}

function scrollToNearestFromY(clientY) {
  const visible = getVisibleTocItems();
  if (visible.length === 0) return;
  let closest = visible[0];
  let closestDist = Infinity;
  visible.forEach((entry) => {
    const rect = entry.item.getBoundingClientRect();
    const mid = rect.top + rect.height / 2;
    const dist = Math.abs(clientY - mid);
    if (dist < closestDist) { closestDist = dist; closest = entry; }
  });
  if (closest.alwaysVisible) {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  } else {
    closest.section.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
}

tocTrack.addEventListener('mousedown', (e) => {
  if (e.target.closest('.toc-item')) return;
  isDragging = true;
  tocTrack.classList.add('is-dragging');
  document.body.style.userSelect = 'none';
  scrollToNearestFromY(e.clientY);
});
window.addEventListener('mousemove', (e) => { if (isDragging) scrollToNearestFromY(e.clientY); });
window.addEventListener('mouseup', () => { if (isDragging) { isDragging = false; tocTrack.classList.remove('is-dragging'); document.body.style.userSelect = ''; } });
tocTrack.addEventListener('touchstart', (e) => { if (e.target.closest('.toc-item')) return; isDragging = true; tocTrack.classList.add('is-dragging'); scrollToNearestFromY(e.touches[0].clientY); }, { passive: true });
window.addEventListener('touchmove', (e) => { if (isDragging) scrollToNearestFromY(e.touches[0].clientY); }, { passive: true });
window.addEventListener('touchend', () => { if (isDragging) { isDragging = false; tocTrack.classList.remove('is-dragging'); } });
