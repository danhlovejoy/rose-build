# Canvas Module Push Checklist

Two separate workflows: **Module Upload** (can happen any time) and **Welcome Page Update** (Monday night or Tuesday before class only).

---

## Module Upload

### 1. Build

- [ ] Run `bash build/build.sh [course/moduleN]`
- [ ] Confirm: no dead links, no encoding errors in output
- [ ] Confirm `build.conf` delivery mode is correct (concurrent vs. standalone)

### 2. Canvas Assignments

Create these four items in Canvas for the week. All are unpublished until Step 5.

- [ ] **Week X Participation** — Assignment / No Submission / 80 pts / Participation group
- [ ] **Week X Ethics Discussion** — Discussion Topic / 20 pts / Participation group
  - Paste the ethics prompt from the module's ethics HTML page into the Canvas discussion body
- [ ] **Week X [Presentation or Demo]** — Assignment / On Paper / 100 pts / correct group
  - Attach the correct rubric (rubric IDs differ by course — see CLAUDE.md)
- [ ] **Week X GitHub Repo** — Assignment / Online URL / 100 pts / GitHub Repos group
  - Attach the Repo rubric
- [ ] Set due dates on all four assignments

### 3. Canvas Pages

- [ ] Upload each built HTML file from `build/output/[course]/[moduleN]/` to Canvas as a wiki page
- [ ] Spot-check the overview and assignments pages in Canvas: no garbled characters, layout intact, links resolve

### 4. Canvas Module Structure

- [ ] Create the Module in Canvas (if not already created)
- [ ] Add pages to the module in order (matching file numbering)
- [ ] Add all four assignments to the module
- [ ] Verify item order

### 5. Publish

- [ ] Publish all pages
- [ ] Publish all assignments and the ethics discussion
- [ ] Publish the module itself

---

## Welcome Page Update

**Do this Monday night or Tuesday before class — not during module upload.**

- [ ] Open `[course]/welcome.html`
- [ ] Copy the current "This Week" link into the Previous Modules list (newest at top)
- [ ] Update "This Week" to the new module's Canvas overview page URL
- [ ] Run `bash build/build.sh [course]` (builds only the welcome and course-level pages)
- [ ] Upload the built welcome page to Canvas and publish

---

## Canvas Details Reference

| | AIML 2003 (NLP) | AIML 2013 (CV) |
|--|--|--|
| Course ID | 26943 | 26944 |
| Presentation Rubric | `/courses/26943/rubrics/65800` | `/courses/26944/rubrics/66062` |
| Demo Rubric | `/courses/26943/rubrics/65794` | `/courses/26944/rubrics/66063` |
| Repo Rubric | `/courses/26943/rubrics/66034` | `/courses/26944/rubrics/66064` |
