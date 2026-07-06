const toolsSearch = document.getElementById('toolsSearch');
const toolsModeToggle = document.getElementById('toolsModeToggle');
const resourceCards = Array.from(document.querySelectorAll('.resource-card'));
const toolLinks = Array.from(document.querySelectorAll('.tool-link'));
const categorySections = Array.from(document.querySelectorAll('.tool-category'));
const toggleOptions = Array.from(document.querySelectorAll('.tools-toggle-option'));
let currentMode = 'free';

// Page 1 (Free Tools): free | free-tier | limited.
// Page 2 (Paid Tools): paid | limited | free-tier (all tools that have a paid tier).
function matchesPricingMode(pricing, mode) {
  if (mode === 'free') {
    return pricing === 'free' || pricing === 'free-tier' || pricing === 'limited';
  }
  if (mode === 'paid') {
    return pricing === 'paid' || pricing === 'limited' || pricing === 'free-tier';
  }
  return false;
}

// Extra keywords per category (data-category or title) so search has wide reach
const CATEGORY_KEYWORDS = {
  'must-try': ['compare', 'ai', 'redirect', 'vocal', 'blocker', 'uncensored', 'cluely', 'essential'],
  'free-books': ['books', 'read', 'library', 'anna', 'ocean', 'openstax', 'libgen', 'gutenberg', 'open library'],
  'ai': ['ai', 'claude', 'chatgpt', 'gemini', 'perplexity', 'copilot', 'grok', 'deepai', 'deepseek', 'qwen', 'cluely', 'assistant'],
  'research': ['research', 'search', 'academic', 'papers', 'perplexity', 'claude', 'chatgpt'],
  'analytical': ['analysis', 'data', 'claude', 'gemini', 'perplexity'],
  'immersive-reader': ['reader', 'read', 'text to speech', 'eleven', 'speechify', 'accessibility'],
  'creator-tools': ['creator', 'youtube', 'thumbnail', 'instagram', 'bass', 'visualizer', 'download'],
  'browser-games': ['games', 'minecraft', 'subway', 'fancy', 'temple', 'kizi', 'poki', 'play'],
  'remote-jobs': ['remote', 'jobs', 'work', 'remotasks', 'neevo', 'hivemicro', 'clickworker', 'appen', 'pareto'],
  'utilities': ['utility', 'qr', 'password', 'random', 'url', 'shortener', 'barcode', 'tinyurl', 'fix', 'cheat sheet'],
  'image': ['image', 'photo', 'remove bg', 'watermark', 'resize', 'crop', 'convert', 'compress', 'tinywow', 'iloveimg', 'ocr'],
  'video': ['video', 'convert', 'youtube', 'download', 'clipchamp', 'vsave', 'cnvmp3', 'openshot', 'shotcut'],
  'audio': ['audio', 'mp3', 'convert', 'vocal', 'remover', 'audacity', '123apps'],
  'productivity': ['notepad', 'notes', 'notion', 'ticktick', 'todo', 'productivity'],
  'free-movies': ['movies', 'stream', 'tubi', 'pluto', 'soap', 'flix', 'watch', 'free movies'],
  'free-stuff': ['free', 'fmhy', 'alternativeto', 'product hunt', 'discovery', 'deepweb'],
  'generative-ai': ['generative', 'ai', 'magic', 'character', 'hume', 'venice'],
  'conversation': ['chat', 'conversation', 'ai', 'character', 'hume', 'venice'],
  'all-in-one-tools': ['toolfk', 'tinywow', '10015', 'all in one', 'online tools'],
  'security': ['password', 'security', 'generator'],
  'programming-ai': ['programming', 'code', 'claude', 'copilot', 'dyad', 'aistudio', 'design arena'],
  'ai-browser': ['browser', 'ai', 'manus', 'google disco', 'kortix', 'arc', 'opera'],
  'notepad': ['notepad', 'notes', 'notion', 'evernote', 'standard notes'],
  'todo-list': ['todo', 'task', 'list', 'microsoft', 'ticktick', 'minimalist', 'todoist'],
  'mathematics': ['math', 'algebra', 'calculus', 'symbolab', 'mathbot', 'mathos', 'wolfram', 'numbers'],
  'english': ['english', 'writing', 'grammar', 'quillbot', 'claude', 'chatgpt', 'gemini'],
  'science': ['science', 'chemistry', 'chemistry guide'],
  'study': ['study', 'flashcards', 'quiz', 'learn', 'knowt', 'quizlet', 'anki', 'studocu', 'khan', 'coursera', 'exam'],
  'courses': ['courses', 'learn', 'khan', 'mit', 'odin', 'freecodecamp', 'coursera', 'edx'],
  'writing': ['writing', 'citation', 'zotero', 'mendeley', 'easybib', 'word counter'],
  'pdf': ['pdf', 'merge', 'split', 'ilovepdf', 'tinywow', 'lightpdf', 'pdf.io', 'smallpdf'],
  'converters': ['convert', 'compress', 'freeconvert', 'cloudconvert', 'tinypng', 'handbrake'],
  'design': ['design', 'canva', 'gimp', 'figma', 'photopea', 'inkscape'],
  'programming': ['programming', 'code', 'freecodecamp', 'odin', 'sololearn', 'qwen'],
  'cloud': ['cloud', 'storage', 'drive', 'dropbox', 'mega', 'onedrive', 'wetransfer', 'box']
};

