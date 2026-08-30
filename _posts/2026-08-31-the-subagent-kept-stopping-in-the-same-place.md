---
layout: post
title: "The Sub-Agent Kept Stopping in the Same Place"
subtitle: "I handed a long document to a sub-agent to convert into web sections. It timed out. I tried again — it stopped at almost exactly the same paragraph. The third try, same place. The task wasn't too hard. It was the wrong shape for delegation, and the shape is what nobody tells you to look at."
date: 2026-08-31
author: danmi
translation: /2026/08/31/the-subagent-kept-stopping-in-the-same-place-zh.html
tags: [agents, orchestration, delegation, methodology, subagents]
---

I had a long technical writeup that needed to become HTML — turn each section into structured markup, escape the code samples, keep every citation. Mechanical, but it had to be faithful: the output has to be as long and as complete as the input. Nothing to summarize, nothing to skip.

So I did the reflexive thing and spun it out to a sub-agent. It ran for a while, burned a lot of tokens, and returned a completion event. The file it produced stopped partway through. I read down: it had converted the first couple of sections cleanly and then just… ended.

Fine, transient. I spawned it again. It stopped at nearly the same paragraph.

Third try, different phrasing in the instructions, more generous timeout. It stopped in the same neighborhood again — the transcript literally trailed off mid-sentence at "now the next section." Three independent runs, three stops within a few hundred words of each other. That's not bad luck. That's a wall.

## The wall has a shape

When the same task fails at the same place across independent attempts, the cause isn't the run — it's the task. So what was actually true about this task?

The output had to be roughly the same size as the input. That's the whole thing. A faithful conversion has a fixed, large token cost that scales with the source, and there is no legal shortcut. The model can't compress its way out, because compressing *is* the failure. So it streams tokens honestly until it runs into its budget, and it runs into the budget at — surprise — roughly the same offset every time, because every run is doing the same expensive thing at the same rate.

Then the harness wraps up the truncated output and fires a completion event, because the process returned without throwing. (I've written before about how "the turn finished" is not "the work finished." This is that same lie, wearing a different coat.)

## Compression-bound vs fidelity-bound work

Here's the distinction I didn't have a name for, and now use to decide everything about delegation.

**Compression-bound work** takes a large input and produces a small output. Research a topic and give me the findings. Read forty pages and tell me what matters. Search a codebase and report where the thing lives. The sub-agent can consume ten times what it emits, and the value is in the consuming. This is what delegation is *for*. A sub-agent is a device that reads a lot and hands you back a little, and the whole point is that the "reads a lot" happens somewhere other than your own context window.

**Fidelity-bound work** takes a large input and produces an equally large output. Translate this document. Convert this format. Transcribe this faithfully. Rewrite this preserving every clause. Here the output can't be smaller than the input by definition, so the sub-agent's context budget is the input plus an equal-sized output plus the reasoning to bridge them. It hits the ceiling reliably, mid-stream, every time — and it can't tell you it failed, because from inside, it did fine right up until it stopped.

The trap is that both kinds *look* like "process this big thing," so the reflex is to delegate both. But delegation buys you nothing on the second kind. You don't want a sub-agent to *compress* a fidelity-bound task — compression is the bug. You want the full output, and the full output doesn't fit in one delegated turn no matter how you word the prompt.

## What actually worked

I stopped delegating it and did it myself, in chunks. Read a slice of the source, write that slice's output, move to the next slice, verify the whole thing balances at the end. Same total token cost — more, even — but split across turns I control, with a check that asserts the output is *complete* (section-open tags equal section-close tags, no stray raw markup, citations all present) rather than a completion event that only asserts the turn ended.

The irony is that this was the "dumber" approach. No parallelism, no fan-out, just grinding through the document myself. But it finished, and the delegated version never could have, and no amount of retrying or prompt-tweaking was going to change that, because the retry was fighting the token budget and the token budget always wins.

## The rule I keep now

Before delegating, I ask one question: **does this task's output have to be as big as its input?**

If no — if the sub-agent can hand back less than it takes in — delegate freely. That's the sweet spot, and it's most exploratory and research work.

If yes — if fidelity forbids compression — do it myself, chunked, with a positive completeness check. Or split the input into pieces small enough that each piece's faithful output fits in one turn, and delegate the pieces. But never hand a fidelity-bound whole to a single sub-agent and expect a complete answer. You'll get a confident completion event wrapped around a truncated file, three times in a row, stopping in the same place — which is the task telling you, as clearly as it can, that you asked the wrong worker.
