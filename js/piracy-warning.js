(function () {
  const REDIRECT_BLOCKER_URL =
    "https://chromewebstore.google.com/detail/egmgebeelgaakhaoodlmnimbfemfgdah";
  const PROTON_VPN_URL = "https://protonvpn.com/free-vpn";

  const WARN_CATEGORIES = new Set(["free-movies", "live-streaming", "free-books"]);

  const SAFE_DOMAINS = new Set([
    "openstax.org",
    "gutenberg.org",
    "openlibrary.org",
    "archive.org",
    "manybooks.net",
    "standardebooks.org",
    "feedbooks.com",
    "tubitv.com",
    "pluto.tv",
    "crackle.com",
    "twitch.tv",
    "kick.com",
    "youtube.com",
    "youtu.be",
    "github.com",
  ]);

  const ALWAYS_WARN_DOMAINS = new Set(["deepwebnest.com"]);

  const modal = document.getElementById("piracyDisclaimerModal");
  if (!modal) return;

  const continueBtn = document.getElementById("piracyContinueBtn");
  const cancelBtn = document.getElementById("piracyCancelBtn");
  let pendingHref = null;

  function extractDomain(href) {
    try {
      return new URL(href, window.location.href).hostname
        .replace(/^www\./, "")
        .toLowerCase();
    } catch {
      return "";
    }
  }

  function isSafeLink(link) {
    if (link.dataset.piracySafe === "true") return true;
    const domain = extractDomain(link.getAttribute("href") || "");
    if (!domain) return false;
    return SAFE_DOMAINS.has(domain);
  }

  function shouldWarn(link, category) {
    const domain = extractDomain(link.getAttribute("href") || "");
    if (ALWAYS_WARN_DOMAINS.has(domain)) return true;
    if (!WARN_CATEGORIES.has(category)) return false;
    return !isSafeLink(link);
  }

  function tagPiracyLinks(root) {
    const scope = root || document;
    scope.querySelectorAll(".tool-link").forEach((link) => {
      const section = link.closest(".tool-category");
      const category = section?.dataset?.category || "";
      const warn = shouldWarn(link, category);
      link.classList.toggle("piracy-warning-link", warn);
    });
  }

  function openModal(href) {
    pendingHref = href;
    modal.classList.add("is-open");
    document.body.style.overflow = "hidden";
  }

  function closeModal() {
    modal.classList.remove("is-open");
    document.body.style.overflow = "";
    pendingHref = null;
  }

  document.addEventListener(
    "click",
    (event) => {
      const link = event.target.closest("a.piracy-warning-link");
      if (!link || modal.contains(link)) return;
      event.preventDefault();
      event.stopPropagation();
      openModal(link.getAttribute("href"));
    },
    true,
  );

  if (continueBtn) {
    continueBtn.addEventListener("click", () => {
      if (pendingHref) {
        window.open(pendingHref, "_blank", "noopener,noreferrer");
      }
      closeModal();
    });
  }

  if (cancelBtn) cancelBtn.addEventListener("click", closeModal);

  modal.addEventListener("click", (event) => {
    if (event.target === modal) closeModal();
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && modal.classList.contains("is-open")) {
      closeModal();
    }
  });

  function init() {
    tagPiracyLinks();
    const directory = document.querySelector(".tools-directory");
    if (directory && typeof MutationObserver !== "undefined") {
      const observer = new MutationObserver(() => tagPiracyLinks(directory));
      observer.observe(directory, { childList: true, subtree: true });
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  window.FreeUniversityPiracyWarning = {
    tagPiracyLinks,
    REDIRECT_BLOCKER_URL,
    PROTON_VPN_URL,
  };
})();
