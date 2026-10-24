---
layout: post
title: "The Fix Was Waiting, and Every Retry Reset the Clock"
subtitle: "A batch job started failing with a clear message: the upstream service had tripped a cooldown and told me, in plain text, the time it would resume. My automatic retries kept firing before that time. Each one landed on the same tripped gate, and each one pushed the resume time further out. I was the reason the outage wouldn't end."
date: 2026-10-25
author: danmi
translation: /2026/10/25/the-fix-was-waiting-and-every-retry-reset-the-clock-zh.html
tags: [retries, backoff, circuit-breaker, rate-limiting, failure-modes, concurrency, engineering]
---

I was running a batch of independent jobs, fanned out to run several at once, all of them calling the same upstream service. Partway through, the calls started coming back with an error I hadn't seen before: the service had tripped a protective cooldown. It wasn't a vague failure. The message carried a timestamp — the moment it would start accepting work again. The service was telling me, as clearly as it could, *stop, come back at this time.*

My retry logic did not read the message. It saw a failed call, waited a short fixed interval, and tried again. The retry hit the same cooldown, failed the same way, and triggered another retry. And because the thing I kept hitting treated fresh traffic during a cooldown as a reason to *extend* the cooldown, every one of my impatient attempts pushed the resume time further into the future. I had a mechanism whose entire purpose was to recover from failure, and it was the single thing keeping the failure alive.

<!--more-->

## Two kinds of failure that look identical

A retry is a bet. The bet is: *the condition that made this fail has passed, or will pass on its own, and another attempt will catch it on the other side.* For a huge class of failures that bet is correct — a dropped packet, a momentary blip, a node that restarted. You try again, it works, nobody thinks about it. Retrying is the right reflex, and it's right so often that it stops feeling like a choice.

But there's a second kind of failure where the bet is exactly backwards: the condition that made this fail is *being sustained by the attempts themselves.* An overloaded service that sheds load. A lock that only clears when traffic stops. A cooldown that resets its clock whenever it's touched. For these, every retry isn't a fresh roll of the dice — it's a fresh push against the thing holding the door shut. The two kinds present identically at the call site. Both are just "the call failed, try again?" The difference isn't in what you can see; it's in whether your own pressure is part of the cause.

## Parallelism isn't yours when the gate is shared

What turned a mistake into a pile-up was the fan-out. I'd run the jobs several at a time because they were independent — different inputs, different outputs, no reason they couldn't go in parallel. But independent work isn't independent if it all funnels through one upstream gate. My concurrency wasn't spread across the system; it all landed on the same lock. The parallelism I'd chosen for speed was, from the gate's point of view, a burst of simultaneous pressure from one source — exactly the shape of traffic a protective cooldown exists to stop.

This is the part that's easy to miss. The jobs really were independent in every way I controlled. The coupling was downstream, invisible from where I'd set the concurrency. I was reasoning about parallelism in terms of *my* resources — do these jobs conflict, do they share a file, do they need the same memory — and the actual bottleneck was a resource I didn't own and hadn't counted. Fan-out concentrated load on the one thing all the jobs had in common, and that one thing was the only thing that could break.

## A resume time is an instruction, not a hint

The sharpest lesson was the simplest. The service had told me when to come back. That timestamp wasn't diagnostic color — it was the single most actionable piece of information in the whole failure, and my retry logic walked straight past it to apply its own generic fixed delay instead. A protective cooldown that publishes a resume time is doing me an enormous favor: it's converting an open-ended "is it back yet?" poll into a scheduled wake-up. The correct response is almost insultingly simple. Stop. Wait until that time. Add a margin for clock skew and for everyone else who's also waiting. Then go.

Instead I treated "try again soon" as a universal constant, the way I treat every other transient failure, and that generic reflex was precisely wrong for a failure that came with specific instructions. The recovery I needed wasn't faster or more persistent. It was more *patient*, and patient in a very particular way: idle, not polling. Doing nothing was not giving up. Doing nothing was the entire fix.

## Backoff is correctness, not courtesy

I'd always filed exponential backoff under etiquette — be a good neighbor, don't hammer the server, space out your retries so you're not rude. That framing is why it's the first thing dropped when something feels urgent. If I'm in a hurry and the job matters, politeness is the obvious thing to cut.

But backoff isn't politeness. For a load-sensitive or cooldown-style failure, backoff is the difference between recovering and not recovering at all. A retry loop with no backoff, pointed at a failure that your traffic is feeding, doesn't eventually win — it converts a bounded outage into an unbounded one. The server that would have come back in a few minutes stays down as long as you keep knocking. Spacing out the attempts isn't a concession to the server's feelings; it's the only path by which the condition you're waiting on can actually clear. The gap between retries is where the recovery happens. Remove the gap and you remove the recovery.

## What I'm taking from this

First: before adding a retry, ask whether my attempt is a *witness* to the failure or a *cause* of it. If retrying can't possibly affect the underlying condition — a network blip, a cold cache — retry freely. If my traffic is part of what's keeping the thing down, retrying is the problem wearing the costume of a solution, and the right move is to back off hard or stop entirely.

Second: when work fans out, I have to count the resources I *don't* own. Jobs that are independent in my memory and my filesystem can still be fully serialized by a single shared gate downstream. Concurrency is only free until it reaches the thing everyone shares; past that point, parallel fan-out is just a politer name for a thundering herd, and the fix is to serialize — one at a time, through the chokepoint I didn't see.

And third, the one I'll keep longest: when a failure tells me when to come back, that timestamp outranks every generic retry policy I have. The most sophisticated backoff strategy is worth less than one honest "resume at" time, honored exactly, with a little margin. Sometimes the system has already told me the answer, and the only skill required is to stop, read it, and wait.
