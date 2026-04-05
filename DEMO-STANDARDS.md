# DEMO-STANDARDS.md

Standards for building interactive HTML demos in `slides/`. These demos are standalone files used during live class sessions. They are also added to readings. They do not go through the build pipeline or use `course-styles.css`. These demos form a bridge from the students' current understanding to understanding the new concept being presented. Consider WHERE the student is in the course, and what they have already learned to build upon their understanding. 

## Process and Pedagogy 
When the instructor gives you a demo task, be sure to think through it with them. When planning the lesson, go through the thinking process with your imaginary student. Think of what you know the student knows, what they have recently covered, and the learning desired and the intermediate understandings required to get there. Think of questions the student might ask. Prompt the instructor with these questions when planning the demo. Each stage should build on the previous one; a student who understood Stage N should have the vocabulary and intuition needed for Stage N+1.  

## Writing

All prose in demos — stage descriptions, tip boxes, warn boxes, card text, explanations — must follow **WRITING-STANDARDS.md**. The same banned frames, banned tells, and formatting constraints apply here as in course pages. Demos are not exempt because they're standalone files.

Watch especially for:
- Dramatic inversion rhetoric: "X is not the problem. Y is." This is an AI tell.
- Banned words from the lexical governance list (delve, robust, comprehensive, etc.).
- Over-explaining concepts the student already knows from a previous stage.
- Restating the same idea in different words within the same tip box.

## File Conventions

**Naming:** `{topic}-demo.html`, kebab-case. Examples: `cosine-similarity-demo.html`, `pixel-histogram-demo.html`.

**Title format:** `Topic: Subtitle — Course`. Use a hyphen after the topic and an em-dash before the course. A demo can be for both courses.

```html
<title>Cosine Similarity: From Geometry to Meaning — AIML 2003 / 2013</title>
```

**Single-file architecture:** Each demo is one self-contained HTML file. All CSS in a single `<style>` block in `<head>`. All JS in a single `<script>` block at the end of `<body>`. No external stylesheets, no JS modules, no build step.

**External dependencies:** Plotly only, loaded from CDN. Pin the version.

```html
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
```

If the demo uses only Canvas (no charts), omit Plotly entirely.

## Page Structure

Every demo follows this skeleton:

```html
<body>
  <div class="hero">
    <h1>Demo Title</h1>
    <p>Subtitle or course name</p>
    <p class="hl">One-sentence hook describing what the student will see.</p>
  </div>

  <div class="container">
    <div class="stage">
      <div class="stage-line"><span class="stage-num">1</span><h2>Stage Title</h2></div>
      <p>Explanatory prose.</p>
      <!-- Interactive elements -->
      <!-- Tip/warn boxes -->
    </div>

    <div class="arrow-box">&darr;</div>

    <div class="stage">...</div>
  </div>

  <div class="footer">
    AIML 2003 &bull; Module 3: Learned Embeddings &bull; Spring 2026
  </div>

  <script>/* all JS here */</script>
</body>
```

**Stage count:** Aim for 3–6 stages. Every stage should have its own interactive element (chart, canvas, sliders, buttons). If a stage has no interactivity, it is probably a tip box or a paragraph, not a stage.

**Footer format:** `Course &bull; Module: Topic &bull; Semester`. For cross-course demos: `AIML 2003 / 2013 &bull; Module: Topic &bull; Semester`.

## CSS Design System

### Required Variables

Every demo must define this full set in `:root`. Do not omit variables or hardcode their values elsewhere.

```css
:root {
  --primary: #1a3a5c;
  --primary-light: #2e5a88;
  --accent: #2e7d32;
  --light-bg: #f7f9fc;
  --border: #d0d7de;
  --text: #1f2328;
  --muted: #656d76;
  --neg: #c62828;
  --neg-bg: #fce4ec;
  --pos: #2e7d32;
  --pos-bg: #e8f5e9;
  --purple: #5e35b1;
  --purple-bg: #ede7f6;
  --orange: #e65100;
}
```

Demo-specific variables (e.g., channel colors for an image demo) go after the standard set with a comment.

### Standard Components

Use these class names consistently. Do not invent synonyms.

| Class | Purpose |
|---|---|
| `.hero` | Full-width gradient header |
| `.container` | Centered content column, `max-width: 1100px` |
| `.stage` | One conceptual section |
| `.stage-num` | Numbered circle in stage header |
| `.stage-line` | Stage header bar with bottom border |
| `.card` | Bordered info card on light background |
| `.tip` | Green insight/takeaway box (left border accent) |
| `.warn-tip` | Orange warning box (left border orange) |
| `.btn` / `.btn-primary` / `.btn-accent` / `.btn-outline` / `.btn-purple` | Buttons |
| `.btn-group` | Flex row of buttons |
| `.stats-row` / `.stat-card` | Row of metric cards with `.val` and `.lbl` |
| `.eq-box` | Centered monospace equation display |
| `.arrow-box` | Down-arrow separator between stages |
| `.footer` | Page footer |

