const toolsSearch = document.getElementById('toolsSearch');
const toolsModeToggle = document.getElementById('toolsModeToggle');
const resourceCards = Array.from(document.querySelectorAll('.resource-card'));
const categorySections = Array.from(document.querySelectorAll('.tool-category'));
const toggleOptions = Array.from(document.querySelectorAll('.tools-toggle-option'));
let currentMode = 'all';

function applyToolFilters() {
  const query = (toolsSearch?.value || '').trim().toLowerCase();
  const mode = currentMode;

  resourceCards.forEach((card) => {
    const text = card.textContent.toLowerCase();
    const matchesQuery = query.length === 0 || text.includes(query);
    const matchesMode = mode === 'all' || card.dataset.pricing === mode;
    card.style.display = matchesQuery && matchesMode ? '' : 'none';
  });

  categorySections.forEach((section) => {
    const cards = section.querySelectorAll('.resource-card');
    const hasEmpty = section.querySelector('.category-empty');
    if (cards.length === 0 && hasEmpty) {
      section.classList.toggle('is-hidden', query.length > 0 || mode !== 'all');
      return;
    }
    const anyVisible = Array.from(cards).some((c) => c.style.display !== 'none');
    section.classList.toggle('is-hidden', !anyVisible);
  });
}

applyToolFilters();

function setMode(nextMode) {
  currentMode = nextMode;
  if (toolsModeToggle) {
    toolsModeToggle.dataset.mode = nextMode;
  }
  toggleOptions.forEach((option) => {
    option.classList.toggle('active', option.dataset.mode === nextMode);
  });
  applyToolFilters();
}

// --- Timeline TOC ---
const tocTrack = document.getElementById('tocTrack');
const tocProgress = document.getElementById('tocProgress');
const tocItems = [];

const pageHeader = document.querySelector('.page-header');
(function addHeaderTocItem() {
  const item = document.createElement('div');
  item.className = 'toc-item';
  item.dataset.category = 'top';
  const dot = document.createElement('div');
  dot.className = 'toc-dot';
  const label = document.createElement('span');
  label.className = 'toc-label';
  label.textContent = 'Powerful Tools';
  item.appendChild(dot);
  item.appendChild(label);
  tocTrack.appendChild(item);
  item.addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
  tocItems.push({ item, section: pageHeader, alwaysVisible: true });
})();

categorySections.forEach((section) => {
  const title = section.querySelector('.category-title');
  if (!title) return;

  const item = document.createElement('div');
  item.className = 'toc-item';
  item.dataset.category = section.dataset.category;

  const dot = document.createElement('div');
  dot.className = 'toc-dot';

  const label = document.createElement('span');
  label.className = 'toc-label';
  label.textContent = title.textContent;

  item.appendChild(dot);
  item.appendChild(label);
  tocTrack.appendChild(item);

  item.addEventListener('click', () => {
    section.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });

  tocItems.push({ item, section });
});

const tocTimeline = document.getElementById('tocTimeline');

function updateTocVisibility() {
  const query = (toolsSearch?.value || '').trim();
  const isSearching = query.length > 0;
  if (tocTimeline) {
    tocTimeline.classList.toggle('is-searching', isSearching);
  }
  tocItems.forEach(({ item, section, alwaysVisible }) => {
    if (alwaysVisible) return;
    item.classList.toggle('is-hidden', section.classList.contains('is-hidden'));
  });
}

const _origApply = applyToolFilters;
applyToolFilters = function() {
  _origApply();
  updateTocVisibility();
};
updateTocVisibility();

if (toolsSearch) {
  toolsSearch.addEventListener('input', () => applyToolFilters());
}

toggleOptions.forEach((option) => {
  option.addEventListener('click', () => setMode(option.dataset.mode));
});

const observer = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      entry.target.style.opacity = '1';
      entry.target.style.animation = 'fadeInUp 0.6s ease forwards';
    }
  });
}, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });

categorySections.forEach((section) => {
  section.style.opacity = '0';
  observer.observe(section);
});

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
    const firstVisible = tocItems.find(t => !t.item.classList.contains('is-hidden'));
    if (firstVisible) activeIdx = tocItems.indexOf(firstVisible);
  }

  tocItems.forEach(({ item }, i) => {
    item.classList.toggle('is-active', i === activeIdx);
  });

  if (tocProgress && tocTrack) {
    const visibleTocItems = tocItems.filter(t => !t.item.classList.contains('is-hidden'));
    if (activeIdx >= 0 && visibleTocItems.length > 0) {
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

const _origApply2 = applyToolFilters;
applyToolFilters = function() {
  _origApply2();
  scheduleTocUpdate();
};

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
    if (dist < closestDist) {
      closestDist = dist;
      closest = entry;
    }
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

window.addEventListener('mousemove', (e) => {
  if (!isDragging) return;
  scrollToNearestFromY(e.clientY);
});

window.addEventListener('mouseup', () => {
  if (!isDragging) return;
  isDragging = false;
  tocTrack.classList.remove('is-dragging');
  document.body.style.userSelect = '';
});

tocTrack.addEventListener('touchstart', (e) => {
  if (e.target.closest('.toc-item')) return;
  isDragging = true;
  tocTrack.classList.add('is-dragging');
  scrollToNearestFromY(e.touches[0].clientY);
}, { passive: true });

window.addEventListener('touchmove', (e) => {
  if (!isDragging) return;
  scrollToNearestFromY(e.touches[0].clientY);
}, { passive: true });

window.addEventListener('touchend', () => {
  if (!isDragging) return;
  isDragging = false;
  tocTrack.classList.remove('is-dragging');
});
