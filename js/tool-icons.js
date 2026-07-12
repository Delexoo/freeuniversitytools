/**
 * Resolve tool icons with a reliable fallback chain:
 * bundled logo -> icon.horse PNG -> site default logo
 */
(function () {
  const FALLBACK =
    "https://raw.githubusercontent.com/Delexoo/freeuniversitytools/refs/heads/main/doc/FreeUniversityTools.png";

  function hostFromHref(href) {
    try {
      return new URL(href).hostname.replace(/^www\./i, "");
    } catch {
      return "";
    }
  }

  function networkIconForHref(href) {
    const host = hostFromHref(href);
    if (!host) return null;

    if (host === "github.com") {
      try {
        const owner = new URL(href).pathname.split("/").filter(Boolean)[0];
        if (owner) return `https://github.com/${owner}.png?size=64`;
      } catch {
        /* fall through */
      }
    }

    if (host === "chromewebstore.google.com") {
      return "https://icon.horse/icon/google.com";
    }

    return `https://icon.horse/icon/${encodeURIComponent(host)}`;
  }

  function isBundledLogo(src) {
    return /raw\.githubusercontent\.com|FreeUniversityTools\.png/i.test(src);
  }

  function isGithubAvatar(src) {
    return /github\.com\/.+\.png/i.test(src);
  }

  function isGoogleFavicon(src) {
    return /google\.com\/s2\/favicons|gstatic\.com\/faviconV2/i.test(src);
  }

  function isDuckDuckGoFavicon(src) {
    return /duckduckgo\.com\/ip3\//i.test(src);
  }

  function isNetworkFavicon(src) {
    return (
      isGoogleFavicon(src) ||
      isDuckDuckGoFavicon(src) ||
      /icon\.horse\/icon\//i.test(src)
    );
  }

  function upgradeNetworkIconSrc(src, href) {
    if (isGoogleFavicon(src) || isDuckDuckGoFavicon(src) || !src.trim()) {
      return networkIconForHref(href);
    }
    return null;
  }

  function normalizeIconSrc(img, href) {
    const src = img.getAttribute("src") || "";
    if (isBundledLogo(src) || isGithubAvatar(src)) return;

    const upgraded = upgradeNetworkIconSrc(src, href);
    if (upgraded) img.src = upgraded;

    const dataFallback = img.getAttribute("data-fallback") || "";
    if (isDuckDuckGoFavicon(dataFallback) || isGoogleFavicon(dataFallback)) {
      const network = networkIconForHref(href);
      if (network) img.setAttribute("data-fallback", network);
    }
  }

  function wireImage(img, href) {
    if (!img || img.dataset.logoWired === "1") return;

    normalizeIconSrc(img, href);

    img.addEventListener("error", function onError() {
      if (img.dataset.logoFinal === "1") return;

      const stage = Number(img.dataset.logoStage || 0);
      const current = img.currentSrc || img.getAttribute("src") || "";
      const dataFallback = img.getAttribute("data-fallback") || "";

      if (stage === 0 && (isBundledLogo(current) || isGithubAvatar(current))) {
        img.dataset.logoStage = "1";
        const network = networkIconForHref(href);
        if (network && current !== network) {
          img.src = network;
          return;
        }
      }

      if (
        stage < 2 &&
        dataFallback &&
        !isNetworkFavicon(dataFallback) &&
        dataFallback !== current
      ) {
        img.dataset.logoStage = "2";
        img.src = dataFallback;
        return;
      }

      if (stage < 3 && !isNetworkFavicon(current)) {
        img.dataset.logoStage = "3";
        const network = networkIconForHref(href);
        if (network && current !== network) {
          img.src = network;
          return;
        }
      }

      img.dataset.logoStage = "4";
      img.dataset.logoFinal = "1";
      if (current !== FALLBACK) {
        img.src = FALLBACK;
      }
    });

    img.referrerPolicy = "no-referrer";
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

  function wireLinksInSection(section) {
    section.querySelectorAll(".tool-link").forEach((link) => {
      wireIcon(link);
    });
  }

  function initToolIcons() {
    document.querySelectorAll(".tool-link").forEach(wireIcon);
    document
      .querySelectorAll('a.tool-card[href^="http"]')
      .forEach(wireToolCard);
  }

  window.addEventListener("fut:category-loaded", (event) => {
    const section = event.detail?.section;
    if (!section) return;

    const wire = () => wireLinksInSection(section);
    if ("requestIdleCallback" in window) {
      window.requestIdleCallback(wire, { timeout: 300 });
    } else {
      window.setTimeout(wire, 0);
    }
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initToolIcons);
  } else {
    initToolIcons();
  }

  window.FUTWireToolImage = wireImage;
})();
