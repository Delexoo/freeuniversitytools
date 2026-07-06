const ctaPanel = document.querySelector('.cta-panel');
const heroSection = document.querySelector('.hero');
const heroContent = heroSection ? heroSection.querySelector('.hero-content') : null;
const featureSection = document.querySelector('.features');
const dmSection = document.querySelector('.dm-section');
const dmContainerEl = document.getElementById('dmContainer');
const featuresInline = document.querySelector('.features-inline');
const toolsPreviewSection = document.querySelector('.tools-preview');
const toolsHeader = toolsPreviewSection ? toolsPreviewSection.querySelector('.tools-header') : null;
const toolsTrack = toolsPreviewSection ? toolsPreviewSection.querySelector('.tools-track') : null;
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

function getScrollEffectScale() {
  const width = window.innerWidth;
  if (width <= 768) return 0;
  if (width <= 1024) return 0.35;
  if (width <= 1280) return 0.65;
  return 1;
}

function resetInlineMotion(el) {
  if (!el) return;
  el.style.transform = '';
  el.style.opacity = '';
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

function updateDmMotion() {
  if (!dmSection || !dmContainerEl) return;

  const effectScale = getScrollEffectScale();
  if (effectScale === 0) {
    dmContainerEl.style.transform = '';
    return;
  }

  const rect = dmSection.getBoundingClientRect();
  const viewport = window.innerHeight || document.documentElement.clientHeight;

  // Start from the current position and slide the phone UP as you scroll past it.
  const startY = viewport * 0.9;   // when the section is just entering view
  const endY = viewport * 0.1;     // let it keep moving until it's very high on the screen
  const progress = clamp((startY - rect.top) / (startY - endY), 0, 1);

  const maxOffset = window.innerWidth >= 1400 ? -260 : -140;
  const offset = lerp(0, maxOffset * effectScale, progress);
  dmContainerEl.style.transform = `translateY(${offset}px)`;
}

function updateScrollEffects() {
  const effectScale = getScrollEffectScale();

  // Subtle hero text parallax: slide the hero copy down a bit as you scroll
  if (heroSection && heroContent) {
    if (effectScale === 0) {
      heroContent.style.transform = '';
      heroContent.style.opacity = '';
    } else {
      const heroRect = heroSection.getBoundingClientRect();
      const viewport = window.innerHeight || document.documentElement.clientHeight;
      const heroProgress = clamp((0 - heroRect.top) / (heroRect.height || 1), 0, 1);
      const heroOffset = lerp(0, 160 * effectScale, heroProgress);
      const heroScale = lerp(1, 1 - 0.1 * effectScale, heroProgress);
      heroContent.style.transform = `translateY(${heroOffset.toFixed(1)}px) scale(${heroScale.toFixed(3)})`;
      const heroOpacity = lerp(1, 1 - effectScale, heroProgress);
      heroContent.style.opacity = heroOpacity.toFixed(2);
    }
  }

  // Inline "Why choose us" text: as you scroll DOWN it grows, moves down, and fades in (smoothed)
  if (featuresInline) {
    if (effectScale === 0) {
      resetInlineMotion(featuresInline);
    } else {
      const rect = featuresInline.getBoundingClientRect();
      const viewport = window.innerHeight || document.documentElement.clientHeight;
      const rawProgress = (viewport - rect.top) / viewport;
      const progress = clamp(rawProgress * 2.2, 0, 1);
      const offset = lerp(-140 * effectScale, 40 * effectScale, progress);
      const scale = lerp(1 - 0.06 * effectScale, 1 + 0.08 * effectScale, progress);
      const opacity = lerp(1 - 0.9 * effectScale, 1, progress);

      featuresInline.style.transform =
        `translateY(${offset.toFixed(1)}px) scale(${scale.toFixed(3)})`;
      featuresInline.style.opacity = opacity.toFixed(2);
    }
  }

  // Featured Tools section: text and buttons animate separately from opposite directions
  if (toolsPreviewSection && (toolsHeader || toolsTrack)) {
    const rect = toolsPreviewSection.getBoundingClientRect();
    const viewport = window.innerHeight || document.documentElement.clientHeight;
    const raw = (viewport - rect.top) / viewport;
    const progress = clamp(raw * 1.2, 0, 1);

    if (toolsHeader) {
      if (effectScale === 0) {
        resetInlineMotion(toolsHeader);
      } else {
        const headerOffsetX = lerp(-140 * effectScale, 0, progress);
        const headerScale = lerp(1 - 0.05 * effectScale, 1 + 0.04 * effectScale, progress);
        const headerOpacity = lerp(1 - effectScale, 1, progress);
        toolsHeader.style.transform =
          `translate(${headerOffsetX.toFixed(1)}px, 0px) scale(${headerScale.toFixed(3)})`;
        toolsHeader.style.opacity = headerOpacity.toFixed(2);
      }
    }

    if (toolsTrack) {
      const cards = Array.from(toolsTrack.querySelectorAll('.tool-card'));
      cards.forEach((card, index) => {
        if (effectScale === 0) {
          resetInlineMotion(card);
          return;
        }

        const delay = index * 0.08;
        const localProgress = clamp((progress - delay) * 1.2, 0, 1);
        const cardOffsetX = lerp(120 * effectScale, 0, localProgress);
        const cardOffsetY = lerp(30 * effectScale, 0, localProgress);
        const cardScale = lerp(1 - 0.05 * effectScale, 1 + 0.03 * effectScale, localProgress);
        const cardOpacity = lerp(1 - effectScale, 1, localProgress);
        card.style.transform =
          `translate(${cardOffsetX.toFixed(1)}px, ${cardOffsetY.toFixed(1)}px) scale(${cardScale.toFixed(3)})`;
        card.style.opacity = cardOpacity.toFixed(2);
      });
    }
  }

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
  updateDmMotion();

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
