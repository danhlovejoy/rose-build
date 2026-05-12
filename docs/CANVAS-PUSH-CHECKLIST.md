# Canvas Module Push Checklist

Two separate workflows: **Module Upload** (can happen any time) and **Welcome Page Update** (Monday night or Tuesday before class only).

---

## Module Upload

### 1. Build

- [ ] Confirm `build.conf` delivery mode is correct (concurrent vs. standalone)
- [ ] Run `bash build/build.sh [course/moduleN]`
- [ ] Spot-check the output for encoding errors and garbled characters
- [ ] Run `python3 build/check_links.py [course/moduleN]` to catch dead relative links

### 2. Canvas Assignments

Create the items below in Canvas for the week. Module 6 skips the Ethics Discussion in both courses, and its Participation assignment is worth 100 points instead of 80. All items are unpublished until Step 5.

- [ ] **Week X Participation** — Assignment / No Submission / 80 pts (100 pts for Module 6) / Participation group
- [ ] **Week X Ethics Discussion** — Discussion Topic / 20 pts / Participation group. Skip for Module 6.
  - Paste the ethics prompt from the module's ethics HTML page into the Canvas discussion body
- [ ] **Week X [Presentation or Demo]** — Assignment / On Paper / 100 pts / correct group
  - Attach the correct rubric (rubric IDs differ by course — see CLAUDE.md)
- [ ] **Week X GitHub Repo** — Assignment / Online URL / 100 pts / GitHub Repos group
  - Attach the Repo rubric
- [ ] Set due dates on every assignment created above

### 3. Canvas Pages

- [ ] Upload each built HTML file from `build/[course]/[moduleN]/` to Canvas as a wiki page (or run `python3 scripts/upload_to_canvas.py [course]`)
- [ ] Spot-check the overview and assignments pages in Canvas: no garbled characters, layout intact, links resolve

### 4. Canvas Module Structure

- [ ] Create the Module in Canvas (if not already created)
- [ ] Add pages to the module in order (matching file numbering)
- [ ] Add the week's assignments to the module (four for most weeks; three for Module 6)
- [ ] Verify item order

### 5. Publish

- [ ] Publish every page
- [ ] Publish every assignment
- [ ] Publish the ethics discussion (skip for Module 6)
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
