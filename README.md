# Logo assets (doc folder)

This folder contains **PNG logos** for tools and services used across the site. All assets are referenced in HTML as `docs/FileName.png` and rewritten at runtime to the GitHub raw URL.

## Adding or updating logos

1. **Automated (recommended)**  
   From the project root, run:
   ```bash
   python scripts/download_logos.py
   ```
   This uses Clearbit and Google Favicon APIs to fetch logos and saves them here as PNG. Install Pillow for non-PNG conversion: `pip install Pillow`.

2. **Manual**  
   Add or replace a PNG file in this folder. Use the exact filename referenced in the HTML (e.g. `AnnasArchive.png`, `Tubi.png`). Keep filenames in PascalCase and use `.png` for consistency.

## Naming convention

- One file per tool/service (e.g. `Todoist.png`, `Symbolab.png`).
- Name matches the `docs/` reference in `powerful.html` and `student.html`.
- Generic fallback when a logo is missing: `FreeUniversityTools.png`.

## Failed downloads

If the script could not fetch a logo (e.g. 404 or network), the site still works: the image `onerror` handler falls back to `FreeUniversityTools.png`. You can add a proper logo later by placing the correct `.png` in this folder.
