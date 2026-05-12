# templates/ — Weekly Module Templates

Reusable HTML page structure for every weekly module in Canvas. Templates are course-agnostic — use them for both AIML 2003 and AIML 2013. Every placeholder uses `{{PLACEHOLDER_NAME}}` syntax for easy find-and-replace.

## Template Files

| File | Purpose | Use When |
|------|---------|----------|
| `week-overview.html` | Module landing page | Every module |
| `week-readings.html` | Readings & prep page | Every module |
| `week-assignments-presentation.html` | Assignment sheet with presentation deliverable | When the week's deliverable is a presentation |
| `week-assignments-demo.html` | Assignment sheet with live-demo deliverable | When the week's deliverable is a demo |
| `week-ethics.html` | Weekly ethics discussion prompt | Most modules — see exceptions below |

See `aiml2003/README.md` and `aiml2013/README.md` for the deliverable type per module (Presentation vs. Demo) in each course. The two courses don't always match — Module 5 NLP is a Presentation while Module 5 CV is a Demo, and Module 6 is the reverse.

## Weekly Module Checklist

Each weekly Canvas module should contain (in order):

1. **Week Overview** — `week-overview.html`
2. **Readings & Prep** — `week-readings.html`
3. **Assignment Sheet** — `week-assignments-presentation.html` OR `week-assignments-demo.html`
4. **Lab Option Pages** (if applicable) — custom per week
5. **Ethics Discussion** — `week-ethics.html` (skip for Module 6)

## Module 6 has no ethics discussion

Both courses dropped the Module 6 ethics discussion. The module's Participation grade comes from attendance/engagement only that week — no separate ethics post. Don't apply `week-ethics.html` for Module 6 in either course.

## Placeholder Reference

### Used in ALL templates

| Placeholder | Example | Notes |
|-------------|---------|-------|
| `{{WEEK_NUM}}` | `3` | Week number (1–8) |
| `{{TOPIC_TITLE}}` | `Text as Data` | Short topic name from syllabus |
| `{{DUE_DATE}}` | `April 7` | Tuesday due date from syllabus |
| `{{TUESDAY_DATE}}` | `April 1` | Tuesday class date for THIS week |
| `{{THURSDAY_DATE}}` | `April 3` | Thursday lab date for THIS week |

### Week Overview (`week-overview.html`)

| Placeholder | Example |
|-------------|---------|
| `{{TOPIC_SUBTITLE}}` | `Spring 2026 · Week 3 · AIML 2003` |
| `{{TOPIC_HOOK}}` | `This week you'll turn raw text into numbers...` |
| `{{FOCUS_SUMMARY}}` | `Tokenization, word embeddings, sentiment analysis` |
| `{{DELIVERABLE_TYPE}}` | `Presentation` or `Demo` |
| `{{TUESDAY_TOPICS}}` | `tokenization, embeddings, and why text needs to be numerical` |

### Readings (`week-readings.html`)

| Placeholder | Example |
|-------------|---------|
| `{{PREP_TIME}}` | `90 minutes` |
| `{{BIG_PICTURE}}` | `Before an LLM can process text, that text must become numbers...` |
| `{{RESOURCE_TITLE}}` | `3Blue1Brown: But what is a neural network?` |
| `{{RESOURCE_SOURCE}}` | `YouTube / 3Blue1Brown` |
| `{{RESOURCE_TIME}}` | `19 min` |
| `{{RESOURCE_URL}}` | `https://youtube.com/watch?v=...` |
| `{{RESOURCE_DESCRIPTION}}` | `Visual walkthrough of how neural networks learn...` |
| `{{KEY_TAKEAWAY}}` | `Embeddings capture meaning, not just spelling` |
| `{{DISCUSSION_Q1–Q3}}` | Discussion questions for Tuesday class |

Copy the resource-card block for each reading/video. Use the `.optional` class for non-required resources.

### Assignments — Presentation variant (`week-assignments-presentation.html`)

| Placeholder | Example |
|-------------|---------|
| `{{NUM_DELIVERABLES}}` | `three` |
| `{{LAB_TITLE}}` | `Zero-Shot vs. Few-Shot Classification` |
| `{{LAB_OVERVIEW}}` | `In this lab you'll compare how Gemini performs...` |
| `{{LAB_INSTRUCTIONS}}` | Detailed build instructions |
| `{{PRESENTATION_DATE}}` | `April 1` |
| `{{PRES_POINT_1–3}}` | What students should cover in their presentation |

### Assignments — Demo variant (`week-assignments-demo.html`)

| Placeholder | Example |
|-------------|---------|
| `{{NUM_DELIVERABLES}}` | `three` |
| `{{LAB_TITLE}}` | `Chat with a PDF` |
| `{{LAB_OVERVIEW}}` | `Build a RAG pipeline that lets you ask questions...` |
| `{{LAB_INSTRUCTIONS}}` | Detailed build instructions |
| `{{DEMO_DATE}}` | `April 21` |
| `{{DEMO_POINT_1–3}}` | What students should show in their live demo |

### Ethics Discussion (`week-ethics.html`)

| Placeholder | Example |
|-------------|---------|
| `{{ETHICS_TITLE}}` | `Where Does the Data Come From?` |
| `{{ETHICS_CONTEXT}}` | `The Karpathy video mentions that LLMs are trained on...` |
| `{{ETHICS_Q1–Q3}}` | Discussion questions (add/remove as needed) |

## Standing Assignments (not templated per week)

These live as standalone pages, not inside weekly modules:

- **Missed Class Participation Makeup** — `<course>/makeup-participation.html`
- **Welcome / Course landing page** — `<course>/welcome.html`

## Participation Model (80/20)

Every module (except Module 6 — see above):

- **80%** — Attendance & engagement (or makeup post within 48 hours)
- **20%** — Ethics discussion post

Module 6's Participation grade is 100% attendance/engagement (no ethics post).
