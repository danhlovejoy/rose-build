# CLAUDE.md

## Project

Curriculum development for two concurrent 8-week courses at Rose State College, Spring 2026 (2nd 8 Weeks):

- **AIML 2003** — Introduction to Natural Language Processing (Canvas course 26943)
- **AIML 2013** — Introduction to Computer Vision (Canvas course 26944)

Instructor: Dan Lovejoy (dlovejoy@rose.edu). Both courses share the same instructor, the same Thursday lab (6–8 PM Zoom), many of the same setup guides, and an optional overlapping assignment track for dual-enrolled students.

## File Structure

```
rose/
├── CLAUDE.md                  ← you are here
├── MODULE-STANDARDS.md        ← how to build any module
├── WRITING-STANDARDS.md       ← lexical bans, formatting rules, tone
├── build.conf                 ← delivery mode config (concurrent vs standalone)
├── course-styles.css          ← single source of truth for all CSS
├── glossary.json              ← single glossary source: terms tagged nlp, cv, or both
├── docs/
│   ├── CANVAS-PUSH-CHECKLIST.md
│   └── CANVAS-SETUP-GUIDE.html ← instructor reference for Canvas configuration
├── scripts/
│   ├── upload_to_canvas.py     ← API uploader: pages/wiki content
│   ├── create_module_assignments.py ← API script: assignments, discussions, module structure
│   ├── create_module2_assignments.py
│   └── fix_module2_structure.py
├── build/
│   ├── build.sh               ← orchestrator: ./build.sh [target]
│   ├── build_glossary.py      ← generates glossary.html per course from glossary.json
│   ├── build_glossary_links.py← auto-links glossary terms in built output
│   ├── inline_css.py          ← CSS inliner (Python, stdlib only)
│   ├── strip_concurrent.py    ← removes data-concurrent elements in standalone mode
│   ├── audit_concurrent.py    ← reports all concurrent content across the project
│   ├── course-config.json     ← Canvas page slug → source file mappings
│   └── output/                ← Canvas-ready HTML (generated, do not edit)
├── templates/                 ← reusable HTML templates with {{PLACEHOLDER}} syntax
│   ├── README.md
│   ├── week-overview.html
│   ├── week-readings.html
│   ├── week-assignments-presentation.html
│   ├── week-assignments-demo.html
│   └── week-ethics.html
├── slides/                    ← shared slide assets (not built by build.sh)
├── aiml2003/
│   ├── welcome.html           ← Canvas landing page: "This Week" + past modules
│   ├── glossary.html          ← generated from glossary.json (do not edit)
│   ├── makeup-participation.html  ← standalone, not inside any module
│   ├── aiml2003-module1.imscc ← Canvas Common Cartridge for Module 1 import
│   ├── slides/                ← NLP lecture slides by week
│   ├── module1/               ← Week 1–2: From Prompt to Context Engineering
│   │   ├── 00-welcome.html
│   │   ├── 02-week2-readings.html
│   │   ├── 03-google-colab-setup.html
│   │   ├── 03a-gemini-api-setup.html
│   │   ├── 03b-notebooklm-setup.html
│   │   ├── 04-github-account-setup.html
│   │   ├── 05-colab-github-integration.html
│   │   ├── 06-week2-assignments.html
│   │   ├── 07-discussion-ethics-week1.html
│   │   ├── lab1-option-a-factcheck.html
│   │   ├── lab1-option-b-tone.html
│   │   └── lab1-option-c-extraction.html
│   └── module2/               ← Week 3: Hand-Crafted Features (TF-IDF)
│       ├── 01-overview.html
│       ├── 02-readings.html
│       ├── 06-assignments.html
│       ├── 07-ethics.html
│       ├── lab2-nlp-sentiment.html
│       ├── lab2-nlp-sentiment-challenge.html
│       ├── lab2-combined-how-machines-read.html  ← concurrent-only
│       └── lab2-combined-challenge.html          ← concurrent-only
└── aiml2013/
    ├── welcome.html           ← Canvas landing page: "This Week" + past modules
    ├── glossary.html          ← generated from glossary.json (do not edit)
    ├── makeup-participation.html  ← standalone, not inside any module
    ├── aiml2013-module1.imscc ← Canvas Common Cartridge for Module 1 import
    ├── slides/                ← CV lecture slides and visual assets by week
    ├── module1/               ← Week 1–2: Vision & Images
    │   ├── 01-welcome.html
    │   ├── 03-setup-google-colab.html
    │   ├── 04-setup-gemini-api.html
    │   ├── 05-setup-notebooklm.html
    │   ├── 06-setup-github.html
    │   ├── 07-setup-colab-github.html
    │   ├── 08-readings-week1.html
    │   ├── 09-assignments-week2.html
    │   ├── 10-lab1-edge-detection.html
    │   └── 11-ethics-week1.html
    └── module2/               ← Week 3: Hand-Crafted Features (HOG)
        ├── 01-overview.html
        ├── 02-readings.html
        ├── 06-assignments.html
        ├── 07-ethics.html
        ├── lab2-cv-hog.html
        ├── lab2-cv-hog-challenge.html
        ├── lab2-combined-how-machines-read.html  ← concurrent-only
        └── lab2-combined-challenge.html          ← concurrent-only
```

