# Module Standards

Standards for building any weekly module in AIML 2003 or AIML 2013.

---

## Module Structure

A module is a numbered sequence of HTML pages. Every module contains these page types in this order. File numbers are sequential — the actual number depends on how many pages of each type the module has.

| Order | Page Type | Required? | Notes |
|-------|-----------|-----------|-------|
| 1 | Overview | Yes | Module landing page with hero, at-a-glance cards, weekly rhythm |
| 2 | Readings & Prep | Yes | Required + optional resources, interactive experiments, discussion prep questions |
| 3 | Assignment Sheet | Yes | Deliverables overview table, abbreviated rubrics with Canvas links, due date banner |
| 4+ | Lab Sheet(s) | Yes (1 or more) | Detailed instructions with code scaffold. Some weeks may have multiple lab options. |
| Last | Ethics Discussion | Yes | Weekly prompt, requirements (150–250 words + reply), participation note |

**Numbering example — single lab:** `01-overview.html`, `02-readings.html`, `03-assignments.html`, `04-lab.html`, `05-ethics.html`

**Numbering example — three lab options:** `01-overview.html`, `02-readings.html`, `03-assignments.html`, `04-lab-option-a.html`, `05-lab-option-b.html`, `06-lab-option-c.html`, `07-ethics.html`

The numbers exist so files sort correctly in a folder and map to Canvas module item order. There are no fixed slot numbers — just sequential ordering.

---

## Syllabus Notice

Every overview page must include a prominent notice box (indigo background, `#e8eaf6`, border `#3949ab`) near the top stating:

> The Course Syllabus is the authoritative document for this course. All policies, grading criteria, due dates, and course requirements are governed by the Syllabus. If anything on this page conflicts with the Syllabus, the Syllabus takes precedence.

Include a direct link to the Syllabus:

- AIML 2003: `https://rose.instructure.com/courses/26943/external_tools/13895`
- AIML 2013: `https://rose.instructure.com/courses/26944/external_tools/13895`

---

## Dates and Deadlines

- All deliverables (lab, repo, presentation/demo, ethics post) are due **by Tuesday class** of the following week.
- The due-date line should say **"By Tuesday class"** and reference the Syllabus for exact dates. Never use "Monday 11:59 PM."
- Readings are due **before the following Tuesday class**, not before the class where they are assigned.
- Use the correct class time for each course in any examples: **5:30 PM** for AIML 2003, **7:00 PM** for AIML 2013.

---

## Presentations and Demos

All presentations and demos are **3–5 minutes**. Use "three- to five-minute" in body text and "3–5 minute" in tables/headings (en-dash `–`, not hyphen). The acceptable rubric window is **2:30–5:30**.

---

## Rubric Display

Assignment pages show **abbreviated rubric summaries** — criterion name, points, one-line description — with a link to the full rubric in Canvas.

Format: "100 points possible. Each criterion is scored on a 4-level scale. **View the full rubric with detailed scoring →**"

### Rubric Links by Course

| Rubric | AIML 2003 | AIML 2013 |
|--------|-----------|-----------|
| Presentation | `https://rose.instructure.com/courses/26943/rubrics/65800` | Update with AIML 2013 rubric ID |
| Demo | `https://rose.instructure.com/courses/26943/rubrics/65794` | Update with AIML 2013 rubric ID |
| Repository | `https://rose.instructure.com/courses/26943/rubrics/66034` | Update with AIML 2013 rubric ID |

### Presentation Rubric (100 pts)

| Criterion | Points |
|-----------|--------|
| Focus & Clarity | 25 |
| Key Takeaways | 25 |
| Visual Aid Effectiveness | 20 |
| Verbal Delivery | 20 |
| Time Management | 10 |

### Demo Rubric (100 pts)

| Criterion | Points |
|-----------|--------|
| Execution & Requirements | 20 |
| Variable & Data Flow | 20 |
| Dependency Justification | 15 |
| Prompt Strategy | 20 |
| Live Modification | 25 |

### Repository Rubric (100 pts)

| Criterion | Points |
|-----------|--------|
| Notebook Runs | 25 |
| Task Requirements (changes weekly) | 40 |
| Reflection | 20 |
| Repo Hygiene | 15 |

---

## Lab Sheet Standards

### Training Wheels Caveat

Every lab sheet with a code scaffold must include this warning box immediately after the "Code Scaffold" heading:

> **Training wheels alert:** This code scaffold is here to get you started. In later labs, you won't have one — you'll be writing your own code from scratch, using Gemini or another AI assistant to help you build it. So don't just copy-paste and run. Read each cell, understand what it does, and experiment with changing things. The more comfortable you get now, the easier it will be when the training wheels come off.

### Lab Sheet Sections

