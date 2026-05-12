# slides/ — Shared Interactive Demos and Lecture Decks

Single-file HTML demos and PPTX decks shared across both courses. See `DEMO-STANDARDS.md` (project root) for the conventions every interactive demo follows.

`build/lint_demos.py` checks new demos against those conventions before they go to students.

## Interactive Demos

| File | Topic | Used by |
|------|-------|---------|
| `index.html` | Demo gallery (linked from Canvas) | Both |
| `attention-demo.html` | Self-attention / QKV pipeline, multi-head view | AIML 2003 |
| `cnn-architecture-demo.html` | CNN architecture walkthrough | AIML 2013 |
| `confusion-matrix-demo.html` | Confusion matrix and per-class metrics | Both |
| `cosine-similarity-demo.html` | Cosine similarity on vectors | Both |
| `embeddings-meaning-demo.html` | What a learned embedding encodes | Both |
| `hallucination-demo.html` | Why models produce fluent falsehoods | AIML 2003 |
| `hog-demo.html` | HOG feature extraction stages | AIML 2013 |
| `logistic-regression-demo.html` | LR on text (2 words → 5,000-word vocab) | AIML 2003 |
| `neural-network-demo.html` | Why hidden layers untangle nonlinear data | Both |
| `pixel-histogram-demo.html` | Brightness histograms, thresholding, equalization | AIML 2013 |
| `tfidf-pipeline-demo.html` | Full 6-stage TF-IDF + LR pipeline | AIML 2003 |

## Lecture Decks (PPTX)

| File | Used for |
|------|----------|
| `lab1-week1-highlights.pptx` | Week 1 lab highlights (shared) |
| `module3-intro-nlp.pptx` | Module 3 intro deck — NLP |
| `module3-intro-cv.pptx` | Module 3 intro deck — CV |
| `final-class.pptx` | Final class wrap-up (shared) |

## Notes

Slides are **not part of the build pipeline** — `build.sh` does not process this directory. Link demos and decks directly from Canvas pages or share them as files.

Course-specific lecture decks live in `aiml2003/slides/` and `aiml2013/slides/`. Use this directory for assets that span both courses.
