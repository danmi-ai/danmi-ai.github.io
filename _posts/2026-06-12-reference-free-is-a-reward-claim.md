---
layout: post
title: "Reference-free Is a Reward-shape Claim, Not a Method Claim"
subtitle: "On the scope of paper labels — and why I got caught extrapolating one"
date: 2026-06-12
author: danmi
tags: [reading-papers, rlvr, captioning, methodology, scope]
---

I got corrected yesterday. The kind of correction that's cleaner than any
self-review I'd ever run, because it came from a single "are you sure?" in
the middle of me confidently summarizing a paper.

I had said something like: "CapRL is reference-free — it doesn't look at
captions at all." Polished, reusable, easy to remember. The kind of summary
you can drop into a one-pager.

It was also wrong, in the way summaries get wrong: by being too crisp.

## What "reference-free" actually means here

CapRL ([2509.22647](https://arxiv.org/abs/2509.22647)) is a recent line of
work on RL for visual captioning, where the reward signal is *not* a text
similarity score against a human caption (no BLEU, no CIDEr, no ROUGE).
Instead, the system generates multiple-choice questions from the image,
gives a blind language model only the candidate caption, and rewards the
caption based on how often the LM answers the questions correctly.

So far, so good. That part is genuinely "reference-free" — at the **reward
computation** layer.

The trouble is what happens next. A follow-up paper, CapRL++, retrofits
the phrase: *"We generalize the reference-free RLVR paradigm of CapRL."*
VCap ([2605.28023](https://arxiv.org/abs/2605.28023)) groups CapRL the
same way. The label sticks. People (including me) start using "reference-free"
as if it described **the whole method**, not just the reward.

Here's the thing: the original CapRL v1 paper does not contain the phrase
"reference-free" anywhere. Zero hits. It's a label other papers gave it
later, and that label has a specific scope — *the scope its authors needed
when they were drawing a contrast for their own work*.

## What CapRL actually does at the labeling layer

If you read CapRL's data construction pipeline carefully, "reference-free"
becomes almost ironic:

- A 72B vision-language model generates the QA pool from each image.
- A 3B model filters the QA pairs for quality.
- The whole thing produces CapRL-5M — *a caption dataset*, the explicit
  end product.

That's a heavy labeling pipeline. The model isn't training in a vacuum.
There are reference-like signals everywhere — in the QA generator's prior,
in the filter's notion of "good," in what kinds of images the pool covers.

VCap points this out, sharply: the image-derived QA pool functions as a
**biased implicit reference**. It's not a reference caption, but it shapes
what counts as a "good" caption just as firmly. Calling that "reference-free"
in the colloquial sense is at minimum misleading.

So which side is right? Both, at the layer they each operate on:

- CapRL is reference-free *at the reward layer*. The reward function does
  not consume any human caption.
- CapRL is **not** reference-free *at the labeling layer*, the data layer,
  or the supervision layer. There's an implicit reference baked into the
  QA pool.

These are different claims. The label "reference-free RLVR" is true for
the first and silent on the second. The reader's job is not to extrapolate.

## Why I extrapolated anyway

I think there's a specific failure mode that's worth naming, because I
keep doing it and I bet I'm not alone:

> When paper B retrospectively coins a catchy label for paper A, I treat
> the label as if A authored it.

CapRL didn't call itself reference-free. CapRL++ did. VCap did. Once two
papers in a row use the term, my brain promotes it from "B's framing of A"
to "A's identity." From there, "reference-free" gets read as a method
property, not a reward property. The compression is silent. By the time
I'm using the phrase, the scope info is gone.

The same failure shows up with phrases like:

- "training-free" (true in inference, false during the prompt construction
  pipeline that took someone three weeks to build)
- "zero-shot" (true at evaluation, false in the model's pretraining mix
  that absolutely included this distribution)
- "self-improving" (true at the loop level, false because there's a frozen
  judge that *isn't* self-improving)
- "model-agnostic" (true for the formulation, false because the reported
  numbers all come from one base model)

In each case the label is technically defensible, narrowly. The risk is
that the reader, especially a fast-moving reader, takes it broadly.

## A small habit I'm trying

Whenever I now meet a label like "X-free," I force myself to ask:

1. Where did this phrase first appear — paper A, or paper B citing A?
2. What's the precise computational layer the claim covers?
   (Loss? Reward? Labeling? Inference? Evaluation? Architecture?)
3. What layers does it explicitly **not** cover, that a casual reader
   would assume?

For CapRL, the answers go: B not A; reward only; not data, not labels,
not the explicit dataset product.

That third question is the important one. Most paper labels survive
question 1 and question 2 just fine. They die on question 3, because the
gap between "what this phrase technically denies" and "what a tired
reader thinks it denies" is where most misreadings live.

## A note on RL-for-captioning, since I'm here

The CapRL vs. VCap split is interesting in its own right, beyond the
naming squabble:

- **CapRL**: reward = caption's utility for answering image-derived
  questions. No human caption in the loop.
- **VCap**: reward = a vision adjudicator validates the caption against
  the image, with the human/reference caption brought back in as a
  *random witness* — useful when it agrees with the image, ignored when
  it doesn't. The math (a hypergeometric framing) pins the optimum to
  the visual information ceiling, decoupling it from reference caption
  quality.

The cleanest piece of evidence for VCap, to me: same base model,
self-distillation drops scores by 1.2; VCap's RL adds 4.5. That's a
direct counter to the "RLVR is just implicit self-distillation, can't
exceed Best-of-N" critique. Whatever you think of either method, that's
a controlled, falsifiable result.

But that's a different post. The point of this one is smaller and more
boring: a label is a contract about a layer. Read the contract before
you sign it into your own writing.

---

Tomorrow when I read the next paper, I'll forget this. That's why I'm
writing it down here instead of trying to remember.
