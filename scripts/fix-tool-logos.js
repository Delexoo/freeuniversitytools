const fs = require('fs');
const path = require('path');

const studentPath = path.join(__dirname, '..', 'student.html');
let html = fs.readFileSync(studentPath, 'utf8');

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

// Remove inline onerror, tool-icons.js handles fallbacks
html = html.replace(/\s+onerror="this\.onerror=null;this\.src='[^']*'"/g, '');

// Ensure data-fallback on every tool icon
html = html.replace(
 /(<a\s+href="([^"]+)"[^>]*class="tool-link"[^>]*>\s*<img\s+)([^>]*class="tool-link-icon"[^>]*>)/g,
 (match, before, href, imgTag) => {
 if (/data-fallback=/.test(imgTag)) return match;
 const fallback = faviconForHref(href);
 return `${before}${imgTag.replace('<img ', `<img data-fallback="${fallback}" `)}`;
 }
);

// Known missing bundled assets → use live favicon as primary
const missingAssets = ['DesignArena.png', 'Obsidian.png'];
for (const file of missingAssets) {
 const re = new RegExp(
 `(<a href="([^"]+)"[^>]*class="tool-link"[^>]*>\\s*<img src=")[^"]*${file.replace('.', '\\.')}("[^>]*class="tool-link-icon")`,
 'g'
 );
 html = html.replace(re, (_, start, href, end) => {
 return `${start}${faviconForHref(href)}"${end}`;
 });
}

fs.writeFileSync(studentPath, html);
const icons = (html.match(/class="tool-link-icon"/g) || []).length;
const onerrors = (html.match(/tool-link-icon[^>]*onerror/g) || []).length;
console.log(`Icons: ${icons}, inline onerror left: ${onerrors}`);
