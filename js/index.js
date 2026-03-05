const ctaPanel = document.querySelector('.cta-panel');
const featureSection = document.querySelector('.features');
const featureCards = Array.from(document.querySelectorAll('.features-grid .feature-card'));
const floatingStartBrowsing = document.getElementById('floatingStartBrowsing');
let lastDuckScrollY = window.scrollY;
let duckFacing = 1;

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}

function lerp(start, end, progress) {
  return start + (end - start) * progress;
}

function clearCtaInlineStyles() {
  if (!ctaPanel) return;
  ctaPanel.style.padding = '';
  ctaPanel.style.borderRadius = '';
  ctaPanel.style.gap = '';
  ctaPanel.style.maxWidth = '';
  ctaPanel.style.transform = '';
  ctaPanel.style.boxShadow = '';
}

function clearFloatingStartInlineStyles() {
  if (!floatingStartBrowsing) return;
  floatingStartBrowsing.style.padding = '';
  floatingStartBrowsing.style.borderRadius = '';
  floatingStartBrowsing.style.gap = '';
  floatingStartBrowsing.style.width = '';
  floatingStartBrowsing.style.transform = '';
  floatingStartBrowsing.style.boxShadow = '';
}

function updateFeatureCardMotion() {
  if (!featureSection || featureCards.length === 0) return;

  if (window.innerWidth <= 768) {
    featureCards.forEach(card => {
      card.style.setProperty('--card-x', '0px');
      card.style.setProperty('--card-y', '0px');
      card.style.setProperty('--card-scale', '1');
      card.style.setProperty('--card-opacity', '1');
      card.style.setProperty('--card-blur', '0px');
      card.style.setProperty('--card-scroll-shift', '0px');
    });
    return;
  }

  const rect = featureSection.getBoundingClientRect();
  const viewport = window.innerHeight || document.documentElement.clientHeight;
  const sectionProgress = clamp((viewport - rect.top) / (viewport + rect.height), 0, 1);
  const cardEntryOffsets = [
    { x: -120, y: 60 },
    { x: 120, y: 52 },
    { x: -110, y: 64 },
    { x: 110, y: 56 }
  ];

  featureCards.forEach((card, index) => {
    const localProgress = clamp(sectionProgress * 1.35 - index * 0.09, 0, 1);
    const offset = cardEntryOffsets[index % cardEntryOffsets.length];
    const x = offset.x * (1 - localProgress);
    const y = offset.y * (1 - localProgress);
    const shift = (1 - localProgress) * 8;
    const opacity = 0.78 + localProgress * 0.22;
    const blur = (1 - localProgress) * 2;
    const scale = 0.97 + localProgress * 0.03;

    card.style.setProperty('--card-x', `${x.toFixed(2)}px`);
    card.style.setProperty('--card-y', `${y.toFixed(2)}px`);
    card.style.setProperty('--card-scale', scale.toFixed(3));
    card.style.setProperty('--card-opacity', opacity.toFixed(3));
    card.style.setProperty('--card-blur', `${blur.toFixed(2)}px`);
    card.style.setProperty('--card-scroll-shift', `${shift.toFixed(2)}px`);
  });
}

function updateFeatureDuckMotion() {
  if (!featureSection) return;

  if (window.innerWidth <= 768) {
    featureSection.style.setProperty('--duck-x', '0px');
    featureSection.style.setProperty('--duck-opacity', '0');
    featureSection.style.setProperty('--duck-scale-x', '1');
    lastDuckScrollY = window.scrollY;
    return;
  }

  const scrollDelta = window.scrollY - lastDuckScrollY;
  if (scrollDelta > 0.1) {
    duckFacing = 1;
  } else if (scrollDelta < -0.1) {
    duckFacing = -1;
  }

  const rect = featureSection.getBoundingClientRect();
  const viewport = window.innerHeight || document.documentElement.clientHeight;
  const sectionProgress = clamp((viewport - rect.top) / (viewport + rect.height), 0, 1);
  const delayedProgress = clamp((sectionProgress - 0.14) / 0.86, 0, 1);
  const travelDistance = window.innerWidth + 240;
  const duckX = travelDistance * delayedProgress;

  featureSection.style.setProperty('--duck-x', `${duckX.toFixed(2)}px`);
  featureSection.style.setProperty('--duck-opacity', '1');
  featureSection.style.setProperty('--duck-scale-x', duckFacing.toString());
  lastDuckScrollY = window.scrollY;
}

function updateScrollEffects() {
  if (floatingStartBrowsing) {
    const isVisible = window.scrollY > 120;
    floatingStartBrowsing.classList.toggle('is-visible', isVisible);

    if (window.innerWidth <= 768 || !isVisible) {
      floatingStartBrowsing.classList.remove('is-expanded');
      clearFloatingStartInlineStyles();
    } else {
      const floatProgress = clamp((window.scrollY - 180) / 760, 0, 1);
      floatingStartBrowsing.classList.toggle('is-expanded', floatProgress > 0.68);
      floatingStartBrowsing.style.padding = `${lerp(10, 14, floatProgress).toFixed(2)}px ${lerp(16, 21, floatProgress).toFixed(2)}px`;
      floatingStartBrowsing.style.borderRadius = `${lerp(999, 24, floatProgress).toFixed(2)}px`;
      floatingStartBrowsing.style.gap = `${lerp(12, 18, floatProgress).toFixed(2)}px`;
      floatingStartBrowsing.style.width = `${lerp(300, 410, floatProgress).toFixed(2)}px`;
      floatingStartBrowsing.style.transform = `translate3d(0, 0, 0) scale(${lerp(0.96, 1, floatProgress).toFixed(3)})`;
      floatingStartBrowsing.style.boxShadow = `0 ${lerp(10, 20, floatProgress).toFixed(2)}px ${lerp(26, 46, floatProgress).toFixed(2)}px rgba(0, 0, 0, ${lerp(0.16, 0.24, floatProgress).toFixed(3)})`;
    }
  }

  updateFeatureCardMotion();
  updateFeatureDuckMotion();

  if (!ctaPanel) return;

  ctaPanel.classList.add('is-expanded');
  clearCtaInlineStyles();
}

window.addEventListener('scroll', updateScrollEffects);
window.addEventListener('resize', updateScrollEffects);
updateScrollEffects();

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function (e) {
    e.preventDefault();
    const target = document.querySelector(this.getAttribute('href'));
    if (target) {
      target.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
      });
    }
  });
});

// DM conversation scroll-reveal (appear/disappear per bubble)
(function() {
  const dmContainer = document.getElementById('dmContainer');
  if (!dmContainer) return;

  const bubbles = Array.from(dmContainer.querySelectorAll('.dm-bubble'));
  if (bubbles.length === 0) return;

  const dmObserver = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
      } else {
        entry.target.classList.remove('is-visible');
      }
    });
  }, { threshold: 0.1, rootMargin: '0px 0px -200px 0px' });

  bubbles.forEach(b => dmObserver.observe(b));
})();
