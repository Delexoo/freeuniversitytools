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
const allToolItems = Array.from(document.querySelectorAll('.tool-item'));
const allCategorySections = Array.from(document.querySelectorAll('.category-section'));
let currentMode = 'free';

// Tag types: free | free-tier | limited → show on "Free Tools"; paid | limited → show on "Paid Tools".
// On Free view, limited tags display "Limited"; on Paid view they display "Paid".
function updateLimitedTagLabels() {
  const label = currentMode === 'free' ? 'Limited' : 'Paid';
  document.querySelectorAll('.tool-tag.limited').forEach((el) => { el.textContent = label; });
}

function getItemPricing(item) {
  const tag = item.querySelector('.tool-tag');
  if (!tag) return 'free';
  if (tag.classList.contains('paid')) return 'paid';
  if (tag.classList.contains('limited')) return 'limited';
  return 'free';
}

// Extra keywords per category label (lowercase) so search has wide reach
const CATEGORY_KEYWORDS = {
  'must try!': ['compare', 'ai', 'redirect', 'vocal', 'blocker', 'essential', 'top'],
  'student': ['writing', 'grammar', 'quillbot', 'notion', 'student'],
  'research': ['research', 'search', 'perplexity', 'claude', 'chatgpt', 'papers', 'academic'],
  'mathematics': ['math', 'algebra', 'calculus', 'equation', 'symbolab', 'mathbot', 'numbers'],
  'programming': ['code', 'coding', 'developer', 'claude', 'cursor', 'github'],
  'analytical': ['analysis', 'data', 'claude', 'gemini', 'perplexity'],
  'ai browsers': ['browser', 'arc', 'opera', 'ai', 'browsing'],
  'conversation': ['chat', 'ai', 'character', 'talk', 'conversation'],
  'notetakers': ['notes', 'notion', 'evernote', 'note', 'taking'],
  'all-in-one': ['ai', 'claude', 'chatgpt', 'all in one'],
  'study': ['study', 'flashcards', 'quiz', 'learn', 'learning', 'exam', 'memorize', 'school', 'homework', 'knowt', 'quizlet', 'anki', 'studocu', 'khan'],
  'essay tools': ['essay', 'writing', 'word counter', 'citation', 'paper'],
  'pdf tools': ['pdf', 'merge', 'split', 'convert', 'tinywow', 'ilovepdf'],
  'image tools': ['image', 'photo', 'remove bg', 'resize', 'crop', 'convert'],
  'video converters': ['video', 'convert', 'youtube', 'download', 'clipchamp'],
  'audio converters': ['audio', 'mp3', 'convert', 'vocal', 'music'],
  'gif converters': ['gif', 'ezgif', 'animate', 'convert'],
  'collaborate': ['collaborate', 'share', 'drive', 'dropbox', 'mega', 'miro', 'team'],
  'online poll': ['poll', 'survey', 'vote', 'feedback'],
  'online whiteboard': ['whiteboard', 'draw', 'board', 'miro'],
  'course': ['course', 'learn', 'coursera', 'edx', 'udemy', 'khan', 'mit', 'freecodecamp'],
  'productivity': ['productivity', 'todo', 'task', 'microsoft', 'ticktick', 'minimalist'],
  'code learning': ['code', 'learn', 'freecodecamp', 'odin', 'programming'],
  'design tools': ['design', 'canva', 'gimp', 'figma', 'photopea', 'inkscape'],
  'language learning': ['language', 'duolingo', 'hello', 'tandem', 'memrise', 'busuu'],
  'immersive reader': ['reader', 'read', 'text to speech', 'eleven', 'speechify', 'accessibility'],
  'todo list': ['todo', 'task', 'list', 'productivity', 'ticktick', 'todoist', 'microsoft'],
  'notepad': ['notepad', 'notes', 'notion', 'simple', 'text'],
  'utilities': ['utility', 'qr', 'password', 'random', 'url', 'shortener', 'barcode'],
  'free books': ['books', 'read', 'library', 'anna', 'ocean', 'libgen', 'gutenberg'],
  'free movies': ['movies', 'stream', 'tubi', 'pluto', 'soap', 'flix', 'watch'],
  'free stuff': ['free', 'fmhy', 'alternativeto', 'product hunt', 'discovery'],
  'secret': ['12ft', 'paywall', 'bypass', 'read']
};

function getSearchableText(item) {
  const name = (item.querySelector('.tool-name')?.textContent || '').toLowerCase();
  const section = item.closest('.category-section');
  const categoryLabel = (section?.querySelector('.category-label')?.textContent || '').toLowerCase();
  const extra = (CATEGORY_KEYWORDS[categoryLabel] || []).join(' ');
  return [name, categoryLabel, extra].filter(Boolean).join(' ');
}

function applyFilters() {
  const query = (toolsSearch?.value || '').trim().toLowerCase();
  const isSearching = query.length > 0;
  const queryWords = query.split(/\s+/).filter(Boolean);

  allToolItems.forEach((item) => {
    const searchable = getSearchableText(item);
    const matchesQuery = !isSearching || queryWords.every((word) => searchable.includes(word));
    const pricing = getItemPricing(item);
    const matchesMode = currentMode === 'paid' ? (pricing === 'paid' || pricing === 'limited') : (pricing !== 'paid');
    const show = matchesQuery && matchesMode;
    item.style.display = show ? '' : 'none';
    if (show) item.classList.add('is-visible');
  });

  allCategorySections.forEach((section) => {
    const isPaidSection = section.classList.contains('paid-section');
    if (isPaidSection) {
      section.style.display = currentMode === 'paid' ? 'block' : 'none';
      if (currentMode === 'paid') section.classList.add('is-visible');
      return;
    }
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
}

function setMode(nextMode) {
  currentMode = nextMode;
  if (toolsModeToggle) toolsModeToggle.dataset.mode = nextMode;
  toggleOptions.forEach((opt) => {
    opt.classList.toggle('active', opt.dataset.mode === nextMode);
  });
  applyFilters();
  updateLimitedTagLabels();
}

if (toolsSearch) {
  toolsSearch.addEventListener('input', () => applyFilters());
}

toggleOptions.forEach((opt) => {
  opt.addEventListener('click', () => setMode(opt.dataset.mode));
});

applyFilters();
updateLimitedTagLabels();
