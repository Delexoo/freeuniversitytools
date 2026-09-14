// Anonymous site visit counter (hits.sh) — no cookies, no personal data
(function () {
  try {
    const host = window.location.hostname || "";
    if (
      !host ||
      host === "localhost" ||
      host === "127.0.0.1" ||
      host.endsWith(".local")
    ) {
      return;
    }

    const img = new Image();
    img.alt = "";
    img.width = 1;
    img.height = 1;
    img.decoding = "async";
    img.referrerPolicy = "no-referrer-when-downgrade";
    img.style.cssText =
      "position:absolute;width:1px;height:1px;opacity:0;pointer-events:none;left:-9999px;top:-9999px";
    img.src =
      "https://hits.sh/freeuniversitytools.com.svg?view=today-total&style=flat-square&label=visits&color=2563eb&labelColor=09090b&" +
      Date.now();
    document.documentElement.appendChild(img);
  } catch {
    /* ignore tracking failures */
  }
})();

// Fixed legal / install dock (bottom on every page)
(function () {
  if (document.getElementById("legalDock")) return;

  const script =
    document.currentScript ||
    document.querySelector('script[src*="common.js"]');
  const scriptSrc =
    script && script.getAttribute("src")
      ? script.getAttribute("src")
      : "js/common.js";
  const inSubfolder = scriptSrc.includes("../");
  const root = inSubfolder ? "../" : "";
  const policyHref = root + "policy.html";
  const manifestHref = root + "manifest.webmanifest";
  const iconHref = root + "doc/FreeUniversityTools.png";
  const swHref = root + "sw.js";

  const onPolicyPage = /policy\.html$/i.test(window.location.pathname);
  if (onPolicyPage) return;

  // PWA head tags (once per page)
  function ensureHeadLink(rel, href, attrs) {
    if (document.querySelector(`link[rel="${rel}"][href="${href}"]`)) return;
    const link = document.createElement("link");
    link.rel = rel;
    link.href = href;
    if (attrs) Object.entries(attrs).forEach(([k, v]) => link.setAttribute(k, v));
    document.head.appendChild(link);
  }
  function ensureMeta(name, content) {
    let el = document.querySelector(`meta[name="${name}"]`);
    if (!el) {
      el = document.createElement("meta");
      el.name = name;
      document.head.appendChild(el);
    }
    el.content = content;
  }

  ensureHeadLink("manifest", manifestHref);
  ensureHeadLink("apple-touch-icon", iconHref);
  ensureMeta("mobile-web-app-capable", "yes");
  ensureMeta("apple-mobile-web-app-capable", "yes");
  ensureMeta("apple-mobile-web-app-status-bar-style", "default");
  ensureMeta("apple-mobile-web-app-title", "Free Uni Tools");
  if (!document.querySelector('meta[name="theme-color"]')) {
    ensureMeta("theme-color", "#0a6b5c");
  }

  if ("serviceWorker" in navigator) {
    window.addEventListener("load", () => {
      navigator.serviceWorker.register(swHref).catch(() => {});
    });
  }

  const dock = document.createElement("div");
  dock.id = "legalDock";
  dock.className = "legal-dock";
  dock.setAttribute("role", "group");
  dock.setAttribute("aria-label", "Site actions");

  const badge = document.createElement("a");
  badge.id = "legalBadge";
  badge.className = "legal-badge";
  badge.href = policyHref;
  badge.setAttribute("aria-label", "Terms and Disclaimer");
  badge.textContent = "Terms & Disclaimer";

  const installBtn = document.createElement("button");
  installBtn.id = "installAppBtn";
  installBtn.type = "button";
  installBtn.className = "legal-badge install-app-btn";
  installBtn.setAttribute("aria-label", "Install app to this device");
  installBtn.textContent = "Install app";

  dock.appendChild(badge);
  dock.appendChild(installBtn);
  document.body.appendChild(dock);

  let deferredPrompt = null;
  const isStandalone =
    window.matchMedia("(display-mode: standalone)").matches ||
    window.navigator.standalone === true;

  if (isStandalone) {
    installBtn.hidden = true;
  }

  window.addEventListener("beforeinstallprompt", (e) => {
    e.preventDefault();
    deferredPrompt = e;
    installBtn.hidden = false;
    installBtn.textContent = "Install app";
  });

  window.addEventListener("appinstalled", () => {
    deferredPrompt = null;
    installBtn.textContent = "Installed";
    setTimeout(() => {
      installBtn.hidden = true;
    }, 1600);
  });

  function isIos() {
    return /iphone|ipad|ipod/i.test(navigator.userAgent);
  }

  function closeInstallSheet(immediate) {
    const el = document.getElementById("installHelpModal");
    if (!el) return;
    if (immediate) {
      el.remove();
      return;
    }
    el.classList.remove("is-open");
    window.setTimeout(() => el.remove(), 180);
  }

  function showInstallSheet({ canPrompt }) {
    closeInstallSheet(true);
    const overlay = document.createElement("div");
    overlay.id = "installHelpModal";
    overlay.className = "install-sheet";
    overlay.setAttribute("role", "dialog");
    overlay.setAttribute("aria-modal", "true");
    overlay.setAttribute("aria-labelledby", "installHelpTitle");

    let bodyHtml = "";
    let actionsHtml = "";

    if (canPrompt) {
      bodyHtml = `
        <p class="install-sheet-lede">
          Open Free University Tools like a real app — faster launch, its own window, and a home-screen icon.
        </p>
        <ul class="install-sheet-perks">
          <li>One-tap access from your desktop or phone</li>
          <li>Opens in its own window, away from browser tabs</li>
          <li>Works offline for pages you’ve already visited</li>
        </ul>`;
      actionsHtml = `
        <div class="install-sheet-actions">
          <button type="button" class="install-sheet-secondary" data-install-dismiss>Not now</button>
          <button type="button" class="install-sheet-primary" data-install-confirm>Install</button>
        </div>`;
    } else {
      let steps = "";
      if (isIos()) {
        steps = `
          <ol class="install-sheet-steps">
            <li>Tap <strong>Share</strong> in Safari</li>
            <li>Choose <strong>Add to Home Screen</strong></li>
            <li>Tap <strong>Add</strong> to finish</li>
          </ol>`;
      } else if (/android/i.test(navigator.userAgent)) {
        steps = `
          <ol class="install-sheet-steps">
            <li>Open the browser menu (⋮)</li>
            <li>Tap <strong>Install app</strong> or <strong>Add to Home screen</strong></li>
            <li>Confirm to add Free University Tools</li>
          </ol>`;
      } else {
        steps = `
          <ol class="install-sheet-steps">
            <li>Open your browser menu</li>
            <li>Choose <strong>Install</strong> or <strong>Apps → Install this site as an app</strong></li>
            <li>Confirm to pin it to your desktop or taskbar</li>
          </ol>`;
      }
      bodyHtml = `
        <p class="install-sheet-lede">
          Add Free University Tools to your device for quick access on phones, tablets, and computers.
        </p>
        ${steps}`;
      actionsHtml = `
        <div class="install-sheet-actions">
          <button type="button" class="install-sheet-primary" data-install-dismiss>Got it</button>
        </div>`;
    }

    overlay.innerHTML = `
      <div class="install-sheet-panel">
        <button type="button" class="install-sheet-close" data-install-dismiss aria-label="Close">
          <span aria-hidden="true">×</span>
        </button>
        <div class="install-sheet-brand">
          <img class="install-sheet-icon" src="${iconHref}" width="56" height="56" alt="" decoding="async">
          <div class="install-sheet-brand-text">
            <p class="install-sheet-kicker">Install app</p>
            <h2 id="installHelpTitle">Free University Tools</h2>
            <p class="install-sheet-host">${window.location.host || "freeuniversitytools.com"}</p>
          </div>
        </div>
        ${bodyHtml}
        ${actionsHtml}
      </div>`;

    const onKey = (e) => {
      if (e.key === "Escape") {
        closeInstallSheet();
        document.removeEventListener("keydown", onKey);
      }
    };

    overlay.addEventListener("click", async (e) => {
      if (e.target === overlay || e.target.closest("[data-install-dismiss]")) {
        closeInstallSheet();
        document.removeEventListener("keydown", onKey);
        return;
      }

      const confirmBtn = e.target.closest("[data-install-confirm]");
      if (!confirmBtn || !deferredPrompt) return;

      confirmBtn.disabled = true;
      closeInstallSheet();
      document.removeEventListener("keydown", onKey);

      try {
        deferredPrompt.prompt();
        await deferredPrompt.userChoice;
      } catch (_) {
        /* user dismissed native prompt */
      }
      deferredPrompt = null;
    });

    document.addEventListener("keydown", onKey);
    document.body.appendChild(overlay);
    requestAnimationFrame(() => overlay.classList.add("is-open"));
    overlay.querySelector(".install-sheet-primary")?.focus();
  }

  installBtn.addEventListener("click", () => {
    if (isStandalone) return;
    showInstallSheet({ canPrompt: Boolean(deferredPrompt) });
  });
})();

