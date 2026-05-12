# aiml2013/ — AIML 2013: Introduction to Computer Vision

Source files for Canvas course 26944. Spring 2026, 2nd 8 Weeks.

## Course-Level Files

| File | Purpose |
|------|---------|
| `welcome.html` | Course landing page on Canvas — updated each week to point to the current module |
| `makeup-participation.html` | Standing makeup assignment page (lives outside any module) |
| `glossary.html` | Generated from `glossary.json` by the build pipeline. Edit `glossary.json`, not this file. |
| `aiml2013-module1.imscc` | Canvas Common Cartridge package for Module 1 (initial import) |

Reading-quiz IMSCC packages (`aiml2013-module*-reading-quiz.imscc`) are gitignored — answers are in plaintext.

## Modules

| Directory | Week(s) | Topic | Deliverable |
|-----------|---------|-------|-------------|
| `module1/` | 1–2 | Vision & Images | Setup → Presentation |
| `module2/` | 3 | Hand-Crafted Features (HOG) | Presentation |
| `module3/` | 4 | Learned Embeddings | Demo |
| `module4/` | 5 | Visual Similarity | Demo |
| `module5/` | 6 | CV Metrics & Bias | Demo |
| `module6/` | 7 | Generative Vision | Presentation |
| `module7/` | 8 | Portfolio & Future | Final Portfolio Presentation |

`slides/` holds CV-specific lecture decks by week. Shared interactive demos and combined decks live in the project-root `slides/` directory.

## Updating the Welcome Page

When a new module goes live, update `welcome.html`:

1. Copy the current "This Week" link into the Past Modules list (newest at top)
2. Update "This Week" to the new module's Canvas overview page URL
3. Build and upload: `bash build/build.sh aiml2013` then `python3 scripts/upload_to_canvas.py aiml2013`

## Building

```bash
# Build all AIML 2013 pages
bash build/build.sh aiml2013

# Build one module
bash build/build.sh aiml2013/module4
```

Output goes to `build/aiml2013/` (gitignored).
