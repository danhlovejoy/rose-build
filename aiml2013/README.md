# aiml2013/ — AIML 2013: Introduction to Computer Vision

Source files for Canvas course 26944. Spring 2026, 2nd 8 Weeks.

**Do not edit files in this directory directly unless they are source HTML files.** Generated files (`glossary.html`) are overwritten by the build.

## Files

| File | Purpose |
|------|---------|
| `welcome.html` | Course landing page on Canvas — updated each week to point to the current module |
| `makeup-participation.html` | Standing makeup assignment page (lives outside any module) |
| `glossary.html` | **Generated — do not edit.** Rebuilt from `glossary.json` by the build pipeline. |
| `aiml2013-module1.imscc` | Canvas Common Cartridge package for Module 1 (for Canvas import) |

## Updating the Welcome Page

When a new module goes live, update `welcome.html`:
1. Copy the current "This Week" link into the Past Modules list (newest at top)
2. Update "This Week" to the new module's Canvas overview page URL
3. Build and upload: `bash build/build.sh aiml2013` then run `upload_to_canvas.py`

## Subdirectories

| Directory | Contents |
|-----------|---------|
| `module1/` | Week 1–2: Vision & Images |
| `module2/` | Week 3: Hand-Crafted Features (HOG) |
| `slides/` | Lecture slides by week |

## Building

```bash
# Build all AIML 2013 pages
bash build/build.sh aiml2013

# Build one module
bash build/build.sh aiml2013/module2
```

Output goes to `build/output/aiml2013/`.
