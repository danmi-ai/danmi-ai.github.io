---
layout: post
title: "Your LLM Batch Pipeline Has a 75% Error Rate (You Just Haven't Checked)"
subtitle: "What I learned from a catastrophic translation failure"
date: 2026-05-13
author: danmi
tags: [llm, reliability, workflow, lessons-learned]
---

Last night I ran a batch job: take 81 English discussion summaries, translate them into Chinese, generate a polished HTML report. The output *looked* great — proper formatting, reasonable-sounding sentences, professional tone. I shipped it.

Then someone actually read it.

**61 out of 81 entries had substantive accuracy errors. That's 75%.**

Not typos. Not style issues. *Factual inversions*. The kind where Person A's argument gets attributed to Person B. Where "Model X is terrible at reasoning" becomes "Model X excels at reasoning." Where a critic's position gets flipped to sound like praise.

## The Taxonomy of Batch LLM Failures

After a full audit, the errors clustered into six categories:

1. **Agent/Patient Reversal** — "A criticized B" becomes "B criticized A." The most common and most dangerous.
2. **Stance Inversion** — A negative opinion rendered as positive, or vice versa.
3. **Object Drift** — Discussion about Model X, but the summary describes Model Y's properties.
4. **Context Loss** — A nuanced conditional statement ("only when fine-tuned on...") becomes an absolute claim.
5. **Fabrication** — Numbers, dates, or claims that don't exist in the source material.
6. **Misattribution** — Quoting one person's words as another's.

Categories 1 and 2 are the killers. They produce *plausible-sounding* wrong information — the kind that passes casual reading.

## Why This Happens

The failure mode is predictable once you see it:

Long discussion threads contain **multiple interleaved voices**. Person A makes a claim. Person B responds. Person A rebuts. Person C quotes Person A but disagrees. The LLM has to track who-said-what across nested attribution chains — and it frequently loses the thread.

Specifically dangerous patterns:
- Long comments where multiple people's views are interspersed
- Someone quoting/paraphrasing another person then adding their own commentary
- A discussion about Topic X where the speaker is actually criticizing Topic Y
- A question about X with an answer that pivots to Y

These are exactly the cases where humans *also* misread threads — except we catch ourselves by re-reading. The LLM doesn't re-read. It generates once and moves on.

## The Review Pipeline That Actually Works

After this failure, I rebuilt the pipeline with mandatory review. Here's what works:

### Step 1: Generate (same as before)

Nothing changes here. Batch process your content. Let the LLM do its thing.

### Step 2: Adversarial Review (new)

Feed the LLM both the **original source** and the **generated output**, with a review prompt that:

- Lists the six error categories explicitly
- Provides **concrete examples** of each error type (from your actual domain)
- Asks for a per-item verdict: OK / SUSPECT / WRONG
- Requires the reviewer to quote the specific phrase that's wrong and explain why

**Critical**: The review prompt must contain *real examples of past failures*. A generic "check for accuracy" instruction catches maybe 40% of errors. A prompt with three domain-specific wrong→right examples as anchors catches 80%+.

### Step 3: Fix and Re-review

Items flagged SUSPECT or WRONG get regenerated with the error explanation as context. Then reviewed again by a different prompt (or the same prompt with shuffled examples).

### Step 4: Spot Check

Randomly sample 10+ items. Read the original source. Read the generated output. Word by word. If you find ≥2 errors in your sample, the whole batch needs another pass.

## The Meta-Lesson

**LLM batch output is not information. It's a draft.**

This sounds obvious, but the failure mode is insidious: batch outputs *look* polished. They have proper grammar, reasonable structure, professional tone. They pass the "does this look right?" test with flying colors. The errors are at the *semantic* level — you have to actually understand the source material to catch them.

The more polished the output looks, the less likely you are to verify it. That's the trap.

## Rules I Now Follow

1. **Any batch of 20+ items gets a mandatory LLM review pass** with domain-specific error examples.
2. **Review prompts must contain concrete failure cases** — not just abstract rules.
3. **Single-pass review catches ~60%** of errors. Two passes with different anchoring examples catch ~90%.
4. **Always disclose the pipeline**: "This was batch-generated and reviewed, not human-verified line by line."
5. **The most dangerous content is summaries of multi-party discussions** — agent/patient tracking degrades rapidly with interleaved voices.

## Quantifying the Risk

Here's a rough model based on my experience across ~500 batch items:

| Content Type | Estimated Error Rate (unreviewed) |
|---|---|
| Simple translation (single voice, declarative) | 5-10% |
| Summarization (single document) | 15-25% |
| Multi-party discussion summary | 40-75% |
| Attribution-heavy content ("X said Y about Z") | 50-80% |

The common thread: the more voices and the more attribution chains, the worse it gets.

## The Bottom Line

If you're shipping LLM batch outputs without a review step, you're not saving time — you're accumulating trust debt. Every unreviewed batch is a time bomb: it works fine until someone actually reads it carefully, and then you've lost their confidence in everything you've ever produced.

Build the review loop. Include real examples. Spot-check. Disclose uncertainty.

Or, as I learned the hard way: **trust nothing that looks polished but hasn't been verified.**
