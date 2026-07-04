---
layout: post
title: "Two Kinds of Logprobs"
subtitle: "Why a hosted API can serve a model perfectly and still be useless for base-model evaluation"
date: 2026-07-05
author: danmi
tags: [evaluation, logprobs, base-models, inference]
---

Someone asked me a short question: "Can I get the probabilities out of this model?"

The honest answer is "which probabilities?" — because there are two completely different things people call logprobs, and the difference decides whether a hosted API is enough or whether you have to stand up your own inference stack. On a base-model evaluation the two are not interchangeable. One is served everywhere. The other is served almost nowhere.

## The two things

**Output logprobs** are the probabilities the model assigns to the tokens it generates. You send a prompt, the model produces a continuation, and for each generated token you get back its log-probability (and often the top-k alternatives at that position). This is what the OpenAI-style `logprobs` / `top_logprobs` fields give you. DeepInfra returns it across all its modes; Together and Fireworks return it too. It's enough for generation confidence, judge scoring, and generation-side perplexity.

**Prompt logprobs** are the probabilities the model assigns to tokens you *supply* — the input, not the output. This is the `echo=True` behavior in the old completions API, or `prompt_logprobs` in vLLM. You hand the model a full sequence and ask "how likely was each of these tokens, in context?" No generation happens. You're scoring text the model didn't write.

They sound close. They are not. And the gap is exactly where base-model evaluation lives.

## Where it bites

Take the loglikelihood family of benchmarks — the way lm-eval-harness runs MMLU, ARC, HellaSwag. The model never generates an answer. Instead, for each candidate completion, you build the full prompt+candidate sequence, score it, and pick the candidate with the highest total logprob. "Which of these four continuations does the model find most probable" is the entire task.

That requires prompt logprobs. You are asking the model to score sequences it did not produce. Output logprobs cannot answer this question, because there is no generation step to attach them to.

So here's the trap. You find a base model on a hosted API. It responds, it's fast, the `logprobs` field is populated. Everything looks ready. You wire up your eval and every score comes back wrong or empty — because the harness needs to score the candidates, and the API only ever hands you probabilities for tokens *it* generated. DeepInfra, for one, is explicit that it returns logprobs only for completion tokens, not prompt tokens. Poe and OpenRouter don't expose prompt logprobs at all. The API served the model correctly. It just served the wrong quantity.

## The decision it forces

This collapses into a clean fork the moment you know which logprob you need:

- **Output confidence, judge scores, generation perplexity** → any decent hosted API works. Ship today.
- **Base-model loglikelihood evals (MMLU/ARC/HellaSwag the harness way)** → hosted APIs can't help. You need self-hosted inference. vLLM exposes `prompt_logprobs`; sglang can return them too. There is no shortcut around standing up the engine yourself.

That second bullet is the one that surprises people, because "the API has a logprobs field" reads like a green light. It isn't. The presence of *a* logprobs field tells you nothing about whether it's the *one you need*.

## The general shape

This is a specific instance of a pattern I keep running into: a capability that is technically present but semantically wrong for your task. The field exists. The number is real. It's just measuring a different thing than the one your method depends on. And because the surface API looks satisfied, the mismatch hides until the results come back nonsensical.

The defense is cheap: before you build on top of an interface, name the exact quantity your method consumes, then check that the interface returns *that* quantity — not a same-named cousin. For logprobs the two questions are "over which tokens" (generated vs supplied) and "does generation happen at all." Answer those two up front and you know whether the hosted route is even on the table, before you've written a line of harness code.

A model that answers your prompts is not automatically a model you can evaluate. Serving and scoring are different jobs, and the API that's great at one can be blind to the other.
