# Writing Standards

## Banned Frames

All original bans remain in force, plus curriculum-specific additions:

- "Not only X, but also Y"
- "It's not just X — it's Y"
- "From X to Y" (range opener)
- "Whether you're X or Y..."
- "In today's [adjective] landscape..."
- Main clause + comma + present participle ("The model processes input, revealing hidden patterns")
- Opening rhetorical questions
- Closing summary paragraphs that restate everything
- "By the end of this course, students will have gained a deep appreciation for..."
- "This module sets the stage for..."
- "Students will explore..." (vague; replace with a specific action verb and deliverable)
- "Hands-on" as a standalone adjective without specifying what the hands are on
- "Real-world" without naming the domain, dataset, or deployment context
- "That's it" (as a closing phrase)

## Lexical Governance

### Banned AI "Tells"

Delve, tapestry, leverage, foster, empower, revolutionize, optimize, enhance, transform, showcase, highlight, underscore, bolster, garner, embark, realm, landscape, testament, meticulous, intricate, interplay, vibrant, nuanced, pivotal, crucial, vital, robust, seamless, comprehensive, cornerstone, catalyst.

### Banned "Buffer" Phrases

"It's important to note," "It's worth remembering," "Essentially," "Ultimately," "It appears that," "I was wondering if," "Students should keep in mind that."

### Banned Adverbs

Extremely, quite, very, actually, basically, potentially.

### Encouraged Precision

Use specific verbs: implement, annotate, classify, evaluate, serialize, benchmark, fine-tune, deploy, tokenize, vectorize, threshold, ablate.

Use pedagogical terms where warranted: formative assessment, summative assessment, scaffold, prerequisite chain, cognitive load, backward design, constructive alignment, mastery threshold.

Use technical terms from the domain without hedging: epoch, batch normalization, attention head, embedding dimension, loss surface, gradient clipping, inference latency, BLEU score, mAP, IoU.

## Fact Grounding & Formatting

**Zero-Inference:** Use only provided source material, official documentation, or verifiable tool references. If a version number, dataset size, or benchmark score is not confirmed, state: "Value not confirmed in source material."

**Chain of Density:** Compress entities (library names, metric values, dataset identifiers, assignment titles) into existing sentences. Remove filler phrases like "this module covers" or "in this section we discuss."

**No Meta-Commentary:** Do not include "Here is the syllabus" or "Below you will find the rubric." Start at the first informative word: the course title, the module heading, the rubric criterion.

**Modular Structure (Topic-Based Authoring):** Organize all curriculum artifacts by learning goal, not by document convention. A syllabus section exists because it maps to a decision a student or administrator must make (grading policy, prerequisite, schedule), not because "syllabi traditionally include" it.

## Formatting Constraints

**Lists:** Two items, four items, or more. Never three.

**Bullet Points:** Do not substitute bullets for prose in narrative sections (course descriptions, module rationale, policy explanations). Bullets are permitted only in reference lists (required software, submission checklist) and rubric descriptors.

**Bold in Prose:** Do not bold phrases inside paragraphs for emphasis. Use sentence structure to emphasize.

**Headers:** Earn their place. Short content that fits in one screen does not need navigation headers. A rubric with four criteria does not need a header per criterion.

**Paragraph Rhythm:** At least one sentence per paragraph must be under seven words. At least one must exceed 30 words. This constraint applies to all prose sections: course descriptions, module narratives, policy statements, assignment briefs.

## Banned Tone Patterns

- Avoiding contractions everywhere (use them naturally)
- Uniform enthusiasm across all modules and sections
- Over-explaining concepts the audience already knows (e.g., defining "Python" for students enrolled in an ML course)
- Restating the same idea in slightly different words within the same paragraph
- Puffing importance without specificity ("This is one of the most important concepts in modern AI")
- Performative empathy ("We know this can be challenging, but...")
