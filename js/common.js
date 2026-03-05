// Mobile menu toggle
const mobileMenuToggle = document.getElementById('mobileMenuToggle');
const mainNav = document.getElementById('mainNav');

if (mobileMenuToggle && mainNav) {
  mobileMenuToggle.addEventListener('click', function() {
    mainNav.classList.toggle('mobile-open');
    this.textContent = mainNav.classList.contains('mobile-open') ? '✕' : '☰';
  });

  mainNav.querySelectorAll('.nav-link, .btn-donate').forEach(link => {
    link.addEventListener('click', function() {
      mainNav.classList.remove('mobile-open');
      mobileMenuToggle.textContent = '☰';
    });
  });
}

// Header scroll effect
window.addEventListener('scroll', function() {
  const header = document.getElementById('header');
  if (!header) return;
  if (window.scrollY > 50) {
    header.classList.add('scrolled');
  } else {
    header.classList.remove('scrolled');
  }
});

// Tooltip system
(function() {
  const tooltipTargets = document.querySelectorAll('[data-tooltip]');
  if (tooltipTargets.length === 0) return;

  let tip = null;
  let hideTimer = null;
  const isTouchDevice = 'ontouchstart' in window;

  function create() {
    if (tip) return tip;
    tip = document.createElement('div');
    tip.className = 'tooltip';
    document.body.appendChild(tip);
    return tip;
  }

  function show(target) {
    const text = target.getAttribute('data-tooltip');
    if (!text) return;
    clearTimeout(hideTimer);
    const el = create();
    el.textContent = text;
    el.classList.remove('is-visible');

    requestAnimationFrame(() => {
      const rect = target.getBoundingClientRect();
      const tipRect = el.getBoundingClientRect();
      let left = rect.left;
      let top = rect.top - tipRect.height - 8;

      if (top < 8) top = rect.bottom + 8;
      if (left + tipRect.width > window.innerWidth - 12) {
        left = window.innerWidth - tipRect.width - 12;
      }
      if (left < 12) left = 12;

      el.style.left = left + 'px';
      el.style.top = top + 'px';
      el.classList.add('is-visible');
    });
  }

  function hide() {
    if (!tip) return;
    tip.classList.remove('is-visible');
    hideTimer = setTimeout(() => {
      if (tip && tip.parentNode) {
        tip.parentNode.removeChild(tip);
        tip = null;
      }
    }, 200);
  }

  if (isTouchDevice) {
    tooltipTargets.forEach(t => {
      t.addEventListener('click', function(e) {
        if (tip && tip.classList.contains('is-visible')) {
          hide();
        } else {
          show(this);
        }
      });
    });
    document.addEventListener('click', function(e) {
      if (!e.target.closest('[data-tooltip]')) hide();
    });
  } else {
    tooltipTargets.forEach(t => {
      t.addEventListener('mouseenter', function() { show(this); });
      t.addEventListener('mouseleave', hide);
    });
  }
})();