**Do not use:** `.info-box` (use `.card`), `.insight` (use `.tip` or `.card`), `.mode-btn` (use `.btn`), `.upload-zone` (use `.card` with custom inner content).

### Layout

Two-column layout when a sidebar is needed:

```css
.row { display: flex; gap: 1.5rem; flex-wrap: wrap; }
.col-main { flex: 1; min-width: 400px; }
.col-side { width: 320px; }
```

For responsive behavior, the `flex-wrap: wrap` causes the sidebar to stack below on narrow screens. Do not use CSS Grid for primary layout — reserve it for specialized components (slider grids, etc.).

### Scoped Selectors

Scope `h2` styling to `.stage-line h2`, not a bare `h2` selector. Bare element selectors break if the demo adds headings outside stages.

## JavaScript Patterns

### Initialization

Wrap initialization in `DOMContentLoaded`:

```js
document.addEventListener('DOMContentLoaded', init);

function init() {
  renderStage1();
  renderStage2();
  // ...
}
```

### State

All state lives in module-level variables. No classes, no frameworks.

```js
let currentWord = null;
const DATA = [];
```

### Plotly

- Always use `Plotly.react()`, never `Plotly.newPlot()`. `react` is idempotent and avoids event listener leaks.
- Always pass `{ responsive: true }` as the third argument.
- Standard layout properties:

```js
{
  plot_bgcolor: '#fff',
  paper_bgcolor: '#fff',
  margin: { l: 60, r: 20, t: 10, b: 50 },
  font: { family: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif', size: 12 },
  xaxis: { gridcolor: '#e8ecf0' },
  yaxis: { gridcolor: '#e8ecf0' },
}
```

- Use `title` in the layout for chart titles, not Plotly's legend as a substitute.
- Set `showlegend: false` on traces when the legend duplicates a title or axis label.
- Remove `plotly_click` listeners with `removeAllListeners` before rebinding to avoid stacking.

### Canvas

- Use `image-rendering: pixelated` on display canvases when upscaling pixel data.
- Grayscale formula: `0.299*R + 0.587*G + 0.114*B` (ITU-R BT.601).
- Use offscreen canvases for processing, visible canvases for display.

### Event Handlers

- **Static HTML elements:** Use inline `onclick` / `oninput` attributes. Simple, visible, no wiring needed.
- **JS-generated elements:** Use `.addEventListener()`. Inline handlers on dynamically created elements can break in some contexts.

### Animation

Use `setInterval` with a stored interval ID. Always `clearInterval` before starting a new one.

```js
let trainInterval = null;

function startTraining() {
  if (trainInterval) clearInterval(trainInterval);
  trainInterval = setInterval(trainStep, 100);
}
```

## Pedagogical Rules

### Start suboptimal

Initialize interactive elements to a random or clearly wrong state. The student should see the problem before seeing the solution. Do not pre-solve the demo.

### Every transformation must be visible

If a stage demonstrates a conversion (color to grayscale, text to vector, raw pixels to histogram), the before and after must look different. Do not use grayscale inputs when demonstrating grayscale conversion. Do not use all zero vectors when demonstrating sparsity.

### Visualizations must not contradict the concept

If the demo teaches that "same direction = similar," every chart in the demo must visually reinforce that. A butterfly chart that mirrors one vector's bars to the left while the other points right makes two similar documents look opposite — directly contradicting the lesson the student just learned. The chart format itself becomes misinformation.

Before choosing a chart type, ask: if a student who understood the previous stage glances at this chart without reading any labels, will their instinct match the data? If a high-similarity pair looks like it's pointing in opposite directions, the chart is lying. Use grouped bars (side by side, same direction) instead of mirrored/tornado charts when comparing vectors that the demo frames as "similar" or "same direction."

This applies broadly. Any visual encoding — color, direction, length, position — that a student could reasonably interpret as meaning the opposite of what the data shows is a bug, not a style choice.

### Match the displayed metric to the optimization target

If the UI shows accuracy, the "best fit" must maximize accuracy. If the UI shows loss, optimize loss. Students will find counterexamples if these diverge.

### Bounded UI, bounded algorithm

Sliders and other controls have finite ranges. If the underlying algorithm can produce values outside that range (e.g., unbounded gradient descent), either regularize, clamp, or widen the range. An algorithm that pins a slider at its limit every time is broken.

### Use real data when possible

Prefer real model outputs over simulated or pseudo-random data. If the demo references a specific model (e.g., `all-MiniLM-L6-v2`), use actual outputs from that model. Generate them offline and embed as static constants.

### Keep stages interactive