function getSearchableTextForLink(linkEl) {
  const text = linkEl.textContent.toLowerCase();
  const section = linkEl.closest('.tool-category');
  const categoryTitle = (section?.querySelector('.category-title')?.textContent || '').toLowerCase();
  const dataCategory = section?.dataset?.category || '';
  const extra = (CATEGORY_KEYWORDS[dataCategory] || []).join(' ');
  return [text, categoryTitle, extra].filter(Boolean).join(' ');
}

function applyToolFilters() {
  const query = (toolsSearch?.value || '').trim().toLowerCase();
  const mode = currentMode;
  const queryWords = query.split(/\s+/).filter(Boolean);

  function filterItem(el) {
    const searchable = el.classList.contains('tool-link')
      ? getSearchableTextForLink(el)
      : el.textContent.toLowerCase();
    const matchesQuery = query.length === 0 || queryWords.every((word) => searchable.includes(word));
    const pricing = el.dataset.pricing || 'free';
    const matchesMode = matchesPricingMode(pricing, mode);
    const show = matchesQuery && matchesMode;
    el.style.display = show ? '' : 'none';
  }

  resourceCards.forEach(filterItem);
  toolLinks.forEach(filterItem);

  categorySections.forEach((section) => {
    const cards = section.querySelectorAll('.resource-card');
    const links = section.querySelectorAll('.tool-link');
    const hasEmpty = section.querySelector('.category-empty');
    if (cards.length === 0 && links.length === 0 && hasEmpty) {
      section.classList.toggle('is-hidden', query.length > 0 || mode !== 'free');
      return;
    }
    const anyCardVisible = Array.from(cards).some((c) => c.style.display !== 'none');
    const anyLinkVisible = Array.from(links).some((l) => l.style.display !== 'none');
    section.classList.toggle('is-hidden', !anyCardVisible && !anyLinkVisible);
  });
}

// Choose Plus / Pro / Premium / Paid based on tool name when in Paid mode
function getPaidLabelForLink(linkEl) {
  const name = (linkEl.querySelector('.tool-link-name')?.textContent || '').toLowerCase();
  if (name.includes('chatgpt')) return 'Plus';
  if (name.includes('claude')) return 'Pro';
  if (name.includes('grammarly')) return 'Premium';
  if (name.includes('quillbot')) return 'Premium';
  if (name.includes('notion')) return 'Plus';
  return 'Paid';
}

function injectPricingLabels() {
  toolLinks.forEach((link) => {
    if (link.querySelector('.tool-pricing-label')) return;
    const span = document.createElement('span');
    span.className = 'tool-pricing-label';
    link.appendChild(span);
  });
}

// Keep label text and data-label in sync with current mode (Free vs Paid)
function updatePricingLabels() {
  toolLinks.forEach((link) => {
    const pricing = link.dataset.pricing || 'free';
    const labelEl = link.querySelector('.tool-pricing-label');
    if (!labelEl) return;

    let labelText = 'Free';
    let labelKey = pricing;

    if (currentMode === 'free') {
      if (pricing === 'free') {
        labelText = 'Free';
        labelKey = 'free';
      } else if (pricing === 'free-tier') {
        labelText = 'Free Tier';
        labelKey = 'free-tier';
      } else if (pricing === 'limited') {
        labelText = 'Limited';
        labelKey = 'limited';
      } else if (pricing === 'paid') {
        labelText = 'Paid';
        labelKey = 'paid';
      }
    } else {
      // Paid mode – anything that has or is a paid tier shows Plus / Pro / Premium / Paid
      if (pricing === 'free') {
        labelText = 'Free';
        labelKey = 'free';
      } else if (pricing === 'paid' || pricing === 'limited' || pricing === 'free-tier') {
        labelText = getPaidLabelForLink(link);
        labelKey = 'paid';
      }
    }

    labelEl.textContent = labelText;
    labelEl.setAttribute('data-label', labelKey);
  });
}

injectPricingLabels();
updatePricingLabels();
applyToolFilters();

function setMode(nextMode) {
  if (nextMode !== 'free' && nextMode !== 'paid') return;
  currentMode = nextMode;
  if (document.body) {
    document.body.dataset.mode = nextMode;
  }
  if (toolsModeToggle) {
    toolsModeToggle.dataset.mode = nextMode;
  }
  toggleOptions.forEach((option) => {
    option.classList.toggle('active', option.dataset.mode === nextMode);
  });
  updatePricingLabels();
  applyToolFilters();
}

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
