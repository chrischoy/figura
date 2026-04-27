---
description: Export every PDF figure in a directory to PNG at 300 DPI (for board uploads, Slack, slide decks, README embeds).
argument-hint: <input-dir> [output-dir]
allowed-tools: ["Bash"]
---

Export every PDF in `$ARGUMENTS` to PNG at 300 DPI. Expected form: `<input-dir> [output-dir]`. Defaults output-dir to input-dir.

If `$ARGUMENTS` is empty, ask the user which directory holds the PDFs. Do not improvise.

Use the bundled helper:

```bash
bash skills/figura/scripts/export_png_bundle.sh <input-dir> [output-dir]
```

The script:
- Walks `<input-dir>/*.pdf` (no recursion)
- Renders each via `pdftoppm -r 300 -png` (poppler — `brew install poppler` if missing)
- Names the output `<input-dir-or-output-dir>/<basename>.png`
- Skips PDFs whose PNG is already newer than the source (idempotent)
- Reports counts at the end

Use cases:
- Board / Slack / Discord uploads (PNG only)
- README embedding (Markdown can't render PDF inline)
- Slide deck assets
- Sharing print-size previews with collaborators who don't have a PDF viewer

After the script runs, report how many PNGs were rendered vs skipped. If a PDF failed to render, `pdftoppm` will print a warning — surface it to the user.

This command is read-mostly: it doesn't modify the source PDFs. Output PNGs may overwrite existing PNGs in the output directory if their source PDF is newer.
