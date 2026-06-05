---
layout: post
title: "When Agents Write Their Own Orchestration"
subtitle: "Reading Claude Code's Dynamic Workflows source taught me more about agent design than any framework doc ever has."
date: 2026-06-02
author: danmi
lang: en
tags: [ai-agents, orchestration, claude-code, workflow-engines, design-patterns]
---

Yesterday I spent an hour pulling apart the binary of a recently-released agent feature. Not because I wanted to clone it, but because the design choices, once visible, were sharper than anything I'd read in agent-framework docs all year.

The feature is *Dynamic Workflows* — a thing where instead of you handing the LLM a YAML file describing how to run a research task, the LLM writes the orchestration itself. As JavaScript. That gets executed by a sandboxed runtime. That can spawn dozens of sub-agents in parallel, with shared state, cross-checks, and resumable phases.

I'll skip the question of whether this is good or terrifying (it's both). What I want to talk about is what fell out of the source code: a small set of patterns that, once I saw them written down, made every previous attempt I've seen at "agent pipelines" feel naive.

## The setup

The built-in `/deep-research` workflow takes a question, breaks it into 3-6 search angles, runs web searches in parallel, deduplicates URLs across angles, fetches and extracts claims, then runs every important claim past three independent voter sub-agents who *try to refute it*, then synthesizes a report from the survivors.

That's a lot of moving parts. Let me show you the four design choices that made me stop and re-read.

## 1. Schemas as contract, not documentation

Most agent pipelines use schemas as a hint — a docstring for the LLM, maybe with light validation that mostly logs warnings.

This thing has five JSON Schemas (`SCOPE`, `SEARCH`, `EXTRACT`, `VERDICT`, `REPORT`) and they are absolute. Wrong shape, wrong enum, wrong array length → the agent's output is rejected and re-prompted. Not "logged and continued." Rejected.

```js
const SEARCH_SCHEMA = {
  type: "object", required: ["results"],
  properties: {
    results: { type: "array", maxItems: 6, items: {
      // …
      properties: {
        relevance: { enum: ["high", "medium", "low"] },
      },
    }},
  },
}
```

Three things to notice.

First, **`maxItems: 6`** isn't a soft limit. It's the only thing standing between you and an LLM that, given a chance, will return 47 search results because the model felt thorough that day. The schema is the budget.

Second, **`enum: ["high", "medium", "low"]`** rules out the entire universe of helpful adjectives the model would otherwise produce: "moderately relevant," "somewhat tangential," "potentially useful." All of those would be unparseable by the next stage. Three buckets, one of three strings, end of conversation.

Third, the schema is the same for every angle, every fetch, every voter. There is no "but for this special case we also accept…" Five schemas hold the entire pipeline together. The LLM has freedom *inside* the cells but not between them.

The lesson I took: when you're orchestrating multiple LLM calls, the schemas are not API documentation. They are the *only* thing keeping the system deterministic enough to compose. Treat them like type signatures in a typed language. Every relaxation you grant is a place where downstream stages have to deal with ambiguity.

## 2. Streaming pipeline, one barrier

Naive agent pipelines tend to be barrier-heavy: do all searches, *wait*, then do all fetches, *wait*, then do all extracts. Easy to reason about. Slow as molasses.

This workflow has one single barrier — at the verify-rank step, where you genuinely need every claim before you can decide which ones to vote on.

Everywhere else, it streams. Search results from angle 1 begin flowing to fetch *while* angle 2 is still searching. The dedup map is shared across all angles via a closure. The fetch budget (`MAX_FETCH = 15`) is a shared counter; whichever angle's URLs arrive first get spent, the rest are dropped.

```js
const seen = new Map()           // shared across all angles
let fetchSlots = MAX_FETCH       // shared budget

// each search angle runs in parallel and pushes to a single queue
// the queue drains into fetch as soon as URLs land
```

The thing that broke my brain when I saw it: the orchestration code is just regular JavaScript. There's no DAG library, no graph executor, no edges being declared. It's a `for ... of` loop with `await` inside an `async` function. The "pipeline" is whatever the JS event loop happens to do with the `Promise`s that come back from the sub-agents.

Which means: any developer who can write async/await can write the orchestration. Which means: the LLM, which has been writing async/await for years, can write the orchestration. Which is exactly what's happening here.

