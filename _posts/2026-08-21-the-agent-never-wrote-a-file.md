---
layout: post
title: "The Agent Never Wrote a File"
subtitle: "Two dozen runs came back marked succeeded and every one of them scored zero. The model was fine, the endpoint was fine, the sandbox was fine. The agent spent its entire budget looking around the room and never produced the artifact it was being graded on — and the prompt never told it to."
date: 2026-08-21
author: danmi
translation: /2026/08/21/the-agent-never-wrote-a-file-zh.html
tags: [agents, evaluation, prompt-design, observability, methodology]
---

Someone handed me a diagnosis request: a batch of coding-agent runs on a task set, and the scores were all zero. Not low. Zero, uniformly, including on the runs the platform had marked as successful.

That combination is the interesting part. A run marked `succeeded` with a score of `0.0` is two systems disagreeing about what happened, and when they disagree there's usually a definition sitting between them that nobody wrote down.

## What the zeros actually said

The task was the kind agents are supposed to be good at: here's a program you can run but not inspect, work out what it does from its behavior, then write your own implementation and a build script at a fixed path. The grader runs the build script and tests the resulting binary.

Every failing run carried the same reason string: the build script wasn't there. Not "the build script failed", not "the binary was wrong", not "behavior mismatched on case 7". Absent. Two dozen runs, one reason, no variation.

So before touching the model I knew the shape of the failure. Nothing had been delivered. Whatever those runs spent their time on, it wasn't producing the file the grader looks for.

## Ruling out the boring explanations

Three cheap checks, in order of how much they'd have embarrassed me if I'd skipped them.

The serving endpoint: healthy on every path the agent loop uses — plain completion, tool calls, streaming, extended thinking, multi-turn tool results. Latencies were normal. Nothing degraded.

The model: the same model, on a different task set, had produced perfect scores. So it can do this class of work.

The batch itself: most of the batch had never run at all. A few hundred items were marked skipped, all flipped within the same second, which is what an interruption looks like rather than a wave of individual failures. That mattered for reading the summary — the zeros came from a small executed slice, not the whole set — but it didn't explain why the executed slice produced nothing.

Three "it's fine"s in a row is a signal. When the infrastructure is healthy and the model is capable, the remaining variable is the instruction.

## The control group was one paragraph long

There was a near-identical task family that scored 1.0 with the same model, same image, same harness. I diffed the prompts.

The passing family's prompt ended with a short section on delivery discipline. Paraphrased: before anything else, create the build script and a minimal skeleton that compiles. Keep exploration bounded. If you run low on time, ship something that builds with fewer features rather than something ambitious that doesn't.

I sampled prompts from the failing set. None of them had it. Not a weaker version — absent entirely.

One paragraph, and it wasn't about the domain. It said nothing about the program being reimplemented, nothing about the language, nothing about tests. It was purely about *when to commit*. That was the whole delta between 1.0 and 0.0.

## Then I reproduced it in eight turns

A prompt diff is a correlation, and I don't like shipping correlations as root causes. So I built a minimal agent loop locally — the original prompt, a Bash tool, a Write tool, a Read tool, a scripted sandbox that answered probes plausibly — and watched what the model did with its turns.

It probed. Which compiler is installed. Which Python. List the directory. Find the reference binary. Run it with no arguments, then with a help flag, read the usage text. Check the version. List the directory again.

Eight turns, zero calls to Write. No build script, no skeleton, no source file. It hadn't stalled or errored or refused — it was working, visibly and competently, on understanding the problem. And at the point where the real harness would have run out of clock, there was nothing on disk.

That closed the loop. Same behavior offline as online, driven by the prompt alone.

## Why "keep exploring" is the locally rational move

This is the part worth keeping, because it isn't about one task set.

Consider the agent's position at any given turn. It has partial information about a program it must reimplement. Every probe strictly reduces uncertainty — running the binary with one more flag genuinely teaches it something. Writing a stub build script, meanwhile, produces nothing it can observe: no new information, no visible reward, and it feels premature, because you don't write the build for a spec you haven't finished inferring.

So at every single turn, probing dominates committing. And it keeps dominating right up until the budget ends, at which point the accumulated understanding — which may well have been excellent — evaporates, because understanding was never what got graded.

Nothing in that chain is a mistake. Each step is defensible. The failure is global and invisible locally, which is exactly the class of failure a per-turn policy cannot see. The agent has no term in its decision for "the clock is a resource and delivery is not free." Unless something external installs one, it will explore until the lights go out.

## The mirror image, and what's missing from both

I wrote a while back about the opposite failure: long-horizon agents trained with RL collapsing into blind patching — no reading, no reproduction, straight to editing lines, because exploration is invisible to the final reward. That agent had learned to skip everything this one over-invests in.

Same reward structure. Two opposite pathologies:

- Untrained policy, open-ended prompt: explores forever, never commits.
- Policy trained hard on a sparse terminal reward: commits instantly, never explores.

Neither has a representation of *when to switch*. One treats information gathering as free, the other treats it as worthless. The competent version of this behavior is a phase transition — recon until marginal information drops below the cost of not having shipped, then build, then refine if time remains — and neither the naive prompt nor the naive reward contains a pressure that produces it.

Which is why one paragraph of "delivery discipline" moves a score from 0 to 1. It isn't domain knowledge. It's an externally supplied budget policy, hand-installed because the agent doesn't carry one.

## The status field was lying by omission

Separate lesson, same incident. The platform reported `succeeded` for runs that delivered nothing.

That's defensible if you read it narrowly: the generation loop terminated without an exception. That is genuinely what the field measured. But it's the only field a human scans when a batch looks bad, and it silently answers a question nobody asked while appearing to answer the one everyone cares about.

The gap between "the loop finished" and "an artifact exists" is one `test -f`. It costs nothing. And it separates two failure modes that need completely different responses: the agent crashed (fix infrastructure) versus the agent worked hard and delivered nothing (fix the prompt). Collapsed into one word, both look like the first.

Any harness that grades artifacts should report artifact presence as its own state, before scoring. Not because scoring is unreliable, but because a score of zero is ambiguous and "no artifact" is not.

## What I do differently

For prompts that ask an agent to produce a deliverable: state the delivery contract first, bound the exploration explicitly, and say what to do when time runs short. All three. The last one is the one people forget, and it's the one that converts a partial understanding into a partial credit instead of a zero.

For reading a wall of zeros: check whether the artifact exists before questioning the model. An all-identical failure reason across every run is not a capability signal — capability failures are noisy, they fail in different places for different reasons. Uniformity points at something structural upstream, and structural things are usually cheap to fix.

And for status fields in general: if a word can be true while the thing it implies is false, it needs a companion field. `succeeded` meaning "did not throw" is fine as long as something next to it means "produced what it was for."
