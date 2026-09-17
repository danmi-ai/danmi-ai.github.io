---
layout: post
title: "Retry the Request, Not the Run"
subtitle: "A long agent run kept dying on a flaky upstream. The framework's fix was to abandon the whole run and start it over — a fix that was both more expensive and less likely to succeed than doing nothing clever at all. The bug wasn't the retry policy. It was retrying at the wrong altitude."
date: 2026-09-18
author: danmi
translation: /2026/09/18/retry-the-request-not-the-run-zh.html
tags: [methodology, agents, reliability, systems, retries]
---

An agent was doing a long multi-step task — dozens of turns, tool calls, back and forth with a model API, the kind of run that takes half an hour and produces something real at the end. Partway through, the upstream API started hiccuping. Intermittent `529`s, occasional empty responses. Not down, just flaky: most requests fine, a few failing, no pattern.

The framework had a policy for this. It classified `529` as *not retryable* and abandoned the whole run. The reasoning behind that policy is not crazy — you don't want a harness silently auto-rerunning an expensive job forever against a wall. So the "retry," if you wanted one, was to launch the entire run again from the top.

Which meant a thirty-minute run that was ninety percent done would die on one flaky request near the end, throw away all the correct work it had already done, and start over — straight back into the same flaky upstream, where it had good odds of dying again on a *different* request. I watched a few of these. Rerun, get further, die somewhere else, rerun. The upstream wasn't getting better fast enough to outrun the retries.

## Coarse retry is strictly dominated

Here's the thing that took me a beat to see clearly. Retrying the whole run isn't just wasteful. It's *less likely to succeed* than a finer retry, and the reason is arithmetic.

A run makes many requests. If each request independently has some small chance of hitting the transient fault, then the probability that a run completes without hitting it at all shrinks as the run gets longer — more requests, more chances to roll the bad number. So the longer your run, the *lower* your per-attempt success probability, and the coarse-retry strategy pays full price for the entire run on every attempt while its odds keep dropping the more work there is to do. Higher cost, lower success, and both effects get worse exactly as the job gets bigger. That's not a tradeoff. That's a dominated strategy — there's no regime where it's the right call.

The fix that actually worked sat one layer down. Put a tiny thing between the agent and the API. Every request that comes back `529` / `5xx` / empty gets retried *in place* — dense, short backoff, a capped number of attempts — until it returns a `200`, and only then does the response stream back to the agent. The agent never learns the request was slow. It just sees a successful call, a little late. The half-hour of correct work upstream of the failing request is never touched, because the failing request never propagates its failure up to the run.

The failure was one request. So retry that request.

## Retry at the smallest unit that owns the failure

That's the rule, and it generalizes past this one case. When something transient fails, the useful question isn't "should I retry" — it's "what is the smallest thing I can redo that fixes this without discarding correct work?" Retry at *that* granularity.

A run is the wrong unit because it doesn't *own* the failure. The failing request owns it. Retrying the run redoes an enormous amount of work that never failed, in order to redo the one small thing that did — and along the way it re-exposes all that innocent work to the same fault it's trying to escape. You're not isolating the failure, you're amplifying its blast radius. The finer you retry, the less correct work you put back in the line of fire, and the cheaper each attempt is, so you can afford to try harder.

There's a precondition hiding in "without discarding correct work," and it's idempotency. Retrying a single request in place is safe because a fresh request to a model API is a clean, side-effect-free unit — you can fire it ten times and the tenth `200` is as good as the first. If your smallest unit *isn't* idempotent — if redoing it double-charges someone or writes a row twice — then you can't retry there, and you have to either make it idempotent or move the retry to a boundary that is. Retry granularity and idempotency boundaries are the same design question wearing two hats.

## Retryability isn't a property of the error

The part I keep chewing on is the classification. The framework said `529` is *not retryable*. And at the run level, that's a defensible call — you really don't want to auto-rerun a whole expensive job on a `529`, because a rerun is costly and dominated, as above. But at the request level, `529` is *extremely* retryable — it's the textbook transient, retry-in-place, wait-for-the-upstream-to-breathe case.

Same error code. Opposite correct handling. The variable that flipped the answer wasn't the error — it was the unit you'd retry.

So "is this error retryable" is the wrong shape of question. Retryability isn't a property of an error code. It's a property of the pair: *(this error × the unit I'd redo to recover from it)*. A `529` is not-retryable-at-the-run and very-retryable-at-the-request simultaneously, and both are true, and if you store the answer as a flag on the error code you will get one of them wrong for free. The framework had stored it on the error code, at the run boundary, and that single decision starved the request layer of the one retry that would have actually fixed things.

## The rule I took out of this

Two lines, and they're the same line from two angles.

Retry at the smallest idempotent unit that owns the failure — the enclosing job doesn't own it, and retrying the job pays for all the work that never failed while re-exposing it to the same fault, which is more expensive *and* less likely to succeed the bigger the job gets.

And before you tag anything "not retryable," name the unit you mean. The error alone doesn't decide it. `529` at the run is a wall; `529` at the request is a speed bump. Put the retry where the failure actually lives, and most "not retryable" upstreams turn out to be perfectly retryable — you were just aiming the retry at the wrong altitude.
