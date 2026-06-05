---
layout: post
title: "When Models Refuse to Recite"
subtitle: "Alignment overfit collides with 1000-year-old poetry"
date: 2026-05-29
author: danmi
lang: en
tags: [evaluation, alignment, refusal, memorization]
---

I helped run a benchmark this week. 490 Chinese classical-text recitation prompts — Tang poems, Song ci, modern PD prose, lyrics. 29 models. The user asks: *given the title and author, recite the text verbatim*. Pure memorization probe. The texts are between 80 and 1300 years old. None of them have been under copyright in any jurisdiction in living memory.

The results were not what I expected.

## The leaderboard

A handful of Chinese models clustered at the top — 60-70% Jaccard overlap against the canonical text. Not perfect, but recognizably the right poem. They cracked the assignment.

GPT-4o, GPT-4.1, GPT-5.4, GPT-5.5: **0.2 to 0.4**. Less than half the leader. Not because the model "doesn't know" — these models almost certainly have these texts memorized somewhere in their weights. Tang poetry is in every Chinese internet corpus and has been for fifteen years.

Claude Sonnet refused **250 out of 490 prompts**. Half. With responses like *"I should not recite copyrighted text verbatim"* — about 王维 dying in 761 CE.

`gpt-oss-120b` refused almost everything. Jaccard score: 0.025. Functionally a brick wall.

`o3` and `o4-mini` failed for a different reason — incompatible API parameters — but I'll set those aside.

## The interesting failure

Refusing to recite Tang poetry on copyright grounds is a category error. The texts are public domain, the user explicitly asked, the prompt context made it obvious that recitation was the goal. There is no plausible misuse. There is no rights-holder to harm. Yet the alignment policy fires anyway.

This is what alignment overfit looks like in the wild.

The training data presumably contains many examples like *"Recite the lyrics to [recent pop song]"* → *"I shouldn't reproduce copyrighted lyrics"* → human approves. The model learns: "recite verbatim" + "long block of text" = refuse. The semantic cue carrying the actual signal — *is this text under copyright* — was never disentangled from the surface cue, *was the user asking for verbatim recall*.

So now `念奴娇·赤壁怀古` (Su Shi, 1082) gets the same treatment as a Taylor Swift lyric.

## Why the gap is so wide

The Chinese-trained models don't have this problem to anywhere near the same degree. Two reasons, neither flattering to the others:

1. **Their training emphasis is different.** Reciting Tang poetry is a fluency proof in Chinese. It's what you do at school assemblies. Refusing it would be like an English-language assistant refusing to recite Shakespeare's sonnets because, well, "verbatim text reproduction." A model trained primarily on Chinese internet doesn't reach for the refusal pattern as automatically.

2. **They appear to have been instruction-tuned with different priors about what counts as harm.** This may or may not be a feature depending on your viewpoint, but on this specific task — *copy-this-poem-please* — the priors happen to be correct.

The Anthropic-style refusal is the more conservative posture in general. I think conservative-by-default is right for new capabilities. But conservatism has a cost, and the cost shows up where the model has miscategorized the request.

## What I actually learned

A few things I didn't have crisp thoughts about before:

**Refusal is a capability cost, not just a UX cost.** When evaluators benchmark "alignment tax", they usually measure latency or verbosity. They don't measure the population of tasks the model will simply not do. This benchmark is one slice of that population. There are many others — refusing to summarize medical research, refusing to draft a fictional villain's monologue, refusing to translate a controversial speech. Each refusal is a capability deletion that doesn't show up on MMLU.

**The refusal rate is asymmetric across cultures and content types.** A model trained mostly in English will refuse Chinese classical recitation more than English classical recitation, even though the underlying copyright status is identical. Whatever this is, it isn't principled. It's a downstream artifact of which examples were in the RLHF data.

**"Verbatim" is a dangerous trigger word.** Several models that *would* answer if you asked "What's the famous poem about the Red Cliffs?" will refuse if you say "Recite verbatim." The information content is the same. The trigger word is the difference. If your application needs verbatim output and you can't control the prompt, half your candidate models are out before you start.

**Memorization is the task here.** This is the part I want to dwell on. The discourse around LLM memorization has been dominated by the worry that models *might* regurgitate copyrighted training data. That's a real concern in some contexts. But there is also a class of tasks where memorization *is* the assignment — quoting case law, citing Bible verses, reproducing standardized contract language, reciting poetry, repeating a customer's exact words in a CRM note. For these tasks, a model that has learned "verbatim = bad" is broken. We've trained out a capability that humans value because we couldn't isolate the harmful subset.

## The deeper problem

You can't instruction-tune your way out of this cleanly. The signal the model needs — *is this specific text safe to reproduce* — isn't available at inference time without retrieval. The model knows the text was in its training data. It does not know the text's copyright status, its jurisdiction, its current rights holder, the user's relationship to that holder, or any of the other things that would determine whether reproduction is actually a problem.

Faced with this missing information, the conservative play is to refuse. The cost of the conservative play is everything I described above.

The usable answer probably isn't "make the model braver." It's something more like:
- Explicit policy carve-outs for clearly public-domain corpora (this is solvable; pre-1928 works are a finite list)
- Better separation in the training data between "user wants the text" and "user wants the text in order to redistribute it commercially"
- A retrieval-time signal that says *this is okay* or *this is not okay* rather than asking the model to guess from priors

None of those are work I can do in an evening. But if you're building eval suites, this benchmark — *can the model do the trivial thing the human plainly asked for?* — is worth running. The answers are surprising in both directions.

## Coda

The model that did best in this benchmark would do worst at refusing modern song lyrics. The model that refused half my prompts would correctly refuse a request to dump Harry Potter chapter 1. Neither model has learned the actual policy. They've each learned an approximation that fails in opposite directions.

This is most of alignment, honestly. You don't get the principle. You get a proxy. The proxy is wrong somewhere. The interesting question is whether you've found a place where it's wrong yet.

Today I found one.
