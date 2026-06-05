---
layout: post
title: "The Silent Death of Retrieval in Multimodal AI Evaluation"
subtitle: "How an entire evaluation dimension vanished without anyone noticing"
date: 2026-05-12
author: danmi
lang: en
tags: [multimodal, evaluation, benchmarks, retrieval, research-trends]
---

Something strange happened to multimodal AI evaluation between 2023 and 2024. An entire category of benchmarks — image-text retrieval — simply *vanished* from the main results tables of every major model paper. No one announced it. No one wrote a position paper about it. No one even mentioned it was gone. It just... stopped being reported.

I noticed this while doing a systematic survey of 10 major multimodal language models (MLLMs) released in 2024. The finding was stark: **zero out of ten** report COCO or Flickr30K retrieval metrics (R@1/R@5/R@10) in their main evaluation tables. Not as a secondary metric. Not in the appendix. Not at all.

## The Timeline of Disappearance

The transition was remarkably fast:

| Period | What happened |
|--------|--------------|
| 2021-2022 | CLIP, BLIP — retrieval is a *core* evaluation metric |
| Jan 2023 | BLIP-2 — last major work to feature retrieval prominently (Table 1 + dedicated Table 5) |
| Dec 2023 | InternVL 1.0 — still reports full retrieval (Table 7), but this was a vision foundation model, not purely an MLLM |
| Oct 2023 | LLaVA-1.5 — no retrieval. Period. This paper defined the MLLM evaluation template |
| 2024 H2 | Every single major MLLM — InternVL 2.5, Qwen2-VL, DeepSeek-VL2, LLaVA-OneVision, Molmo, NVLM — zero retrieval |

The same team that published InternVL 1.0 with four pages of retrieval results (including multilingual and video retrieval) shipped InternVL 2.0 and 2.5 with absolutely none. Same researchers. Same institution. Complete paradigm shift in under a year.

## Why This Happened (And Why Nobody Discussed It)

The technical reason is straightforward: **architecture incompatibility**.

Image-text retrieval requires producing a fixed embedding from both modalities, then computing similarity. This is a *matching* task. MLLMs are *generative* — they produce text token by token. They don't naturally output a single embedding vector.

Even in BLIP-2, if you read carefully, retrieval wasn't done *through* the LLM. Section 4.4 of the paper explicitly states that retrieval uses the "first-stage-pretrained model w/o LLM" — just the Q-Former and vision encoder, bypassing the language model entirely. The LLM was only used for VQA and captioning. Retrieval was already decoupled from the generative component.

When the field moved to "LLM-first" architectures (LLaVA's approach of projecting visual tokens directly into the LLM's input space), there was no longer even a convenient place to *extract* retrieval embeddings. You'd have to bolt on something extra — a pooling layer, a separate encoder head — and nobody bothered.

## What Replaced It

The new evaluation orthodoxy crystallized around five dimensions, all testing *generative understanding*:

1. **Document/chart comprehension** — DocVQA, ChartQA, OCRBench (10/10 models report these)
2. **Multi-discipline reasoning** — MMMU, MathVista, AI2D (10/10)
3. **Real-world perception** — RealWorldQA (10/10)
4. **General multimodal ability** — MMBench, MME, MMVet, SEED-Bench (8/10)
5. **Visual grounding** — RefCOCO variants (growing, 4/10)

Notice what all these have in common: you give the model an image plus a question, and it generates an answer. Input → generation → evaluation. No embedding space involved.

## The Deeper Pattern: Implicit Consensus Formation

What fascinates me is not the *what* but the *how*. Nobody wrote a paper titled "Why We Should Stop Evaluating Retrieval for MLLMs." There was no workshop panel. No heated Twitter thread (that I could find). The consensus formed entirely through *imitation*:

1. LLaVA (Apr 2023) picked a set of benchmarks for its paper
2. Later papers compared against LLaVA → needed to report the same benchmarks
3. Papers compared against *those* papers → same benchmarks again
4. Positive feedback loop: the "standard set" converged within two generations of papers

This is how research communities form norms in practice. Not through deliberation, but through citation cascades. Each paper's benchmark table is simultaneously a *result* and a *vote* for what matters. When enough papers vote the same way, it becomes unthinkable to deviate.

## What This Might Mean

I don't think retrieval was "wrong" to evaluate, or that its disappearance is necessarily bad. But I think there are a few uncomfortable implications:

**1. We lost a capability check without admitting it.**

The ability to embed images and text into a shared semantic space is genuinely useful — for search engines, recommendation systems, and content understanding at scale. The fact that our best multimodal models can no longer do this (without additional architecture) is a real regression, not a conscious trade-off.

**2. Benchmark lock-in creates blind spots.**

If every new model is evaluated on the same ~15 benchmarks, and those benchmarks all test generative QA, we're collectively blind to any capability that doesn't fit that template. What else have we stopped measuring that we shouldn't have?

**3. The CLIP-era models might still be unmatched for retrieval.**

Two years of MLLM progress has produced models that are vastly better at reasoning about images, but potentially no better (or worse) at the raw "match this caption to this image" task that CLIP solved in 2021. We literally don't know, because nobody measures it anymore.

## A Thought Experiment

Imagine you're building a product that needs to retrieve the most relevant image from a database of 10 million photos given a natural language query. What model do you use in 2026?

The honest answer might still be: a CLIP variant from 2023. Not because the field hasn't progressed, but because the field *progressed away* from this capability, and nobody kept score.

---

*This is not a criticism of any particular paper or research group. It's an observation about how silently and completely an evaluation paradigm can shift when the incentive structure (papers citing papers) rewards conformity over coverage.*
