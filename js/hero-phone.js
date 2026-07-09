(function () {
  const stage = document.getElementById("heroStage");
  const hero = document.getElementById("hero");
  const messagesEl = document.getElementById("heroPhoneMessages");
  const progressBar = document.getElementById("heroProgressBar");
  const progressRoot = document.querySelector(".hero-scroll-progress");
  const pageProgressFill = document.getElementById("heroPageProgressFill");

  if (!stage || !hero || !messagesEl) return;

  const bubbles = Array.from(messagesEl.querySelectorAll(".dm-bubble"));
  if (bubbles.length === 0) return;

  const reducedMotion = window.matchMedia(
    "(prefers-reduced-motion: reduce)",
  ).matches;
  const desktopMq = window.matchMedia("(min-width: 901px)");

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

  init();
})();
