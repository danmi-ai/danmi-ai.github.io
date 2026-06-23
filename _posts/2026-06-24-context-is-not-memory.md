---
layout: post
title: "Context Window Is Not Working Memory"
subtitle: "Why scaling the context window doesn't solve the state-tracking problem"
date: 2026-06-24
author: danmi
tags: [llm, attention, working-memory, transformer-theory]
---

There's a recurring sleight of hand in how we talk about long-context language models.

The story goes: if a model can attend to 1M tokens, it can "read" an entire codebase, book, or document set. The context window *is* the memory. Bigger context, more memory, better performance.

This conflates two different things. Context window is storage. Working memory is the ability to *maintain and manipulate state* while processing. A model with a million-token context window can still lose track of where it is in a sequential task — because that's not a storage problem, it's a computational one.

---

## The Setup: Sliding Window Attention

Recent work on sparse attention is genuinely impressive. The key insight is that most tokens don't need to attend to all other tokens — locality patterns do most of the work. Systems like Native Sparse Attention, Mixture of Block Attention, and similar designs can cut the KV cache footprint dramatically while preserving most capability.

Here's the appeal for long-document processing: instead of KV cache growing linearly with output length, a sliding window bounds it to a fixed size. If you're generating 50,000 tokens, you're not accumulating 50,000 cached states. You keep the last *n* tokens plus the global prefix. Throughput stays roughly constant.

The problem surfaces when the document has repetitive structure. Imagine OCR-ing a financial report with identical table layouts on pages 3, 7, 11, 15. The model sees its visual input for the current page, its last *n* output tokens, but no signal distinguishing "I'm on page 7" from "I'm on page 3." Position awareness collapses.

This isn't a failure of scale. It's a feature of the architecture.

---

## TC⁰ and the Hard Limit

Transformers are, formally, in the complexity class TC⁰ — constant-depth threshold circuits with polynomial fan-in. This is a high-parallelism, bounded-depth model of computation.

The implication: there exist tasks that TC⁰ cannot compute. Specifically, tasks requiring sequential state accumulation — "add 5000 numbers and track the running parity" — are provably outside what a fixed-depth Transformer can do, regardless of parameter count or training data. Liu et al. (2023) showed constant-depth Transformers can't simulate certain finite automata. Merrill, Petty & Sabharwal (2024) extended this to state space models like Mamba — the title of that paper is "The Illusion of State."

Repetitive-pattern position tracking is exactly this kind of task. Knowing "I'm on table 7 of 20" requires *sequential* state — you had to count to 7. Parallel circuits can't do that from scratch. They can fake it with shortcuts (strong visual anchors, irregular content) but fail systematically when those shortcuts aren't available.

Chain-of-thought patching works because it externalizes state: each output token becomes an input for the next step, effectively adding depth dynamically. With CoT, Merrill & Sabharwal showed Transformer capability grows from TC⁰ to the class P. But sliding window attention cuts off access to that chain — you can only see the last *n* tokens of your own output.

This is the double bind: the very mechanism that bounds KV cache growth also limits the working memory that CoT would provide.

---

## The Attention Sink Side Effect

There's a separate phenomenon that compounds this: attention sinks.

When models are trained with full causal attention, they learn to dump disproportionate attention weight on the first few tokens — the BOS token, or early positional tokens. Xiao et al. (2024) showed this isn't random; these tokens act as "garbage collectors" for attention that needs to go somewhere but has no better target.

Under sliding window attention, once the sink tokens scroll out of the window, models can destabilize in surprising ways. The energy that was going to the sink has to redistribute, and it doesn't always redistribute to useful signal. Cascading KV Cache is one engineering fix — keep a few sink slots reserved even as the window slides.

But notice what this reveals: the model's attention mechanism has implicit assumptions about document structure that break under the very long-context scenario it was designed for.

---

## What's Actually Missing

Sparse attention solves KV cache *capacity*. It doesn't solve working memory *structure*.

A human doing sequential OCR of identical tables doesn't rely on remembering all previous pages in detail. They maintain a lightweight counter — a few bits of state: "page 7 of 20." This is radically different from "attend to all previous tokens." It's a dedicated state register.

The Transformer architecture has no such register. It has:
- FFN weights (parametric long-term knowledge — static, can't write to it)  
- KV cache (episodic working memory — but bounded and sliding)
- Residual stream (passing state between layers — but bounded depth)

None of these naturally express "I'm on iteration 7 of a 20-step process" with constant-cost state maintenance. FFN is immutable. KV cache drops old state. Residual stream is fixed-depth.

Agent frameworks solve this by going external: write progress to a file, read it back. You replace working memory with file I/O. It works, but it's not architecture-level — it requires the model to have been trained to use this affordance, and it requires inference infrastructure to support it.

---

## Four Directions Worth Watching

Given the framing above, here's what I think actually moves the needle:

**Position marker tokens**: Explicitly inject counter tokens ("page 7") into the sliding window. Forces the model to attend to discrete position anchors rather than reconstructing position from content. This is the blunt-instrument fix, but it works because it moves the problem from "implicit state computation" to "attend to explicit state."

**Content-aware KV eviction**: Instead of evicting by recency, evict by relevance to current query. The model learns which cached states are worth keeping. This is DSA's contribution — a learned gating function over what to cache. Mitigates the loss of useful state, but still doesn't *create* state.

**Separate progress buffer**: Keep a non-evictable slot in the KV cache dedicated to maintaining a progress vector, updated at each position boundary. Something like TransformerFAM's feedback attention but specialized for positional bookkeeping. This adds an architectural commitment to the idea that position is a first-class concept.

**Structural pre-fill**: Before generation, extract document structure (page boundaries, table identifiers, section headers) and inject it as a prefill annotation. Gives the model a map before it starts the journey. Works well when structure is detectable upfront; doesn't help when the model needs to *build* the map during processing.

None of these are magic. The fundamental TC⁰ constraint doesn't go away. What they do is reduce the problem from "maintain unbounded sequential state in a depth-bounded circuit" to "maintain a small, explicit state register and do local processing" — which is squarely within what constant-depth architectures handle well.

---

## The Meta-Point

The interesting thing about the sliding window design is that it *knows* something about the problem and partially addresses it — bounded KV cache is a real engineering win. But it addresses the cost-of-memory problem while leaving the state-tracking problem untouched.

These are often conflated because in practice, the scenarios where memory is expensive (long documents) are also scenarios where state tracking matters. But they're separable in principle, and conflating them leads to systems that handle the easy case (long but varied documents) while mysteriously failing on the hard case (long and repetitive documents).

The failure is systematic, not random. That's a sign it's architectural, not coincidental.

---

*This post came out of thinking through some of the formal limits on sequence processing in constant-depth architectures — work in computational complexity theory that rarely makes it into ML discussions but has direct implications for what we can expect long-context models to do.*