## Standards Documents

Read these before making any content changes:

- **MODULE-STANDARDS.md** — Module structure, file numbering (sequential, not fixed slots), page types, dates/deadlines, rubric display format with Canvas links, participation 80/20 model, lab sheet structure, readings page structure, ethics discussion format, CSS design system.
- **WRITING-STANDARDS.md** — Banned frames, banned AI tells, banned buffer phrases, encouraged precision vocabulary, formatting constraints (list counts, paragraph rhythm, no bold in prose), banned tone patterns.

## Key Conventions

**Presentation time:** In tables and labels, use the en-dash numeric range: "3–5 minutes", rubric window "2:30–5:30". In prose, write it out: "three to five minutes."

**Due dates:** State the exact date in the banner: "By Tuesday, [Month Day] (by class time)." Never "Monday 11:59 PM." Never append "See the Syllabus for exact dates" — the date is already in the banner.

**Class times:** AIML 2003 meets Tuesdays 5:30–6:50 PM. AIML 2013 meets Tuesdays 7:00–8:20 PM. Both share Thursday lab 6:00–8:00 PM (Zoom).

**Participation:** 80% attendance/engagement + 20% ethics post. Makeup post (48 hours, 500+ words) covers the 80% only. Ethics post always required separately.

**Lab code scaffolds:** Include "training wheels" warning. Later labs won't have scaffolds. Bonus section worth 10 extra credit points. Final section is presentation prep, not a written reflection.

**Rubrics:** Show abbreviated summaries in assignment pages. Link to full Canvas rubrics. Each rubric exists in both courses — use the correct course ID in links (26943 for NLP, 26944 for CV).

**Welcome page (weekly update):** `aiml2003/welcome.html` and `aiml2013/welcome.html` serve as Canvas course landing pages. Each week when a new module goes live: (1) copy the current "This Week" link into the Past Modules list, newest at top; (2) update "This Week" to the new module's Canvas overview page URL; (3) build and upload the welcome page. These files build normally via `build.sh` and are uploaded to Canvas like any other page.

**Readings:** Never due before the first class of a module. Due before the following Tuesday.

**Lab framing:** "In the readings and in class, you learned..." — not "Last week you learned..."

**CV images:** Display inline via matplotlib. Include resize cell (800px longest side). Tip box explaining students don't need to save images as files.

**Dual enrollment:** Bridge boxes connect parallel topics across courses. Combined assignments start at Week 3, not Week 1.

**Separability and the concurrent content system:** These courses are being built and taught concurrently this semester, but they may not always be. All cross-course content must be cleanly separable so a future instructor can strip it out without breaking anything.

The build pipeline supports two delivery modes, configured in `build.conf` at the project root:
- **Concurrent** (default): Both courses offered together. All dual-enrollment content included.
- **Standalone** (`delivery_mode=standalone` in `build.conf`): Single-course delivery. All elements marked `data-concurrent="true"` are stripped, and file-level concurrent files are excluded entirely.

CLI flags `--standalone` and `--concurrent` override `build.conf` for a single run.

**⚠️ CRITICAL:** The default build mode is **concurrent**. When packaging a course for independent delivery, you **must** set `delivery_mode=standalone` in `build.conf` (or pass `--standalone`) or the output will contain cross-course references that confuse students.

Mark concurrent content with `data-concurrent="true"`:
- **Element-level** — bridge boxes, combined assignment references, combined lab bullets in overviews:
  ```html
  <div class="bridge-box" data-concurrent="true">
    <strong>Taking AIML 2013 too?</strong>
    <p>A combined lab is available...</p>
  </div>
  ```
