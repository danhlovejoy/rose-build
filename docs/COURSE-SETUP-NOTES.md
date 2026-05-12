# Course Setup Notes — {{COURSE_NAME}}

Welcome. This page is included in the {{COURSE_CODE}} Canvas import cartridge ({{CARTRIDGE_FILENAME}}). It explains what's in the cartridge, what you still need to set up by hand, and where to find the source files if you want to edit anything.

## What this cartridge contains

- Every wiki page for Modules 1 through 7 — overview, readings, assignment sheets, lab pages, the welcome landing page, the standing makeup-participation page, and the glossary.
- The Canvas module structure: Modules 1–7 with their pages in the order students should see them.
- Ethics discussion topics for every module that has one (Modules 1–5 and Module 7; Module 6 has no ethics post).
- Reading quizzes for Modules 1 through 6 and a final exam. **The live course did not use these.** They ship as optional assessments in case you want to add a formal comprehension check; if not, leave them unpublished or delete them. The quizzes import from separate `.imscc` files in the source repo's `quizzes/` and `final-exam/` directories — Canvas's CC importer fails when one cartridge holds more than one standalone QTI quiz, so the import script imports them one at a time and then arranges them into the right modules via the Canvas API.
- This setup-notes page.

Internal links between pages use Canvas's `$WIKI_REFERENCE$` syntax, so they resolve to whatever course ID Canvas assigns after import. You don't need to find-and-replace course IDs.

## What you still need to set up after import

The cartridge intentionally does not include the items below, because Canvas's Common Cartridge format doesn't carry them cleanly. Each one needs a separate manual or scripted step.

### Per-week assignments and rubrics

Canvas assignments with attached rubrics don't round-trip through Common Cartridge. The repository ships a script that creates them via the Canvas API. From a working copy of the source repo:

```
python3 scripts/create_module_assignments.py {{COURSE_CODE_LOWER}} <module_num> <due_date>
```

Example:
```
python3 scripts/create_module_assignments.py {{COURSE_CODE_LOWER}} 2 2026-04-07T17:30:00-05:00
```

The script creates the four Canvas artifacts per module (Participation assignment, Ethics Discussion, Presentation/Demo assignment, GitHub Repo assignment), wires them into the module, and attaches the right rubrics. Module 6 only needs three artifacts — see CLAUDE.md in the repo for the full rules.

### Grade-weight settings

Canvas grade weighting by Assignment Group is course-level configuration that doesn't ship in the cartridge. Set it up under Assignments → Assignment Groups → "Weight final grade based on assignment groups":

| Group | Weight |
|--|--|
| Participation | 20% |
| GitHub Repos | 25% |
| Presentations | 15% |
| Demos | 25% |
| Final Reflection | 5% |
| Final Portfolio | 10% |

### Rubrics

Three course-specific rubrics need to exist before `create_module_assignments.py` can attach them: a Presentation rubric, a Demo rubric, and a GitHub Repo rubric. The existing rubric IDs for the current Rose State courses are in CLAUDE.md. For a new Canvas course, recreate these three rubrics under Course → Rubrics, then update the rubric IDs in `scripts/create_module_assignments.py` (the IDs are at the top of the file).

### Advancing the welcome page each week

The cartridge ships `welcome.html` pointing at Module 1 as "This Week" with an empty Past Modules list. The Canvas course landing page uses this file. Each week as you advance through the semester, update it:

1. Copy the current "This Week" link into the Past Modules list (newest at top).
2. Update "This Week" to point at the new module's overview page.
3. Edit the page in Canvas directly, or rebuild from source and re-upload via `scripts/upload_to_canvas.py`.

The course README has the same instructions under "Advancing to a New Week."

## Class schedule and participation model

This course meets Tuesdays during the second 8-week session. The companion lab session is on Thursdays via Zoom and is shared with the other course in the AIML pair when both are offered concurrently.

The Participation grade follows an 80/20 split:

- **80%** — attendance and engagement (or a Missed Class Participation Makeup post within 48 hours)
- **20%** — the weekly Ethics Discussion post

**Module 6 exception**: both courses dropped the Module 6 ethics post. For Module 6, the Participation assignment is worth 100 points (attendance/engagement only) and there is no Ethics Discussion item.

## Source repository

The full source for this course lives at <https://github.com/danhlovejoy/rose-build>. The repo is what you edit; this cartridge is what Canvas imports.

To rebuild the cartridge from source after editing:

```
bash build/build.sh --standalone {{COURSE_CODE_LOWER}}
python3 build/package_course_cartridge.py {{COURSE_CODE_LOWER}}
```

The new cartridge will land in `dist/{{CARTRIDGE_FILENAME}}`. To push the full bundle (master cartridge + reading quizzes + final exam) into a fresh Canvas course in one step:

```
python3 scripts/import_cartridge_to_canvas.py --bundle {{COURSE_CODE_LOWER}} <course_id>
```

Editing conventions worth reading before you make changes:

- `docs/MODULE-STANDARDS.md` — module structure, file numbering, page types, rubric format
- `docs/WRITING-STANDARDS.md` — banned phrases, formatting constraints, tone rules
- `docs/DEMO-STANDARDS.md` — conventions for interactive slide demos
- `CLAUDE.md` — full project context for AI assistants, plus Canvas details and correction protocol

## Questions

The source author is Dan Lovejoy (danlovejoy@gmail.com).