Every stage should have something the student can click, drag, or hover. If a stage is purely expository, it should be a tip box inside an adjacent stage or a short paragraph, not its own numbered stage. The exception is a final "bridge to readings" stage that points students to the assigned materials.

## Assertions

Demos contain hardcoded values that make implicit mathematical or behavioral claims: a "Perpendicular" button implies a 90-degree angle, a "Best Fit" button implies maximum accuracy, a toy vector labeled "Queen" implies specific attribute values. When these claims are wrong, students notice.

The rule: **any hardcoded value that makes a verifiable claim gets an assertion comment.** The comment documents the claim, shows the math, and states the expected result. This serves two purposes: it forces the author to verify the math at write time, and it gives a future reader (or a lint script) something to check.

### Format

Use HTML comments with the prefix `assert:` followed by a plain-language check. Place the comment immediately above the code it covers.

```html
<!-- assert: dot(3,4, -4,3) = 0 (perpendicular) -->
<!-- assert: dot(3,4, 4,3) = 24 (similar, not identical) -->
<!-- assert: dot(3,4, -3,-4) = -25 (opposite) -->
<button onclick="presetVectors(3,4,4,3)">Nearly aligned</button>
<button onclick="presetVectors(3,4,-4,3)">Perpendicular</button>
<button onclick="presetVectors(3,4,-3,-4)">Opposite</button>
```

For JS data, use `// assert:` comments:

```js
// assert: cosine(king, queen) > 0.6 (most similar pair)
// assert: cosine(king, water) < 0.35 (unrelated)
const REAL_EMBEDDINGS = { ... };
```

### What to assert

- **Preset buttons** that claim a mathematical property (perpendicular, opposite, identical, zero, maximum).
- **Hardcoded vectors** where the relationships between entries matter (e.g., king is closer to queen than to water).
- **Toy data** where specific values produce a known outcome (e.g., training data that is linearly separable, a word vector that is sparse).
- **Threshold values** where crossing a boundary changes behavior (e.g., a similarity cutoff, a learning rate that avoids divergence).

### What not to assert

- Layout constants (chart heights, margins, font sizes).
- Aesthetic choices (colors, labels, prose).
- Values that are only approximate by nature ("roughly 0.68" does not need `assert: exactly 0.6807`).

### The standard that prevents the bug

The perpendicular preset bug happened because `presetVectors(3, 4, -4, 1)` was never checked: (3)(−4) + (4)(1) = −8, not 0. With the assertion convention, the author writes `assert: dot(3,4, -4,1) = 0`, does the mental math, gets −8, and catches the typo before committing.

### Lint script

`build/lint_demos.py` automatically verifies all `assert:` comments and checks for anti-patterns. Run it before committing any demo changes:

```
python3 build/lint_demos.py                        # all demos
python3 build/lint_demos.py slides/foo-demo.html   # one file
```

The script checks:

- **Assertions:** Parses `assert:` comments and verifies the math. Supports `dot(a,b, c,d) = N`, `cosine(name1, name2) > N`, `cosine(name1, name2) < N`. Cosine assertions look up named vectors from JS objects in the same file (e.g., `REAL_EMBEDDINGS`).
- **Anti-patterns:** `Plotly.newPlot` usage, SVG via innerHTML, CSS variables in JS string contexts, bare `h2` selectors.
- **CSS completeness:** Reports any missing required CSS variables from the `:root` block.

The script exits with code 1 if any assertion fails (errors). Warnings (anti-patterns, missing vars) are reported but do not fail the run.

## Things That Break

These are lessons from actual bugs. Do not repeat them.

**Never create SVG via `innerHTML`.** SVG requires the correct XML namespace. Elements created via `innerHTML` in an HTML context may not render. Use Canvas for simple graphics or `document.createElementNS('http://www.w3.org/2000/svg', tag)` if SVG is required.

**Do not use CSS variables in JS-generated inline styles.** A `style="color:var(--muted)"` set via JS works if the element is in the DOM, but it is fragile and hard to debug. Hardcode hex values in JS-generated styles, or look up the variable:

```js
const muted = getComputedStyle(document.documentElement).getPropertyValue('--muted').trim();
```

**Plotly legend colors break with per-bar color arrays.** When a trace has `marker.color` set to an array (e.g., different colors per bar for highlighting), Plotly uses the first element's color for the legend swatch. If the first element is dimmed, the legend loses its real color. Fix: use a single `marker.color` for the trace and dim via `marker.opacity` array instead.

**Cosine similarity with negative result vectors.** In toy embedding spaces where all word vectors are non-negative (0–1), vector subtraction can produce negative components. Cosine similarity then ranks orthogonal (unrelated) words higher than semantically close words with negative dot products. Fix: clamp the result vector to non-negative before the nearest-neighbor search. Display the raw (unclamped) vector for pedagogical transparency.

**Hardcoded presets that contradict their labels.** See the Assertions section below — this is now a standardized practice, not just a warning.
