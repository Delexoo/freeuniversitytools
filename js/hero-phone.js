(function () {
  const stage = document.getElementById('heroStage');
  const hero = document.getElementById('hero');
  const messagesEl = document.getElementById('heroPhoneMessages');
  const progressBar = document.getElementById('heroProgressBar');

  if (!stage || !hero || !messagesEl) return;

  const bubbles = Array.from(messagesEl.querySelectorAll('.dm-bubble'));
  if (bubbles.length === 0) return;

  const DESKTOP_MIN = 901;
  let mobileTimer = null;
  let lastVisible = -1;
  let isPinned = false;
  let scrollEnabled = false;

  stage.style.setProperty('--hero-msg-count', String(bubbles.length));

  function clamp(value, min, max) {
    return Math.min(max, Math.max(min, value));
  }

  function isDesktopMode() {
    return (
      window.innerWidth >= DESKTOP_MIN &&
      !window.matchMedia('(prefers-reduced-motion: reduce)').matches
    );
  }

  function getStageMetrics() {
    const stageTop = stage.getBoundingClientRect().top + window.scrollY;
    const scrollable = Math.max(stage.offsetHeight - window.innerHeight, 1);
    return { stageTop, scrollable };
  }

  function scrollMessagesToEnd() {
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function setVisibleCount(count) {
    const next = clamp(count, 0, bubbles.length);
    if (next === lastVisible) return;
    lastVisible = next;

    bubbles.forEach((bubble, index) => {
      bubble.classList.toggle('is-visible', index < next);
    });

    if (progressBar) {
      const pct = bubbles.length <= 1 ? 100 : ((next - 1) / (bubbles.length - 1)) * 100;
      progressBar.style.width = `${clamp(pct, 0, 100)}%`;
    }

    if (next > 0) {
      requestAnimationFrame(scrollMessagesToEnd);
    }

    stage.classList.toggle('is-complete', next >= bubbles.length);
  }

  function visibleFromScrollY(y) {
    const { stageTop, scrollable } = getStageMetrics();
    const segment = scrollable / bubbles.length;
    if (y <= stageTop) return 1;
    const index = Math.floor((y - stageTop) / segment) + 1;
    return clamp(index, 1, bubbles.length);
  }

  function maxScrollForVisible(visible) {
    const { stageTop, scrollable } = getStageMetrics();
    if (visible >= bubbles.length) return stageTop + scrollable;
    const segment = scrollable / bubbles.length;
    return stageTop + visible * segment;
  }

  function setPinned(pinned) {
    if (pinned === isPinned) return;
    isPinned = pinned;
    hero.classList.toggle('is-pinned', pinned);
    stage.classList.toggle('is-pinned', pinned);
    document.documentElement.classList.toggle('hero-scroll-locked', pinned);
  }

  function updateFromScroll() {
    if (!isDesktopMode()) return;

    const { stageTop, scrollable } = getStageMetrics();
    const y = window.scrollY;
    const stageEnd = stageTop + scrollable;

    if (y < stageTop) {
      setPinned(false);
      setVisibleCount(1);
      return;
    }

    if (y <= stageEnd + 2) {
      setPinned(true);

      const visible = visibleFromScrollY(y);
      setVisibleCount(visible);

      if (visible < bubbles.length) {
        const maxY = maxScrollForVisible(visible);
        if (y > maxY + 1) {
          window.scrollTo({ top: maxY, left: 0, behavior: 'auto' });
        }
      }
      return;
    }

    if (lastVisible < bubbles.length) {
      setPinned(true);
      setVisibleCount(bubbles.length);
      window.scrollTo({ top: stageEnd, left: 0, behavior: 'auto' });
      return;
    }

    setPinned(false);
  }

  function onWheel(event) {
    if (!isDesktopMode() || !isPinned) return;
    if (lastVisible >= bubbles.length) return;

    const { stageTop, scrollable } = getStageMetrics();
    const y = window.scrollY;
    const maxY = maxScrollForVisible(lastVisible);

    if (event.deltaY > 0 && y >= maxY - 1) {
      event.preventDefault();
    }

    if (event.deltaY > 0 && y >= stageTop + scrollable - 1 && lastVisible < bubbles.length) {
      event.preventDefault();
    }
  }

  function startMobileSequence() {
    if (mobileTimer) clearInterval(mobileTimer);
    setPinned(false);
    setVisibleCount(0);

    let step = 0;
    mobileTimer = setInterval(() => {
      step += 1;
      setVisibleCount(step);
      if (step >= bubbles.length) {
        clearInterval(mobileTimer);
        mobileTimer = null;
      }
    }, 650);
  }

  function enableDesktop() {
    if (mobileTimer) {
      clearInterval(mobileTimer);
      mobileTimer = null;
    }
    setVisibleCount(1);
    updateFromScroll();
    if (!scrollEnabled) {
      window.addEventListener('scroll', updateFromScroll, { passive: true });
      window.addEventListener('wheel', onWheel, { passive: false });
      scrollEnabled = true;
    }
  }

  function enableMobile() {
    if (scrollEnabled) {
      window.removeEventListener('scroll', updateFromScroll);
      window.removeEventListener('wheel', onWheel);
      scrollEnabled = false;
    }
    setPinned(false);
    setVisibleCount(1);
    startMobileSequence();
  }

  function onResize() {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      if (scrollEnabled) {
        window.removeEventListener('scroll', updateFromScroll);
        window.removeEventListener('wheel', onWheel);
        scrollEnabled = false;
      }
      setPinned(false);
      setVisibleCount(bubbles.length);
      return;
    }

    if (window.innerWidth < DESKTOP_MIN) {
      enableMobile();
    } else {
      enableDesktop();
    }
  }

  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    setVisibleCount(bubbles.length);
  } else if (window.innerWidth < DESKTOP_MIN) {
    enableMobile();
  } else {
    enableDesktop();
  }

  window.addEventListener('resize', onResize, { passive: true });
})();