1. **Title and subtitle** — Lab name and one-line description
2. **The Task** — What students are building and why. Frame as "In the readings and in class, you learned..." — not "Last week you learned..."
3. **Input setup** — What data/image to use and where to get it
4. **Code Scaffold** — Training wheels caveat, then numbered cells with runnable code
5. **Markdown cell prompts** — Tip box after each code cell telling students what to write
6. **Bonus** — Optional creative exploration, worth **10 extra credit points**
7. **Presentation/Demo Prep** — Final section pointing to the assignment sheet. The notebook IS the presentation. No separate written reflection — the presentation serves as the reflection.

### CV-Specific Notes

- Images display inline via `matplotlib` — students don't save them as separate files. Include a tip box stating this.
- Include a resize cell after loading (longest side ~800px) with clear explanation.
- All code must be tested and verified to run in Google Colab.

---

## Readings Page Standards

### Required Sections

1. **Title and subtitle** with due date
2. **Time estimate box**
3. **Framing box** — "The big picture" (dark gradient background)
4. **NotebookLM reminder**
5. **Required readings/videos** — Resource cards with tags (Required/Optional, Video/Read/Interactive, time estimate)
6. **Interactive experiments** — Hands-on tools where applicable
7. **Preview section** — If the lab needs concepts beyond the main readings, bridge to them here
8. **Optional deeper dive**
9. **Discussion prep questions** — 3 questions for Tuesday class
10. **Bridge box** — For dual-enrolled students, connecting the parallel course topic

### Resource Card Format

Each card includes: title, required/optional tag, format tag (Video/Read/Interactive), time estimate, source, description, link. Optionally a "Key takeaway" focus box.

---

## Ethics Discussion Standards

- Title format: "Ethics Thread: [Question/Theme]"
- Context paragraph connecting the week's technical content to an ethical question
- 3–4 prompts; students address at least one
- Requirements: 150–250 words, take a position, reply to a classmate
- Deadline: Initial post by Tuesday (before class), reply by the following Tuesday
- Include this note: "The weekly ethics discussion is worth 20% of your weekly Participation grade (the other 80% comes from attendance and in-class engagement). Whether you attend in person or via Zoom, this post is required every week."
- Where possible, NLP and CV ethics prompts should be **thematically aligned** so dual-enrolled students see the same question through both lenses.

---

## Participation Model (80/20)

Each week's participation grade:

- **80%** — Attendance & engagement (or the makeup post if absent)
- **20%** — Weekly ethics discussion post (always required)

The makeup participation post is a **standalone course resource**, not part of any weekly module.

---

## CSS Design System

All pages share the same variables and component styles.

| Variable | Value | Usage |
|----------|-------|-------|
| `--primary` | `#1a3a5c` | Headings, hero gradient |
| `--accent` | `#2e7d32` | Tip boxes |
| `--light-bg` | `#f7f9fc` | Card backgrounds |
| `--border` | `#d0d7de` | Borders |
| `--text` | `#1f2328` | Body text |
| `--muted` | `#656d76` | Subtitles |
| `--warn-bg` / `--warn-border` | `#fff3e0` / `#e65100` | Warning boxes |

Components: hero (dark gradient), syllabus notice (indigo), info cards (2-col grid), tip boxes (green left border), warning boxes (orange left border), section cards (white, 1px border), rubric tables (primary header), bridge boxes (purple `#ede7f6` / `#5e35b1`), tags (small rounded pills — blue/Tuesday, purple/Thursday, red/due).

Font stack: `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif`. Body 0.95rem, line-height 1.6. Max width 820–860px, centered.

---

## Separability (Cross-Course Content)

These courses are built and taught concurrently this semester. They may not always be. All cross-course content must be cleanly removable so a future instructor can teach either course standalone.

### What must be separable

- **Bridge boxes** (purple, `.bridge-box`): Self-contained HTML blocks. Delete the entire `<div class="bridge-box">...</div>` and the page still makes sense.
- **Combined assignment references**: Must live in their own section, paragraph, or callout — never woven into the individual assignment description. Use a distinct heading or box (e.g., "Taking AIML 2003 too?") that can be removed as a unit.
- **Shared lab references**: The Thursday lab is currently combined. References should say "shared lab session" or "combined lab," not "the AIML 2003/2013 lab." If the courses are taught separately, this phrasing still works.
- **Ethics alignment notes**: The suggestion to align ethics prompts across courses is a preference, not a dependency. Each course's ethics prompt must stand alone.

### How to test separability

Delete every bridge box, combined assignment reference, and cross-course mention from a module's HTML files. The remaining content must be complete, coherent, and require no edits to make sense.

---

## GenAI Policy

Include in every welcome/overview page. Two hard rules:

1. Never share university login credentials with any external GenAI agent.
2. Do not upload sensitive data, PII, or school login credentials into any AI tool.

Students are expected to use GenAI. They are accountable for their work; they get credit for work done with AI and are counted off for AI errors.
