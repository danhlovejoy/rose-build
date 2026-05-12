# Rose State College — AIML Course Materials

Curriculum for two concurrent 8-week courses, Spring 2026 (2nd 8 Weeks):

- **AIML 2003** — Introduction to Natural Language Processing (Canvas course 26943)
- **AIML 2013** — Introduction to Computer Vision (Canvas course 26944)

Instructor: Dan Lovejoy (dlovejoy@rose.edu)

---

## Project Structure

```
rose/
├── build.conf                 ← delivery mode setting (concurrent vs. standalone)
├── course-styles.css          ← single CSS source of truth for all pages
├── glossary.json              ← all glossary terms for both courses
├── CLAUDE.md                  ← full project context for AI assistants
├── build/                     ← build pipeline scripts and generated output
├── docs/                      ← standards docs, Canvas setup guide, push checklist
│   ├── MODULE-STANDARDS.md    ← how to build any module
│   ├── WRITING-STANDARDS.md   ← banned phrases, formatting rules, tone
│   └── DEMO-STANDARDS.md      ← how to build interactive slide demos
├── scripts/                   ← Canvas API helpers (upload_to_canvas.py, create_module_assignments.py, split_szeliski.py)
├── templates/                 ← reusable HTML page templates
├── aiml2003/                  ← NLP course source files
├── aiml2013/                  ← CV course source files
├── readings/                  ← shared reading materials (gitignored where copyrighted)
└── slides/                    ← shared interactive demos and lecture decks
```

---

## Build Process

Canvas strips `<style>` and `<link>` tags from wiki pages. The build pipeline inlines CSS into each element's `style=""` attribute and outputs body-only HTML for Canvas upload.

**Prerequisites:** Python 3.8+ (stdlib only — no external packages required).

### Commands

```bash
# Build everything (reads delivery_mode from build.conf)
cd rose && bash build/build.sh

# Build one course
bash build/build.sh aiml2003
bash build/build.sh aiml2013

# Build one module
bash build/build.sh aiml2003/module2

# Override delivery mode for a single run
bash build/build.sh --standalone        # strip dual-enrollment content
bash build/build.sh --concurrent        # include all dual-enrollment content

# Audit all concurrent-only content across the project
python3 build/audit_concurrent.py
```

Output goes to `build/aiml2003/` and `build/aiml2013/` (both gitignored). Upload to Canvas via `python3 scripts/upload_to_canvas.py` or paste into the Canvas HTML editor.

### Delivery Mode

Set `delivery_mode` in `build.conf` before building for distribution:

- `concurrent` (default) — both courses taught together; bridge boxes and combined labs included
- `standalone` — single-course delivery; all `data-concurrent="true"` content stripped

**Never change `build.conf` to `standalone` while students are actively enrolled in both courses.**

---

## Editing Content

Edit source HTML files directly. They render correctly in a browser for local preview. Run the build before uploading to Canvas.

**Read before making changes:**
- `docs/MODULE-STANDARDS.md` — module structure, file numbering, page types, rubrics, participation model
- `docs/WRITING-STANDARDS.md` — banned phrases, formatting rules, tone
- `docs/DEMO-STANDARDS.md` — conventions for interactive slide demos in `slides/`
- `CLAUDE.md` — full project conventions, build system, Canvas details, correction protocol

**Never put `<style>` blocks in source HTML files** — all CSS goes in `course-styles.css`.

---

## Advancing to a New Week

When a new module is ready to go live:

1. Update `aiml2003/welcome.html` and `aiml2013/welcome.html`:
   - Move the current "This Week" link into the Past Modules list
   - Update "This Week" to point to the new module's overview page
2. Build: `bash build/build.sh`
3. Upload the updated welcome pages to Canvas
