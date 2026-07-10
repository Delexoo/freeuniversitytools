(function () {
  const stage = document.getElementById("heroStage");
  const hero = document.getElementById("hero");
  const messagesEl = document.getElementById("heroPhoneMessages");
  const progressBar = document.getElementById("heroProgressBar");
  const progressRoot = document.querySelector(".hero-scroll-progress");
  const pageProgressFill = document.getElementById("heroPageProgressFill");
  const header = document.getElementById("header");
  const mobileBanner = document.getElementById("mobileBanner");

  if (!stage || !hero || !messagesEl) return;

  const bubbles = Array.from(messagesEl.querySelectorAll(".dm-bubble"));
  if (bubbles.length === 0) return;

  const reducedMotion = window.matchMedia(
    "(prefers-reduced-motion: reduce)",
  ).matches;
  const desktopMq = window.matchMedia("(min-width: 901px)");
  const mobileMq = window.matchMedia("(max-width: 900px)");

  let lastVisible = -1;
  let lastProgress = -1;
  let revealTimer = null;
  let nextIndex = 0;

  stage.style.setProperty("--hero-msg-count", String(bubbles.length));

  function clamp(value, min, max) {
    return Math.min(max, Math.max(min, value));
  }

  function isDesktop() {
    return desktopMq.matches;
  }

  function syncLayoutVars() {
    if (header) {
      const headerHeight = Math.ceil(header.getBoundingClientRect().height);
      document.documentElement.style.setProperty(
        "--header-h",
        `${headerHeight}px`,
      );
    }

    const bannerVisible =
      mobileBanner &&
      mobileMq.matches &&
      !mobileBanner.classList.contains("hide");
    const bannerHeight =
      bannerVisible && mobileBanner
        ? Math.ceil(mobileBanner.getBoundingClientRect().height)
        : 0;

    document.documentElement.style.setProperty(
      "--mobile-banner-h",
      `${bannerHeight}px`,
    );
    document.documentElement.classList.toggle("has-mobile-banner", bannerVisible);
  }

  function setMobileMode() {
    const mobile = mobileMq.matches;
    document.documentElement.classList.toggle("hero-mobile", mobile);
    stage.classList.toggle("hero-stage--mobile", mobile);
    hero.classList.toggle("hero--mobile", mobile);
    syncLayoutVars();
  }

  function randomBetween(min, max) {
    return min + Math.random() * (max - min);
  }

  function delayBeforeBubble(index) {
    if (index === 0) return randomBetween(500, 1100);

    const bubble = bubbles[index];
    const prev = bubbles[index - 1];
    const sameSide =
      bubble.classList.contains("sent") === prev.classList.contains("sent");

    if (sameSide) return randomBetween(280, 720);
    if (bubble.classList.contains("received")) {
      return randomBetween(900, 1900);
    }
    return randomBetween(650, 1400);
  }

  function scrollMessagesToBottom() {
    const top = messagesEl.scrollHeight - messagesEl.clientHeight;
    if (top <= 0) return;
    messagesEl.scrollTo({
      top,
      behavior: reducedMotion ? "auto" : "smooth",
    });
  }

  function setVisibleCount(count, progress) {
    const next = clamp(count, 0, bubbles.length);
    const pct = clamp(progress * 100, 0, 100);
    const complete = next >= bubbles.length;

    if (next !== lastVisible) {
      lastVisible = next;
      bubbles.forEach((bubble, index) => {
        bubble.classList.toggle("is-visible", index < next);
      });
      if (next > 0) scrollMessagesToBottom();
    }

    stage.classList.toggle("is-complete", complete);
    hero.classList.toggle("is-complete", complete);

    if (progress !== lastProgress) {
      lastProgress = progress;
      if (progressBar) progressBar.style.width = `${pct}%`;
      if (progressRoot) {
        progressRoot.setAttribute("aria-valuenow", String(Math.round(pct)));
      }
      if (pageProgressFill) pageProgressFill.style.height = `${pct}%`;
    }
  }

  function clearRevealTimer() {
    if (revealTimer) {
      window.clearTimeout(revealTimer);
      revealTimer = null;
    }
  }

  function scheduleNextReveal() {
    clearRevealTimer();

    if (!isDesktop() || document.hidden) return;

    if (nextIndex >= bubbles.length) {
      setVisibleCount(bubbles.length, 1);
      return;
    }

    const wait = delayBeforeBubble(nextIndex);
    revealTimer = window.setTimeout(() => {
      nextIndex += 1;
      setVisibleCount(nextIndex, nextIndex / bubbles.length);
      scheduleNextReveal();
    }, wait);
  }

  function startConversation() {
    clearRevealTimer();
    nextIndex = 0;
    setVisibleCount(0, 0);
    scheduleNextReveal();
  }

  function stopConversation() {
    clearRevealTimer();
  }

  function init() {
    setMobileMode();

    if (!isDesktop()) {
      stopConversation();
      setVisibleCount(0, 0);
      stage.classList.remove("is-complete");
      hero.classList.remove("is-complete");
      return;
    }

    if (reducedMotion) {
      stopConversation();
      setVisibleCount(bubbles.length, 1);
      return;
    }

    startConversation();
  }

  document.addEventListener("visibilitychange", () => {
    if (!isDesktop() || reducedMotion) return;
    if (document.hidden) {
      stopConversation();
      return;
    }
    if (nextIndex < bubbles.length) {
      scheduleNextReveal();
    }
  });

  desktopMq.addEventListener("change", init);
  mobileMq.addEventListener("change", init);

  window.addEventListener("resize", syncLayoutVars, { passive: true });
  window.addEventListener("orientationchange", syncLayoutVars, { passive: true });

  if (mobileBanner) {
    const bannerObserver = new MutationObserver(syncLayoutVars);
    bannerObserver.observe(mobileBanner, {
      attributes: true,
      attributeFilter: ["class"],
    });
  }

  const mainNav = document.getElementById("mainNav");
  if (mainNav) {
    const navObserver = new MutationObserver(syncLayoutVars);
    navObserver.observe(mainNav, {
      attributes: true,
      attributeFilter: ["class"],
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init, { once: true });
  } else {
    init();
  }

  window.addEventListener("load", syncLayoutVars, { once: true });
})();