// Mobile menu toggle
const mobileMenuToggle = document.getElementById("mobileMenuToggle");
const mainNav = document.getElementById("mainNav");

if (mobileMenuToggle && mainNav) {
  function closeMobileNav() {
    mainNav.classList.remove("mobile-open");
    mobileMenuToggle.textContent = "☰";
    mobileMenuToggle.setAttribute("aria-expanded", "false");
    mobileMenuToggle.setAttribute("aria-label", "Open menu");
    document.body.classList.remove("mobile-nav-open");
  }

  function openMobileNav() {
    mainNav.classList.add("mobile-open");
    mobileMenuToggle.textContent = "✕";
    mobileMenuToggle.setAttribute("aria-expanded", "true");
    mobileMenuToggle.setAttribute("aria-label", "Close menu");
    document.body.classList.add("mobile-nav-open");
  }

  mobileMenuToggle.setAttribute("aria-expanded", "false");
  mobileMenuToggle.setAttribute("aria-controls", "mainNav");

  mobileMenuToggle.addEventListener("click", function (e) {
    e.stopPropagation();
    if (mainNav.classList.contains("mobile-open")) {
      closeMobileNav();
    } else {
      openMobileNav();
    }
  });

  mainNav.querySelectorAll(".nav-link, .btn-donate").forEach((link) => {
    link.addEventListener("click", closeMobileNav);
  });

  document.addEventListener("click", function (e) {
    if (!mainNav.classList.contains("mobile-open")) return;
    if (mainNav.contains(e.target) || mobileMenuToggle.contains(e.target)) {
      return;
    }
    closeMobileNav();
  });

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && mainNav.classList.contains("mobile-open")) {
      closeMobileNav();
    }
  });
}

