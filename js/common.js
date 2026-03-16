// Mobile menu toggle
const mobileMenuToggle = document.getElementById('mobileMenuToggle');
const mainNav = document.getElementById('mainNav');

if (mobileMenuToggle && mainNav) {
  mobileMenuToggle.addEventListener('click', function() {
    mainNav.classList.toggle('mobile-open');
    this.textContent = mainNav.classList.contains('mobile-open') ? '✕' : '☰';
  });

  mainNav.querySelectorAll('.nav-link, .btn-donate').forEach(link => {
    link.addEventListener('click', function() {
      mainNav.classList.remove('mobile-open');
      mobileMenuToggle.textContent = '☰';
    });
  });
}

// Desktop dropdown (hamburger "More" menu)
const desktopDropdownToggle = document.getElementById('desktopDropdownToggle');
const navDropdown = document.getElementById('navDropdown');

if (desktopDropdownToggle && navDropdown) {
  desktopDropdownToggle.addEventListener('click', function(e) {
    e.stopPropagation();
    const isOpen = navDropdown.classList.toggle('is-open');
    this.setAttribute('aria-expanded', isOpen);
  });

  navDropdown.querySelectorAll('.nav-dropdown-content .nav-link').forEach(link => {
    link.addEventListener('click', function() {
      navDropdown.classList.remove('is-open');
      desktopDropdownToggle.setAttribute('aria-expanded', 'false');
    });
  });

  document.addEventListener('click', function(e) {
    if (navDropdown.classList.contains('is-open') && !navDropdown.contains(e.target)) {
      navDropdown.classList.remove('is-open');
      desktopDropdownToggle.setAttribute('aria-expanded', 'false');
    }
  });
}

// Header scroll effect
window.addEventListener('scroll', function() {
  const header = document.getElementById('header');
  if (!header) return;
  if (window.scrollY > 50) {
    header.classList.add('scrolled');
  } else {
    header.classList.remove('scrolled');
  }
});
