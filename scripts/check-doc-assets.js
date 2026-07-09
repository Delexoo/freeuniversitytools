const fs = require('fs');
const path = require('path');

const root = path.join(__dirname, '..');
const html = fs.readFileSync(path.join(root, 'student.html'), 'utf8');
const docFiles = new Set(
 fs.readdirSync(path.join(root, 'doc')).map((f) => f.toLowerCase())
);

const re = /doc\/([^"?]+)/g;
const missing = new Set();
let m;
while ((m = re.exec(html))) {
 const file = decodeURIComponent(m[1]).toLowerCase();
 if (!docFiles.has(file)) missing.add(m[1]);
}

console.log('Missing doc assets:', missing.size);
[...missing].sort().slice(0, 40).forEach((f) => console.log(' -', f));
