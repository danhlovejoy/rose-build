# build/ — Build Pipeline

This directory contains the scripts that transform source HTML into Canvas-ready output. Run `build.sh` from the project root (`rose/`) after editing any source files.

## Scripts

| File | Purpose |
|------|---------|
| `build.sh` | Main orchestrator — runs glossary generation, CSS inlining, glossary linking |
| `inline_css.py` | Inlines `course-styles.css` into element `style=""` attributes; extracts `<body>` content only |
| `build_glossary.py` | Generates `aiml2003/glossary.html` and `aiml2013/glossary.html` from `glossary.json` |
| `build_glossary_links.py` | Auto-links first occurrence of each glossary term in built output |
| `strip_concurrent.py` | Removes `data-concurrent="true"` elements in standalone mode; detects file-level concurrent markers |
| `audit_concurrent.py` | Reports all concurrent-only content across the project; flags untagged bridge boxes |
| `course-config.json` | Canvas page slug → source file mappings used by `upload_to_canvas.py` |
| `course-config.template.json` | Template for adding new pages to the config |

## Output

Built files go to `build/output/`. See the README there.

## Key Rules

- Never edit files in `build/output/` — they are generated and will be overwritten on the next build
- The build is deterministic: no LLM, no network calls, no external dependencies
- CSS custom properties (`var(--name)`) are resolved at build time
- Descendant CSS selectors (e.g., `.hero h2`) are resolved using DOM-aware ancestor tracking
- Glossary auto-linking runs after CSS inlining, on the built output files

## Delivery Mode

Controlled by `delivery_mode` in `build.conf` (project root). Override per-run with `--standalone` or `--concurrent` flags. See the root README for details.
