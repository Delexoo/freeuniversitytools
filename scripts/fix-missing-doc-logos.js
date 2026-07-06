const fs = require('fs');
const path = require('path');

const root = path.join(__dirname, '..');
let html = fs.readFileSync(path.join(root, 'student.html'), 'utf8');
const docFiles = new Set(fs.readdirSync(path.join(root, 'doc')).map((f) => f.toLowerCase()));

const FALLBACK =
  'https://raw.githubusercontent.com/Delexoo/freeuniversitytools/refs/heads/main/doc/FreeUniversityTools.png';

function faviconForHref(href) {
  try {
    const u = new URL(href);
    const host = u.hostname.replace(/^www\./i, '');
    if (host === 'github.com') {
      const owner = u.pathname.split('/').filter(Boolean)[0];
      if (owner) return `https://github.com/${owner}.png?size=64`;
      return 'https://www.google.com/s2/favicons?domain=github.com&sz=128';
    }
    if (host === 'chromewebstore.google.com') {
      return 'https://www.google.com/s2/favicons?domain=google.com&sz=128';
    }
    return `https://www.google.com/s2/favicons?domain=${encodeURIComponent(host)}&sz=128`;
  } catch {
    return FALLBACK;
  }
}

let fixed = 0;
html = html.replace(
  /(<a\s+href="([^"]+)"[^>]*class="tool-link"[^>]*>\s*<img\s+)src="([^"]+)"([^>]*class="tool-link-icon"[^>]*>)/g,
  (match, before, href, src, after) => {
    const docMatch = src.match(/\/doc\/([^"?]+)/);
    if (!docMatch) return match;

    const file = decodeURIComponent(docMatch[1]);
    if (docFiles.has(file.toLowerCase())) return match;

    fixed += 1;
    const icon = faviconForHref(href);
    return `${before}src="${icon}" data-fallback="${icon}"${after}`;
  }
);

fs.writeFileSync(path.join(root, 'student.html'), html);
console.log(`Replaced ${fixed} missing bundled logos with live favicons`);