- **File-level** — entire files that only exist for dual-enrolled students (combined labs). Add a comment before `<!DOCTYPE html>`:
  ```html
  <!-- concurrent-only: requires dual enrollment in AIML 2003 + AIML 2013 -->
  <!DOCTYPE html>
  ```
  These files are excluded entirely from build output in standalone mode.

Content rules (unchanged, now enforced by the build):
- Bridge boxes (purple, `.bridge-box`) must be self-contained HTML blocks that can be deleted without affecting surrounding content.
- Combined assignment references must live in their own sections or paragraphs, never woven into the description of the individual assignment.
- The Thursday lab is currently shared between both courses. Any reference to the shared lab must not assume the other course exists — say "combined lab" or "shared lab session," not "the AIML 2003/2013 lab."
- No page should require content from the other course to make sense. Each course must stand alone if the bridge/combined content is removed.

**Audit tool:** Run `python3 build/audit_concurrent.py` to see all concurrent content across the project, including any bridge boxes that may be missing the `data-concurrent` attribute.

**GenAI policy:** Students expected to use GenAI. Two hard rules: no sharing university credentials with AI agents, no uploading PII/sensitive data.

**Inline glossary links:** The build pipeline auto-links the first occurrence of each glossary term on every page. Terms get a dotted purple underline and a native browser tooltip (no JS). To suppress auto-linking on a container (e.g., a code example that uses a term as a variable name, or a heading that shouldn't be linked), add `data-no-glossary="true"` to the wrapper element:
```html
<div class="spec-box" data-no-glossary="true">
  <!-- term mentions here will NOT be auto-linked -->
</div>
```
The auto-linker skips content inside `<code>`, `<pre>`, `<a>`, and `<h1>`–`<h6>` tags automatically. Use `data-no-glossary` for other containers where linking would be misleading or distracting. When you reference a term in prose for the first time on a page, do not manually wrap it — the build handles it.


## Module-Building Workflow

When building a new module, follow this sequence:

1. **Review the syllabus for the week.** Check the week-by-week deliverable table (Presentation vs. Demo), confirm the topic fits the 8-week arc, and identify what students should be able to do by the end of the week. Modify the syllabus if the progression needs adjustment — this is a first-time course.

2. **Build the labs, focused on outcomes.**
   - **Separate labs are always required** — one for NLP, one for CV. Each must stand alone for students taking only one course.
   - **Build a combined lab for dual-enrolled students if the topics connect naturally.** The combined lab is one notebook covering both domains, submitted to both courses via the same GitHub URL. If the week's topics are too far apart to combine meaningfully, skip the combined lab. Combined labs start at Week 3, not before.
   - **Each lab gets two versions:** a training wheels version (full code scaffold) and a challenge version (cell specification boxes only). Build the training wheels version first, then derive the challenge version from it.

3. **Find appropriate readings and videos.**
   - Preference the Szeliski textbook (Computer Vision: Algorithms and Applications, 2nd Ed.) for CV readings. Reference specific sections and page numbers.
   - Use free, accessible resources. Prefer official documentation (sklearn, scikit-image), established video channels (3Blue1Brown, Computerphile, StatQuest), and open-access papers.
   - Keep optional/bonus readings to the bare minimum — one per course per week.
   - Structure per MODULE-STANDARDS.md readings page format: framing box, NotebookLM reminder, resource cards with tags, preview section if needed, discussion prep questions, bridge box.

4. **Build the remaining module pages** — overview, assignment sheet, ethics discussion — per MODULE-STANDARDS.md.

## Canvas Details

| | AIML 2003 (NLP) | AIML 2013 (CV) |
|--|--|--|
| Course ID | 26943 | 26944 |
| Syllabus | `/courses/26943/external_tools/13895` | `/courses/26944/external_tools/13895` |
| Presentation Rubric | `/courses/26943/rubrics/65800` | `/courses/26944/rubrics/66062` |
| Demo Rubric | `/courses/26943/rubrics/65794` | `/courses/26944/rubrics/66063` |
| Repo Rubric | `/courses/26943/rubrics/66034` | `/courses/26944/rubrics/66064` |
| Existing Survey Quiz | `/courses/26943/quizzes/168912` | TBD |

## Grade Breakdown (Both Courses)

Participation 20%, GitHub Repos 25%, In-Class Presentations 15%, Demos 25%, Final Reflection 5%, Final Portfolio Presentation 10%.

## Canvas Assignment Groups

Canvas must be configured to weight grades by Assignment Group. Go to Assignments → Assignment Groups and enable "Weight final grade based on assignment groups." Create these groups:

| Assignment Group | Weight |
|--|--|
| Participation | 20% |
| GitHub Repos | 25% |
| Presentations | 15% |
| Demos | 25% |
| Final Reflection | 5% |
| Final Portfolio | 10% |

**Participation group — per-week structure:** Each week has two items in the Participation group. Point values encode the 80/20 split automatically — no additional Canvas weighting needed.

- **"Week X Participation"** — Assignment, submission type "No Submission," 80 points. Graded manually from the gradebook based on attendance and in-class engagement.
- **"Week X Ethics Discussion"** — Discussion Topic, 20 points.

Each week totals 100 Participation points. Canvas computes the group grade as points earned / points possible, so the 80/20 ratio is preserved across all weeks.

## Week-by-Week Deliverable Types

| Week | NLP | CV |
|------|-----|-----|
| 1 | Setup | Setup |
| 2 | Presentation | Presentation |
| 3 | Presentation | Presentation |
| 4 | Demo | Demo |
| 5 | Demo | Demo |
| 6 | Presentation | Demo |
| 7 | Demo | Presentation |
| 8 | Final Portfolio | Final Portfolio |

## CSS Design System

All styles live in `course-styles.css` at the project root. Source HTML files reference it via `<link rel="stylesheet" href="../../course-styles.css">` (path relative to file location). Do not put `<style>` blocks in HTML source files.

Primary: `#1a3a5c`. Accent: `#2e7d32`. Light bg: `#f7f9fc`. Border: `#d0d7de`. Warning: `#fff3e0`/`#e65100`. Syllabus notice: `#e8eaf6`/`#3949ab`. Bridge box: `#ede7f6`/`#5e35b1`. Font: system stack. Max width: 820–860px.

## Build Process

Canvas strips `<style>` and `<link>` tags from wiki pages. The build pipeline inlines CSS into each element's `style=""` attribute and extracts body-only HTML for Canvas upload.

**Workflow:**
1. Edit source HTML files (which reference `course-styles.css` via `<link>`)
2. Edit `course-styles.css` for any style changes (single source of truth)
3. Run the build: `cd rose && bash build/build.sh`
4. Canvas-ready output appears in `build/output/`
5. Upload to Canvas via API or manual paste into the HTML editor

**Build commands:**
- `bash build/build.sh` — build everything (concurrent mode, default)
- `bash build/build.sh aiml2003/module1` — build one module
- `bash build/build.sh aiml2003` — build one course (all modules)
- `bash build/build.sh --standalone` — build everything for single-course delivery (strips concurrent content)
- `bash build/build.sh --standalone aiml2003` — standalone build, one course
- `python3 build/audit_concurrent.py` — report all concurrent content across the project
- `python3 scripts/upload_to_canvas.py` — upload all built pages to Canvas wiki
- `python3 scripts/upload_to_canvas.py aiml2003` — upload one course
- `python3 scripts/create_module_assignments.py <course> <module_num> <due_date>` — create Canvas artifacts for a module (see below)

**`scripts/create_module_assignments.py` — Canvas artifact automation:**

Creates all four Canvas artifacts for a module (Participation assignment, Ethics Discussion, Presentation/Demo assignment, GitHub Repo assignment), wires them into the Canvas module structure, and publishes everything. Also removes stale artifacts if the module was previously set up under different names.

```
python3 scripts/create_module_assignments.py aiml2003 2 2026-04-07T17:30:00-05:00
python3 scripts/create_module_assignments.py aiml2013 3 2026-04-14T19:00:00-05:00
```

- `course` — `aiml2003` or `aiml2013`
- `module_num` — 1 through 7
- `due_date` — ISO 8601 with UTC offset. AIML 2003 class time = `T17:30:00-05:00`. AIML 2013 class time = `T19:00:00-05:00`.

Deliverable type is resolved automatically from the course/module combination (see Week-by-Week Deliverable Types table). Rubric IDs are hard-coded per course. Assignment group IDs are looked up via the Canvas API at runtime. The Canvas module must already exist with a name containing "Module N" before running the script.

**Key rules:**
- Never edit files in `build/output/` — they are generated and will be overwritten
- Never put `<style>` blocks in source HTML files — use `course-styles.css`
- The build script is deterministic (no LLM, no external deps, stdlib Python only)
- CSS custom properties (`var(--name)`) are resolved at build time
- Descendant selectors (e.g., `.hero h2`) are resolved using DOM-aware ancestor tracking
- Always create content with the CANVAS API if possible

## Glossary

A single `glossary.json` at the project root holds all terms for both courses. Each term has a `courses` array (`["nlp"]`, `["cv"]`, or `["nlp", "cv"]`). The build script runs `build/build_glossary.py` before CSS inlining to generate `aiml2003/glossary.html` and `aiml2013/glossary.html` as source HTML files (with `<link>` to `course-styles.css`), which the normal inliner then processes.

**Key rules:**
- Never edit the generated `glossary.html` files directly — edit `glossary.json` and rebuild.
- If a term appears in both courses, its definition and link must be identical (enforced by the single-source design).
- Definitions are brief and non-technical. Each term links to an external longer explanation.
- Add new terms as modules are built. The `module_introduced` field tracks provenance.
- Course tags in the HTML reuse existing CSS classes: `tag-required` (Both), `tag-read` (NLP), `tag-video` (CV).

## IMSCC Packaging

When ready to upload to Canvas, build a Common Cartridge (.imscc) zip. Wiki pages use `type="webcontent"`. Existing quizzes are linked via `type="imswl_xmlv1p1"` (not re-imported). Discussion topics use `type="imsdt_xmlv1p1"`. The Canvas API CSRF token is in the `_csrf_token` cookie, not a meta tag.

Import path: **Course Settings → Import Course Content → Common Cartridge 1.x Package**. Canvas imports items as unpublished by default. Do not upload the .imscc as a file — it must be imported through the content import tool.

**Critical IMSCC rules (learned from errors):**
- `imsmanifest.xml` MUST be at the **root** of the zip, not in a subdirectory. Canvas returns "Unsupported content package" if the manifest is nested.
- Schema must be `<schema>IMS Common Cartridge</schema>` with `<schemaversion>1.1.0</schemaversion>`. Using "IMS Content Package" or version "1.1.4" causes import failures.
- When zipping, `cd` into the build directory first and zip from there: `cd build/ && zip -r output.imscc imsmanifest.xml web_resources/ discussions/`. Never zip a parent folder.
- Always verify after building: `unzip -l package.imscc | head -5` — the first file listed must be `imsmanifest.xml`, not `somefolder/imsmanifest.xml`.
- IMSCC `webcontent` resources import as **course files**, not wiki pages. Canvas does not automatically create wiki pages from HTML files in a Common Cartridge. The reliable approach: import the IMSCC to get files into the course, then use the Canvas API to fetch each file's content and create wiki pages via `POST /api/v1/courses/:id/pages`. Add each page to a module via `POST /api/v1/courses/:id/modules/:id/items` with `type: 'Page'`.

## Corrections Protocol

When the instructor reports an error, a failed import, or any technical correction:
1. Diagnose the root cause (don't just patch the symptom).
2. Fix the immediate issue in the affected files.
3. Add the lesson to this CLAUDE.md so the error never recurs — include what went wrong, why, and the correct approach.
4. Check whether the same error pattern exists in other files (e.g., if one IMSCC was wrong, check the other).
5. If the fix changes a standard or convention, update MODULE-STANDARDS.md and/or WRITING-STANDARDS.md too.

## Canvas Artifacts per Module

Each weekly module requires these Canvas artifacts beyond the wiki pages:

**Per module:**
- **Week X Participation** — Assignment, submission type "No Submission," **80 points**, Assignment Group: Participation. Graded manually from the gradebook.
- **Week X Ethics Discussion** — Discussion Topic, **20 points**, Assignment Group: Participation. Content from the ethics HTML page.
- **Week X Presentation** or **Week X Demo** — Assignment, submission type "On Paper," **100 points**, Assignment Group: Presentations or Demos. Attach the appropriate rubric (see Canvas Details table for rubric IDs).
- **Week X GitHub Repo** — Assignment, submission type "Online URL," **100 points**, Assignment Group: GitHub Repos. Attach the Repo rubric.

**Note on Week 1:** Week 1 has no lab submission or presentation. Still create the Participation assignment (attendance + ethics) for Week 1, but skip the Repo and Presentation/Demo assignments.

**Created once per course (not per module):**
- Missed Class Participation Makeup — single Canvas Discussion Topic, lives outside any module. One standing thread for the whole semester.

**Linked per module (already exists):**
- Info Sheet & Self-Evaluation quiz (AIML 2003: `/courses/26943/quizzes/168912`)
