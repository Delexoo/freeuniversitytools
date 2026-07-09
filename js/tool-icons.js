/**
 * Resolve tool icons from each link's domain when bundled logos fail to load.
 */
(function () {
  const FALLBACK =
    "https://raw.githubusercontent.com/Delexoo/freeuniversitytools/refs/heads/main/doc/FreeUniversityTools.png";

  function faviconForHref(href) {
    try {
      const u = new URL(href);
      const host = u.hostname.replace(/^www\./i, "");

      if (host === "github.com") {
        const owner = u.pathname.split("/").filter(Boolean)[0];
        if (owner) {
          return `https://github.com/${owner}.png?size=64`;
        }
        return "https://www.google.com/s2/favicons?domain=github.com&sz=128";
      }

      if (host === "chromewebstore.google.com") {
        return "https://www.google.com/s2/favicons?domain=google.com&sz=128";
      }

      return `https://www.google.com/s2/favicons?domain=${encodeURIComponent(host)}&sz=128`;
    } catch {
      return FALLBACK;
    }
  }

  function wireImage(img, href) {
    if (!img || img.dataset.logoWired === "1") return;

    const fallback = img.getAttribute("data-fallback") || faviconForHref(href);
    img.dataset.fallback = fallback;

    img.addEventListener(
      "error",
      function onError() {
        const current = img.getAttribute("src") || "";
        if (current === FALLBACK) return;

        if (
          current !== fallback &&
          !/\/s2\/favicons/.test(current) &&
          !/github\.com\/.+\.png/.test(current)
        ) {
          img.src = fallback;
          return;
        }

        if (current !== FALLBACK) {
          img.src = FALLBACK;
        }
      },
      { passive: true },
    );

    img.dataset.logoWired = "1";
    if (!img.getAttribute("loading")) {
      img.setAttribute("loading", "lazy");
    }
    if (!img.getAttribute("decoding")) {
      img.setAttribute("decoding", "async");
    }
  }

  function wireIcon(link) {
    const img = link.querySelector(".tool-link-icon");
    wireImage(img, link.getAttribute("href") || "");
  }

  function wireToolCard(card) {
    const img = card.querySelector(".tool-icon img, img");
    wireImage(img, card.getAttribute("href") || "");
  }

  function initToolIcons() {
    document.querySelectorAll(".tool-link").forEach(wireIcon);
    document
      .querySelectorAll('a.tool-card[href^="http"]')
      .forEach(wireToolCard);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initToolIcons);
  } else {
    initToolIcons();
  }
})();