// Desktop dropdown (hamburger "More" menu)
const desktopDropdownToggle = document.getElementById("desktopDropdownToggle");
const navDropdown = document.getElementById("navDropdown");

if (desktopDropdownToggle && navDropdown) {
  desktopDropdownToggle.addEventListener("click", function (e) {
    e.stopPropagation();
    const isOpen = navDropdown.classList.toggle("is-open");
    this.setAttribute("aria-expanded", isOpen);
  });

  navDropdown
    .querySelectorAll(".nav-dropdown-content .nav-link")
    .forEach((link) => {
      link.addEventListener("click", function () {
        navDropdown.classList.remove("is-open");
        desktopDropdownToggle.setAttribute("aria-expanded", "false");
      });
    });

  document.addEventListener("click", function (e) {
    if (
      navDropdown.classList.contains("is-open") &&
      !navDropdown.contains(e.target)
    ) {
      navDropdown.classList.remove("is-open");
      desktopDropdownToggle.setAttribute("aria-expanded", "false");
    }
  });
}

// Header scroll effect (passive + rAF for lighter scroll work)
(function () {
  const header = document.getElementById("header");
  if (!header) return;
  let ticking = false;
  window.addEventListener(
    "scroll",
    function () {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(function () {
        header.classList.toggle("scrolled", window.scrollY > 50);
        ticking = false;
      });
    },
    { passive: true }
  );
})();
