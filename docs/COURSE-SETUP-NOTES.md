# Course Setup Notes — {{COURSE_NAME}}

Welcome. This page is included in the {{COURSE_CODE}} Canvas import cartridge ({{CARTRIDGE_FILENAME}}). It explains what's in the cartridge, what you still need to set up by hand, and where to find the source files if you want to edit anything.

## What this cartridge contains

If you imported via `scripts/import_cartridge_to_canvas.py --bundle`, the script also created per-module assignment shells and cloned the three deliverable rubrics into this course via API. Without `--bundle`, you'll have pages + modules + discussions + quizzes only, and the assignment shells described below will be missing.

- Every wiki page for Modules 1 through 7 — overview, readings, assignment sheets, lab pages, the welcome landing page, the standing makeup-participation page, and the glossary.
- The Canvas module structure: Modules 1–7 with their pages in the order students should see them.
- Ethics discussion topics for Modules 1 through 5 (Module 6 has no ethics post; Module 7 doesn't either).
- Reading quizzes for Modules 1 through 6 and a final exam. **The live course did not use these.** They ship as optional assessments in case you want to add a formal comprehension check; if not, leave them unpublished or delete them. The quizzes import from separate `.imscc` files in the source repo's `quizzes/` and `final-exam/` directories — Canvas's CC importer fails when one cartridge holds more than one standalone QTI quiz, so the import script imports them one at a time and then arranges them into the right modules via the Canvas API.
- This setup-notes page.

Internal links between pages use Canvas's `$WIKI_REFERENCE$` syntax, so they resolve to whatever course ID Canvas assigns after import. You don't need to find-and-replace course IDs.

## What you still need to set up after import

The cartridge intentionally does not include the items below, because Canvas's Common Cartridge format doesn't carry them cleanly. Each one needs a separate manual or scripted step.

### Per-week assignments and rubrics — created automatically by `--bundle`

If you ran the import via `scripts/import_cartridge_to_canvas.py --bundle ...`, all four per-module Canvas artifacts have already been created and the three deliverable rubrics have been cloned into your course:

- Participation (80 pts; 100 for Module 6)
- Ethics Discussion (20 pts, graded discussion; skipped for Module 6)
- Presentation, Demo, or Final Portfolio (100 pts, with rubric attached)
- GitHub Repo (100 pts, with Repo rubric attached)

Due dates are set to the source semester (Module 1 = March 31, 2026, walking forward by week). To put them on your semester schedule, either use Canvas's bulk edit due dates feature (Assignments → ⋮ → Edit Assignment Dates) or re-run the bundle with `--start-date YYYY-MM-DD` against a fresh course.

If you want to re-create assignments for a single module (e.g., after wiping it), use:

```
python3 scripts/create_module_assignments.py {{COURSE_CODE_LOWER}} <module_num> <due_date>
```

That script targets the live source course (Canvas course 26943 / 26944). It expects the Presentation, Demo, and Repo rubrics to already exist in the target course by their original IDs, so it only works against the source course or one that already has rubrics installed.

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

### Rubrics — cloned automatically by `--bundle`

If you used `--bundle`, the three rubrics (Presentation, Demo, GitHub Repo) have been cloned into your course from the source course. No manual setup required. The new rubric IDs are different from the originals; this only matters if you intend to run `create_module_assignments.py` against your new course (that script uses hardcoded source IDs and would need editing).

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