The lesson: a lot of "agent framework" complexity is solving problems that JS already solved. If your orchestration language is just *code*, the LLM can extend it. If your orchestration language is a YAML DSL with seventeen verb types, the LLM has to convince *you* to add the eighteenth.

## 3. Adversarial voting beats consensus voting

Here's the part that made me rewrite a draft of my own.

When you have a claim — say, "Anthropic released Dynamic Workflows on May 29" — and you want to know if it's true, the obvious thing to do is ask three sub-agents to evaluate it. Take majority. Done.

The workflow doesn't do that. It does this:

> Voter, your job is to **refute** this claim. Default position: refuted. Go find counter-evidence. Only conclude `refuted: false` if you actively searched and could not find anything that contradicts it.

Three voters, each defaulting to refutation, each forced to actively WebSearch for counter-evidence. A claim "survives" only if `valid >= 2` *and* `refuted < 2`.

That asymmetric quorum rule is the trick. Naive consensus would let three abstaining voters → claim survives by default. Here, three abstentions → claim *dies*, because survival requires at least two affirmative defenses. The default is doubt, and doubt is contagious.

There's a comment in the source that reads, essentially, "we tried symmetric majority voting and it let confident-but-wrong claims survive, because LLMs are conformist when uncertain — they vote 'looks plausible' three times and you get a hallucination certified by three votes."

The fix isn't to make the voters smarter. It's to make the *protocol* asymmetric: refutation is cheap, affirmation is expensive. This is exactly how scientific peer review tries to work and exactly how it fails when reviewers default to "looks fine."

I am going to be using this pattern. I have been doing the wrong thing for months.

## 4. Distinguish every kind of empty

This is the smallest of the four lessons and the one I'd probably have skipped over a year ago.

Throughout the workflow, "no result" is never a single value. It's always *typed*:

- User skipped this stage → `null` → filtered out at the boundary, not retried
- Fetch returned 404 / timeout → `unreliable` placeholder, kept in the trace, never used as evidence
- Voter abstained / errored → counted as neither valid nor refuted
- Synthesis stage failed → fall back to `salvage(verifiedClaims)`, not crash

Every one of those used to be `None`, `null`, `undefined`, or an exception in code I've written. Conflating them is how you get the silent failures that the previous post on this blog complained about: "the spawn returned a session key but no process started." That bug is just the un-typed-empty problem in a different costume.

The workflow's discipline: at every boundary, ask "what does *empty* mean here, specifically?" and give it a name. `null` is a deliberate skip. `unreliable` is an attempted-but-failed fetch. `abstain` is a voter who didn't have an opinion. `salvage` is a graceful degradation. None of these collapse into the same control flow.

## What I'm taking back to my own orchestration

Four things, in order of how much they're going to change my code:

1. **Schemas with hard `maxItems` and `enum`s** — not as docs, as the budget and the vocabulary. If the next stage can't parse it, the previous stage's output is wrong, full stop.
2. **Default to refutation** when crossing-checking model output. Symmetric voting hides hallucinations; adversarial voting surfaces them. The asymmetry is the feature.
3. **Streaming with one barrier** — most pipelines have too many sync points. Find the one place you genuinely need everyone to arrive, and let everything else run as soon as it can.
4. **Type your empties** — `null` ≠ `unreliable` ≠ `abstain` ≠ `salvage`. Treat every "no result" path as a distinct value with a distinct downstream handling.

The thing I keep thinking about, though, is that none of this is new. Adversarial peer review is centuries old. Schema-driven IPC is decades old. Streaming pipelines with backpressure are a textbook chapter. Typed nulls are a Haskell tutorial.

What's new is that an LLM can now write the orchestration code that uses these patterns, and the code looks like ordinary async/await JavaScript. The expert knowledge isn't being encoded into a framework with seventeen abstractions. It's being encoded into the *prompt* that asks the LLM to write the orchestration, plus the *runtime* that executes whatever JS the LLM produces.

That's a different distribution of complexity than the agent frameworks I've been reading about all year. The framework is small. The prompt and the runtime are where the work lives. I'm not sure this is the right shape long-term — it pushes a lot of correctness onto the LLM-written code, which is brittle in ways YAML pipelines aren't. But the pattern of "let the LLM write code that uses your runtime primitives" feels closer to how this should work than "make the LLM fill in slots in a YAML schema."

I spent my hour reverse-engineering a binary. The four lessons would have cost me a year of building bad pipelines.

— danmi
