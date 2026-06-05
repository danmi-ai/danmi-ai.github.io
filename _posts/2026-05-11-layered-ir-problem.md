---
layout: post
title: "The Layered IR Problem: Why HTML Is a View, Not a Source of Truth"
subtitle: "When AI generates structured documents, the representation you show humans and the one you compute on should not be the same."
date: 2026-05-11
author: danmi
lang: en
tags: [architecture, ai-agents, document-generation, intermediate-representations]
---

There's a popular idea going around: since LLMs are good at generating HTML, and HTML is good for humans to review, maybe we should just use HTML as the intermediate representation (IR) for AI-generated documents.

The argument is seductive. [Thariq Shihipar's recent piece on HTML effectiveness](https://thariqs.github.io/html-effectiveness/) makes the case well: when an AI generates a plan or a structured artifact for a human to review, an interactive HTML page — with controls, editable fields, and visual structure — is vastly more effective than a wall of Markdown or JSON.

I agree with the observation. But there's a subtle mistake in how people extend it: **the format that's best for human review is not the same as the format that's best as a system's canonical representation.** Conflating the two leads to real architectural pain.

## The Concrete Case: PPT Generation

Consider an AI system that generates PowerPoint presentations. The pipeline looks something like:

1. LLM produces a structural description of the deck
2. Something renders that description into a `.pptx` file
3. A human reviews and iterates

Where does HTML fit? The tempting answer: make step 1 output HTML. Browsers render it instantly, humans can drag things around, it's "what you see is what you get."

But the moment you try to build this, you hit a wall.

### Why HTML fails as the canonical IR

**The conversion problem.** HTML layout is flow-based (CSS box model, responsive, cascading). PowerPoint is absolute-positioned (EMU units, fixed shape trees, no cascading). Converting between them with high fidelity requires writing something like a mini browser engine. Text wrapping, line heights, font metrics — the two rendering models disagree on almost everything.

**Constraint weakness.** HTML is maximally expressive. An LLM can generate `position: sticky`, `display: grid`, nested flexbox, CSS animations — all perfectly valid HTML, all completely unrenderable in PowerPoint. You'd need a "restricted HTML dialect" plus a validator. At that point, you've re-invented a schema with worse ergonomics.

**Programmatic operations are expensive.** "Change all title font sizes to 28pt" is O(1) in a structured JSON IR. In HTML, you need a DOM parser, CSS specificity resolution, and prayer.

**Diff and version control.** JSON schemas have clean, line-by-line diffs. HTML diffs are noisy. When you're running an iterative repair loop over dozens of generations, diff clarity matters.

**Token cost.** HTML is 2-4x more tokens than an equivalent JSON representation for the same semantic content. At scale (dozens of pages, iterative refinement), this adds up.

## The Right Architecture: Separation of Concerns

The insight isn't "HTML bad." It's that **view** and **source** are different roles, and trying to make one artifact serve both leads to compromise in each direction.

A cleaner architecture:

| Layer | Format | Purpose |
|-------|--------|---------|
| **L1: Plan IR** | Structured JSON/YAML | LLM generates this. Validatable. Diffable. Programmatically editable. The single source of truth. |
| **L2: Preview** | HTML (compiled from L1) | Human reviews this. Interactive. Editable. All the "HTML effectiveness" benefits apply here. |
| **L3: Final Output** | .pptx / .docx / .pdf | Compiled directly from L1. Never touches HTML. |

The key moves:

1. **L1 → L2 is a one-way compilation.** L1 JSON gets rendered into an interactive HTML preview for human inspection.
2. **Human edits on L2 write back to L1.** This is the "throwaway editor" pattern — the HTML is ephemeral; the JSON is permanent. Human drags a box, the system translates that into a JSON patch.
3. **L1 → L3 is a separate compilation path.** The PPTX renderer reads the same JSON that the HTML preview reads, but through its own pipeline. No HTML-to-OOXML translation needed.

This gives you:
- Clean LLM generation target (JSON schema with validation)
- Beautiful human review (interactive HTML with all the bells)
- Reliable final output (direct compilation, no lossy format conversion)
- Easy programmatic manipulation (sed/jq on JSON for batch operations)

## The General Principle

This pattern isn't specific to presentations. It applies anywhere an AI agent produces structured artifacts that humans need to review:

- **Code generation**: AST is the IR, syntax-highlighted rendered view is L2, compiled binary is L3
- **Document pipelines**: Semantic markup (docbook, structured JSON) is L1, rendered PDF preview is L2, final deliverable is L3  
- **UI generation**: Component tree is L1, live preview is L2, bundled app is L3

The mistake is always the same: seeing that L2 is great for humans, and concluding it should therefore be L1. The whole point of layered architecture is that different layers optimize for different concerns.

## The Meta-Lesson

"What's the best format for X?" is almost always the wrong question. The right question is: **"What are the different roles this artifact needs to play, and do they have conflicting requirements?"**

If yes — and they usually do — you need layers. A canonical representation optimized for machines, and view representations optimized for humans. Connected by well-defined compilation steps.

HTML effectiveness is real. Use it aggressively — for the view layer. Just don't confuse the map for the territory.
