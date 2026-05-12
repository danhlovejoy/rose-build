# aiml2003/ — AIML 2003: Introduction to Natural Language Processing

Source files for Canvas course 26943. Spring 2026, 2nd 8 Weeks.

## Course-Level Files

| File | Purpose |
|------|---------|
| `welcome.html` | Course landing page on Canvas — updated each week to point to the current module |
| `makeup-participation.html` | Standing makeup assignment page (lives outside any module) |
| `glossary.html` | Generated from `glossary.json` by the build pipeline. Edit `glossary.json`, not this file. |
| `aiml2003-module1.imscc` | Canvas Common Cartridge package for Module 1 (initial import) |

Reading-quiz IMSCC packages (`aiml2003-module*-reading-quiz.imscc`) are gitignored — answers are in plaintext.

## Modules

| Directory | Week(s) | Topic | Deliverable |
|-----------|---------|-------|-------------|
| `module1/` | 1–2 | From Prompt to Context Engineering | Setup → Presentation |
| `module2/` | 3 | Hand-Crafted Features (TF-IDF) | Presentation |
| `module3/` | 4 | Learned Embeddings | Demo |
| `module4/` | 5 | Basic RAG | Demo |
| `module5/` | 6 | Evaluating LLMs | Presentation |
| `module6/` | 7 | Simple Agents | Demo |
| `module7/` | 8 | Portfolio & Future | Final Portfolio Presentation |

`slides/` holds NLP-specific lecture decks by week. Shared interactive demos and combined decks live in the project-root `slides/` directory.

## Updating the Welcome Page

When a new module goes live, update `welcome.html`:

1. Copy the current "This Week" link into the Past Modules list (newest at top)
2. Update "This Week" to the new module's Canvas overview page URL
3. Build and upload: `bash build/build.sh aiml2003` then `python3 scripts/upload_to_canvas.py aiml2003`

## Building

```bash
# Build all AIML 2003 pages
bash build/build.sh aiml2003

# Build one module
bash build/build.sh aiml2003/module4
```

Output goes to `build/aiml2003/` (gitignored).
