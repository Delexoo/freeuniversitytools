const toolsSearch = document.getElementById('toolsSearch');
const toolsModeToggle = document.getElementById('toolsModeToggle');
const toolsDirectory = document.querySelector('.tools-directory');
const toolLinks = toolsDirectory
  ? Array.from(toolsDirectory.querySelectorAll('.tool-link'))
  : Array.from(document.querySelectorAll('.tool-link'));
const categorySections = toolsDirectory
  ? Array.from(toolsDirectory.querySelectorAll('.tool-category'))
  : Array.from(document.querySelectorAll('.tool-category'));
const toggleOptions = Array.from(document.querySelectorAll('.tools-toggle-option'));
const futureCategoriesSection = document.querySelector('.future-categories');
let currentMode = 'free';

// Free mode: free | free-tier | limited. Paid mode: paid | limited | free-tier.
function matchesPricingMode(pricing, mode) {
  if (mode === 'free') {
    return pricing === 'free' || pricing === 'free-tier' || pricing === 'limited';
  }
  if (mode === 'paid') {
    return pricing === 'paid' || pricing === 'limited' || pricing === 'free-tier';
  }
  return false;
}

const CATEGORY_KEYWORDS = {
  'must-try': ['compare', 'ai', 'redirect', 'vocal', 'blocker', 'uncensored', 'cluely', 'essential', 'top'],
  'free-books': ['books', 'read', 'library', 'anna', 'ocean', 'openstax', 'libgen', 'gutenberg', 'open library', 'archive'],
  'immersive-reader': ['reader', 'read', 'text to speech', 'eleven', 'speechify', 'accessibility', 'natural', 'aloud'],
  'courses': ['course', 'learn', 'coursera', 'edx', 'udemy', 'khan', 'mit', 'freecodecamp', 'odin', 'mindluster'],
  'essay-tools': ['essay', 'writing', 'word counter', 'citation', 'paper', 'grammar', 'quillbot', 'zotero', 'mendeley', 'detector'],
  'research': ['research', 'search', 'perplexity', 'claude', 'chatgpt', 'papers', 'academic', 'gemini', 'deepseek', 'grok', 'copilot'],
  'mathematics': ['math', 'algebra', 'calculus', 'equation', 'symbolab', 'mathbot', 'numbers', 'wolfram'],
  'programming-ai': ['code', 'coding', 'developer', 'claude', 'cursor', 'github', 'programming', 'dyad', 'aistudio', 'copilot'],
  'analytical': ['analysis', 'data', 'claude', 'gemini', 'perplexity', 'analytical'],
  'conversation': ['chat', 'ai', 'character', 'talk', 'conversation', 'magichour', 'hume', 'venice'],
  'free-movies': ['movies', 'stream', 'tubi', 'pluto', 'soap', 'flix', 'watch', 'vip'],
  'free-stuff': ['free', 'fmhy', 'alternativeto', 'product hunt', 'discovery', 'awesome', 'deepweb'],
  'ai-notetakers': ['notes', 'notion', 'evernote', 'note', 'taking', 'obsidian', 'granola', 'mem'],
  'study': ['study', 'flashcards', 'quiz', 'learn', 'learning', 'exam', 'memorize', 'school', 'homework', 'knowt', 'quizlet', 'anki', 'studocu', 'cluely', 'youlearn'],
  'cloud': ['collaborate', 'share', 'drive', 'dropbox', 'mega', 'icloud', 'onedrive', 'team', 'file sharing', 'wetransfer', 'box'],
  'online-poll': ['poll', 'survey', 'vote', 'feedback', 'forms', 'typeform', 'surveymonkey'],
  'pdf': ['pdf', 'merge', 'split', 'convert', 'tinywow', 'ilovepdf', 'lightpdf', 'smallpdf'],
  'image': ['image', 'photo', 'remove bg', 'resize', 'crop', 'convert', 'ocr', 'watermark', 'compress', 'iloveimg'],
  'video': ['video', 'convert', 'youtube', 'download', 'clipchamp', 'cnvmp3', 'online convert'],
  'audio': ['audio', 'mp3', 'convert', 'vocal', 'music', 'audacity', 'remover'],
  'gif-converters': ['gif', 'ezgif', 'animate', 'convert'],
  'online-whiteboard': ['whiteboard', 'draw', 'board', 'miro', 'canva', 'figma'],
  'programming': ['code', 'learn', 'freecodecamp', 'odin', 'programming', 'sololearn', 'qwen'],
  'design': ['design', 'canva', 'gimp', 'figma', 'photopea', 'inkscape'],
  'language-learning': ['language', 'duolingo', 'hello', 'tandem', 'memrise', 'busuu'],
  'todo-list': ['todo', 'task', 'list', 'productivity', 'ticktick', 'todoist', 'microsoft', 'minimalist'],
  'chrome-extension': ['chrome', 'extension', 'browser', 'grammarly', 'adblock', 'lastpass', 'manus', 'redirect'],
  'notepad': ['notepad', 'notes', 'notion', 'simple', 'text', 'evernote', 'simplenote', 'onenote'],
  'utilities': ['utility', 'qr', 'password', 'random', 'url', 'shortener', 'barcode', 'tinyurl', 'toolfk', 'ifixit'],
  'secret': ['12ft', 'paywall', 'bypass', 'read', 'archive', 'ladder']
};

