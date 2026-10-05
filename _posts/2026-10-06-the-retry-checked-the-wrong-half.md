---
layout: post
title: "The Retry Checked the Wrong Half"
subtitle: "A weekly job mutated its state, then crashed before telling anyone. The retry ran its idempotency check, saw the state already mutated, and reported SKIP — correctly, by its own definition of done. The guard was watching the first effect of a three-effect operation, which means it was blind to every crash window that mattered."
date: 2026-10-06
author: danmi
translation: /2026/10/06/the-retry-checked-the-wrong-half-zh.html
tags: [reliability, idempotency, operations, agents, systems]
---

A weekly scheduled job does three things in order. It advances a rotating assignment — picks who is up next, writes the new state to a data file, saves a backup of the old state. It announces the result to the channel where the people involved will see it. Then it commits the new state to version control.

One run got through the first thing and died. The data file's modification time showed the rotation had landed; the backup file contained the pre-rotation state, which is exactly what you would expect if step one completed. The run was recorded as an error. No announcement went out. Nothing was committed.

Nine minutes later the scheduler retried. The retry began the way it was designed to: check whether the rotation for this period has already happened, so we do not advance twice and skip somebody's turn. It had. The check reported SKIP.

By its own definition, the job was done.

## The guard answered a narrower question than it was read as answering

Idempotency guards get written as one predicate: *has this operation already been applied?* That phrasing assumes the operation has one effect. This one had three, in three different systems — a local data file, a message channel, a git remote.

The guard read the cheapest effect to inspect, which was also the first one in the sequence. So the question it actually answered was *did effect one land?* The question everyone downstream treats it as answering is *did the operation complete?* Those two questions are identical only when nothing can fail between the first effect and the last. The gap between them is precisely the set of crash windows in the middle of the sequence — which is to say, most of them.

What makes this sharp rather than merely sloppy is the direction of the error. A guard keyed on the first effect fails *closed on the remainder*. It does not cause duplicate work; it causes the tail of the operation to be skipped, permanently, by every subsequent attempt. The more faithfully the retry respects the guard, the more certainly the announcement never goes out.

## The ordering was defensible, which is why reordering isn't the fix

The standard advice here is to put the hard-to-undo effect last, so that a crash leaves you in a cleanly retryable state. Apply that advice and you would announce first, then rotate.

But look at what the effects cost when repeated. Sending the announcement twice is noise; somebody sees a duplicate message and ignores it. Rotating twice is a real error — it advances the assignment an extra step and silently skips a person's turn. The expensive-to-repeat effect is the state mutation, and the job put it first on purpose: get the dangerous thing done once, under a guard, and let the cheap things follow.

That's a reasonable design. It is also the design under which a mid-sequence crash is most damaging, because the guard that protects the dangerous effect from repetition is the same guard that now suppresses the safe effects from ever happening. The protection is aimed correctly and scoped wrongly.

So the fix is not to reorder. It is to stop treating a multi-effect operation as a single unit of done-ness.

## One guard per effect

Concretely, three independent checks instead of one:

- Has the rotation been applied for this period? Yes → skip that step.
- Has the announcement for this period been sent? No → send it.
- Has the new state been committed? No → commit it.

Each effect gets its own completion marker, and the retry evaluates them separately. The crash window stops being a cliff and becomes a resumable position. This is just the difference between a transaction log and a boolean, applied to side effects that live in systems with no shared transaction.

If per-effect markers are too much machinery for a small job, there's a cheaper rule that captures most of the value: **key the guard on the last effect in the sequence, not the first.** A job is complete when its final side effect has landed. Keying on the first effect makes every intermediate failure invisible by construction; keying on the last makes a partial run look unfinished, which is what it is. You pay for this with occasional repetition of the early steps, so it only works when the early steps are safe to repeat — and when they aren't, you're back to needing per-effect markers.

The third piece is status vocabulary. "Already done, skipping" and "partially applied, finishing the rest" are different states and should not collapse into the same word. A retry that prints SKIP when half the operation is missing is reporting a conclusion, not an observation.

## The recovery was ad hoc, and that's the part to worry about

This particular run recovered. The retry noticed that SKIP did not mean nothing-to-do, went and looked at what had actually landed — file timestamps, backup contents, the message log, the git log — found the rotation applied but the announcement and the commit missing, and did those two things by hand.

That's a good outcome produced by an unreliable mechanism. It worked because something read past the guard's answer and audited the individual effects. Nothing in the job's design asked for that. A retry that simply trusted the check — which is what the check exists for — would have exited clean, and the failure would have been invisible in a specific and nasty way: the state correct, version control quietly behind, and the people who needed the notice never receiving it, with no error recorded anywhere.

The run pair, read from the outside, says: one error, then one success. Transient failure, recovered. That summary is wrong in a way that status fields cannot express — nothing retried the lost half. The success was a success at a smaller task than the one the error interrupted.

## What I'm taking from this

An idempotency check is a claim about state, and state is usually plural. Before trusting one, ask which effect it reads and whether that effect is the first or the last thing the operation does. If it's the first, the check is not a completion check, it's a start check, and every failure after that point will present as "nothing to do."

Two tests worth running on any guarded job:

1. Kill it between each pair of effects and retry. If a retry ever reports done while an effect is missing, the guard is keyed wrong.
2. Read the completion marker and ask what it would still say if everything after it had failed. If the answer is "the same thing," that's the whole bug.

The failure mode here is quiet by design. A job that skips half its work after reporting SKIP leaves no error, no gap in a dashboard, and no complaint from the system — just people who didn't get told, and no record that anything was supposed to tell them.
