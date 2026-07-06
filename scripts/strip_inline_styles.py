"""Strip inline <style> blocks and ensure external CSS links on inner pages."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILES = ["student.html", "about.html", "contact.html", "donate.html", "report.html"]

CSS_LINKS = """  <link rel="stylesheet" href="css/site.css">
  <link rel="stylesheet" href="css/nav.css">"""

STUDENT_EXTRA = """  <link rel="stylesheet" href="css/toc.css">"""

STYLE_RE = re.compile(r"\s*<style>.*?</style>\s*", re.DOTALL)

MODAL_OLD = re.compile(
    r'<div id="piracyDisclaimerModal" style="[^"]*">.*?</div>\s*</div>\s*</div>',
    re.DOTALL,
)

MODAL_NEW = """<div id="piracyDisclaimerModal" class="modal-overlay" role="dialog" aria-modal="true" aria-labelledby="piracyModalTitle">
    <div class="modal-card">
      <h2 id="piracyModalTitle">Important Disclaimer</h2>
      <p>Disclaimer: For educational purposes only. No support for piracy.</p>
      <p>I have no control over any third-party sites or their content. Use them at your own risk.</p>
      <p><strong>For your safety, it's best to use a VPN and the Redirect Blocker extension included on this website.</strong></p>
      <div class="modal-actions">
        <button id="piracyCancelBtn" type="button" class="modal-btn">Cancel</button>
        <button id="piracyContinueBtn" type="button" class="modal-btn modal-btn--primary">I Understand, Continue</button>
      </div>
    </div>
  </div>"""

MODAL_SCRIPT_OLD = re.compile(
    r"<script>\s*// Piracy / third-party warning modal logic.*?</script>\s*",
    re.DOTALL,
)

MODAL_SCRIPT_NEW = """<script>
    (function () {
      const modal = document.getElementById('piracyDisclaimerModal');
      if (!modal) return;
      const continueBtn = document.getElementById('piracyContinueBtn');
      const cancelBtn = document.getElementById('piracyCancelBtn');
      const warningLinks = document.querySelectorAll('.piracy-warning-link');
      let pendingHref = null;

      function openModal(href) {
        pendingHref = href;
        modal.classList.add('is-open');
      }

      function closeModal() {
        modal.classList.remove('is-open');
        pendingHref = null;
      }

      warningLinks.forEach(link => {
        link.addEventListener('click', function (e) {
          e.preventDefault();
          openModal(this.getAttribute('href'));
        });
      });

      if (continueBtn) {
        continueBtn.addEventListener('click', function () {
          if (pendingHref) {
            window.open(pendingHref, '_blank', 'noopener,noreferrer');
          }
          closeModal();
        });
      }

      if (cancelBtn) cancelBtn.addEventListener('click', closeModal);

      modal.addEventListener('click', function (e) {
        if (e.target === modal) closeModal();
      });
    })();
  </script>
"""


def ensure_css_links(text: str, is_student: bool) -> str:
    # Remove duplicate css link blocks
    text = re.sub(
        r'\s*<link rel="stylesheet" href="css/site\.css">\s*'
        r'<link rel="stylesheet" href="css/nav\.css">\s*'
        r'(?:<link rel="stylesheet" href="css/toc\.css">\s*)?',
        "\n",
        text,
    )
    insert = CSS_LINKS + ("\n" + STUDENT_EXTRA if is_student else "")
    return text.replace("</head>", insert + "\n</head>", 1)


def process(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = STYLE_RE.sub("\n", text)
    text = ensure_css_links(text, path.name == "student.html")

    if path.name == "student.html":
        text = MODAL_OLD.sub(MODAL_NEW, text)
        text = MODAL_SCRIPT_OLD.sub(MODAL_SCRIPT_NEW, text)

    path.write_text(text, encoding="utf-8")
    print(f"Updated {path.name}")


def main():
    for name in FILES:
        process(ROOT / name)


if __name__ == "__main__":
    main()
