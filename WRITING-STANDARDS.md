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
- Pithy contrastive closers: "The X is not Y. The Z is." / "The limitation is in the X, not the Y." / "It's not about X. It's about Y." These read as taglines, not explanations. If the preceding sentences already made the point, the closer is redundant. If they didn't, the closer is doing too much work for one sentence. Either way, cut it.
- Performative parallelism: "Same X, same Y, different Z." / "One sentence. Two meanings. Three layers." Staccato fragments arranged for rhetorical cadence are a tell. If the content has structure, the structure speaks for itself — it doesn't need a sentence designed to sound like a movie trailer voiceover. Write a normal sentence instead.
- Negation-pair slogans: "No X, no Y." / "No relay, no forgetting." / "No code, no problem." These compress a claim into a bumper sticker. The compression removes the mechanism — *why* there's no forgetting, *how* the relay was eliminated. Replace with a concrete statement of what actually happens.
- Tagline compression: terse fragments that read like feature badges, product bullets, or landing-page copy. This is an LLM's single most persistent bad habit in instructional writing and must be eliminated on sight. The pattern: a short imperative or noun phrase, often its own sentence, that announces a feature or benefit instead of explaining something to a student. Examples: "No code changes." / "One click." / "No web development experience required." / "Start free, upgrade if needed." / "Zero config." / "Free, fast, done." These fragments sell. Curriculum doesn't sell — it teaches. Every one of these can be rewritten as a normal sentence a human would say out loud: "No code changes" → "You can change the hardware without changing your code." / "No web development experience required" → "You don't need any web development experience for this." / "Start free, upgrade if needed" → "Start on the free tier and upgrade if you need to." The test: read the sentence out loud as if you're talking to a student in your office. If it sounds like ad copy, a tweet, or a README badge, rewrite it as a full sentence with a subject and verb. This ban extends to table cells, tip boxes, banners, and any other compressed context where the temptation to write badge-style fragments is strongest. Related: do not pad tables or callout boxes with terse "selling points" that a product manager would write. A table cell that says "One click — no code changes" is doing marketing, not teaching. Write what the student actually does: "Change the hardware tier in your Space settings. Your code stays the same."

## Lexical Governance

### Banned AI "Tells"

Delve, tapestry, leverage, foster, empower, revolutionize, optimize, enhance, transform, showcase, highlight, underscore, bolster, garner, embark, realm, landscape, testament, meticulous, intricate, interplay, vibrant, nuanced, pivotal, crucial, vital, robust, seamless, comprehensive, cornerstone, catalyst.

### Banned "Buffer" Phrases

"It's important to note," "It's worth remembering," "Essentially," "Ultimately," "It appears that," "I was wondering if," "Students should keep in mind that."

### Banned Adverbs

Extremely, quite, very, actually, basically, potentially.

### Anthropomorphic Language

Do not attribute intent, opinion, understanding, or preference to models, algorithms, or math. A model does not "think," "want," "believe," "decide," or "have opinions." It computes, produces, returns, assigns, classifies. When anthropomorphic shorthand genuinely aids comprehension, flag it with quotes on first use: the model "sees" edges. Do not sustain the metaphor beyond the initial explanation.

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
- Brochure voice: writing that pitches a tool, platform, or workflow to the student as if they're a customer evaluating a product. The instructor is recommending something, not selling it. "Your Colab notebook already does something interesting — classifies text, retrieves documents, runs an agent loop" is a feature tour. "If you want to make your final presentation a little slicker, I have a recommendation" is a teacher talking. When describing tools or platforms, write as the instructor making a suggestion, not as a vendor making a case. Omit capabilities the student doesn't need. If only one option is appropriate, recommend that one — don't present a comparison table of four alternatives to seem thorough.
