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

// Fixed legal / disclaimer badge (bottom-right on every page)
(function () {
  if (document.getElementById("legalBadge")) return;

  const script =
    document.currentScript ||
    document.querySelector('script[src*="common.js"]');
  const scriptSrc =
    script && script.getAttribute("src")
      ? script.getAttribute("src")
      : "js/common.js";
  const inSubfolder = scriptSrc.includes("../");
  const policyHref = inSubfolder ? "../policy.html" : "policy.html";

  const onPolicyPage = /policy\.html$/i.test(window.location.pathname);
  if (onPolicyPage) return;

  const badge = document.createElement("a");
  badge.id = "legalBadge";
  badge.className = "legal-badge";
  badge.href = policyHref;
  badge.setAttribute("aria-label", "Terms and Disclaimer");
  badge.textContent = "Terms & Disclaimer";

  document.body.appendChild(badge);
})();

// Mobile menu toggle
const mobileMenuToggle = document.getElementById("mobileMenuToggle");
const mainNav = document.getElementById("mainNav");

if (mobileMenuToggle && mainNav) {
  function closeMobileNav() {
    mainNav.classList.remove("mobile-open");
    mobileMenuToggle.textContent = "☰";
    document.body.classList.remove("mobile-nav-open");
  }

  function openMobileNav() {
    mainNav.classList.add("mobile-open");
    mobileMenuToggle.textContent = "✕";
    document.body.classList.add("mobile-nav-open");
  }

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

// Header scroll effect
window.addEventListener("scroll", function () {
  const header = document.getElementById("header");
  if (!header) return;
  if (window.scrollY > 50) {
    header.classList.add("scrolled");
  } else {
    header.classList.remove("scrolled");
  }
});