function normalizeSearchText(value) {
  return (value || '')
    .toLowerCase()
    .replace(/[''`]/g, '')
    .replace(/[^a-z0-9]+/g, ' ')
    .trim();
}

function getSearchableTextForLink(linkEl) {
  const name = linkEl.querySelector('.tool-link-name')?.textContent || '';
  const section = linkEl.closest('.tool-category');
  const categoryTitle = section?.querySelector('.category-title')?.textContent || '';
  const dataCategory = section?.dataset?.category || '';
  const extra = (CATEGORY_KEYWORDS[dataCategory] || []).join(' ');
  return normalizeSearchText([name, categoryTitle, extra].filter(Boolean).join(' '));
}

function linkMatchesQuery(linkEl, queryWords) {
  if (queryWords.length === 0) return true;
  const searchable = getSearchableTextForLink(linkEl);
  return queryWords.every((word) => searchable.includes(normalizeSearchText(word)));
}

function applyFilters() {
  const query = (toolsSearch?.value || '').trim();
  const isSearching = query.length > 0;
  const queryWords = query.split(/\s+/).filter(Boolean);

  toolLinks.forEach((link) => {
    const pricing = link.dataset.pricing || 'free';
    const matchesQuery = linkMatchesQuery(link, queryWords);
    const matchesMode = matchesPricingMode(pricing, currentMode);
    const show = matchesQuery && matchesMode;
    link.style.display = show ? '' : 'none';
  });

  categorySections.forEach((section) => {
    const links = section.querySelectorAll('.tool-link');
    const anyVisible = Array.from(links).some((link) => link.style.display !== 'none');
    section.classList.toggle('is-hidden', !anyVisible);
  });

  if (futureCategoriesSection) {
    futureCategoriesSection.style.display = isSearching ? 'none' : '';
  }
}

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
    } else if (pricing === 'free') {
      labelText = 'Free';
      labelKey = 'free';
    } else if (pricing === 'paid' || pricing === 'limited' || pricing === 'free-tier') {
      labelText = getPaidLabelForLink(link);
      labelKey = 'paid';
    }

    labelEl.textContent = labelText;
    labelEl.setAttribute('data-label', labelKey);
  });
}

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
  applyFilters();
}

if (toolsSearch) {
  toolsSearch.addEventListener('input', applyFilters);
  toolsSearch.addEventListener('search', applyFilters);
}

toggleOptions.forEach((option) => {
  option.addEventListener('click', () => setMode(option.dataset.mode));
});

injectPricingLabels();
updatePricingLabels();
applyFilters();

const sectionObserver = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (!entry.isIntersecting) return;
    entry.target.style.opacity = '1';
    entry.target.style.animation = 'fadeInUp 0.6s ease forwards';
    sectionObserver.unobserve(entry.target);
  });
}, { threshold: 0.05, rootMargin: '0px 0px -50px 0px' });

categorySections.forEach((section) => {
  section.style.opacity = '0';
  sectionObserver.observe(section);
});
