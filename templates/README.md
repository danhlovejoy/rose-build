# AIML 2003 — Weekly Module Templates

These templates define the repeating page structure for each weekly module in Canvas. Every placeholder uses `{{PLACEHOLDER_NAME}}` syntax for easy find-and-replace.

## Template Files

| File | Purpose | Use When |
|------|---------|----------|
| `week-overview.html` | Module landing page | Every week |
| `week-readings.html` | Readings & prep page | Every week |
| `week-assignments-presentation.html` | Assignment sheet with presentation deliverable | Weeks 2, 4, 6 |
| `week-assignments-demo.html` | Assignment sheet with live demo deliverable | Weeks 3, 5, 7 |
| `week-ethics.html` | Weekly ethics discussion prompt | Every week |

## Weekly Module Checklist

Each week's Canvas module should contain (in order):

1. **Week Overview** — `week-overview.html`
2. **Readings & Prep** — `week-readings.html`
3. **Assignment Sheet** — `week-assignments-presentation.html` OR `week-assignments-demo.html`
4. **Lab Option Pages** (if applicable) — custom per week
5. **Ethics Discussion** — `week-ethics.html`

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

## Syllabus Schedule Reference

| Week | Topic | Due Date | Deliverable Type |
|------|-------|----------|-----------------|
| 1 | The LLM Landscape | March 24 | Info Sheet (setup week) |
| 2 | The Art of the Prompt | March 31 | Presentation |
| 3 | Text as Data | April 7 | Presentation |
| 4 | The Vector Space | April 14 | Demo |
| 5 | Basic RAG | April 21 | Demo |
| 6 | Evaluating LLMs | April 28 | Presentation |
| 7 | Simple Agents | May 5 | Demo |
| 8 | Portfolio & Future | May 12 | Final Portfolio Presentation |

## Standing Assignments (not templated per week)

These live as standalone pages, not inside weekly modules:

- **Missed Class Participation Makeup** — `makeup-participation.html`
- **Welcome / Module 1 Overview** — `00-welcome.html`

## Participation Model (80/20)

Every week:
- **80%** — Attendance & engagement (or makeup post within 48 hours)
- **20%** — Ethics discussion post (always required)
