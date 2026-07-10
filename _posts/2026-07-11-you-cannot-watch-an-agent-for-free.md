---
layout: post
title: "You Cannot Watch an Agent for Free"
subtitle: "The more completely you can see what an autonomous process is doing, the more you've had to become part of it"
date: 2026-07-11
author: danmi
tags: [agents, observability, instrumentation, systems, epistemics]
---

Spend a while trying to build a live view into a coding agent — something that shows you, in real time, what tools it's calling, what it's thinking, how much context it has left — and you run into a problem that has nothing to do with UI. It's an epistemics problem wearing an engineering costume. To see what the thing is doing, you have to be positioned somewhere relative to it, and where you stand determines both how much you can see and how much you've disturbed. There is no vantage point that gives you everything and touches nothing.

I ended up sorting the approaches into four, and they line up on a single axis.

## The four ways to watch

**Read the traces.** The agent writes files as it runs — session logs, transcripts, a JSONL of what happened. You poll those from the outside. You are a pure observer; you change nothing. But you only see what the agent chose to write down, after it wrote it, and you find out about a turn when the turn is already over. It's archaeology on a live dig. The dead-giveaway signature of this approach is that some fields are just missing — token counts, the model name, how much context is left — because the agent never had a reason to persist them to disk.

**Install a hook.** Most agent runtimes have callback points: before a tool runs, after a permission is requested, when a turn ends. You register there. Now you get events as they happen instead of after, and you get them structured. The cost is that you're now *inside* the agent's execution — your callback runs in its loop, and if your handler is slow or throws, you're no longer just watching. You've become a thing that can break the run. The hooks also only fire where the runtime decided to put them, so your view is complete exactly up to the boundary someone else drew.

**Take over the I/O.** Launch the agent as a child process and own its stdin and stdout. Speak its streaming protocol directly. Now the completeness jumps: because you're reading the official event stream the agent emits for exactly this purpose, the fields that were missing from the disk traces — model, token usage, context percentage — are suddenly reliable, because the agent is *telling* you, not leaving footprints you have to interpret. But look at what you had to do to get there. You are no longer observing the agent. You are the process that starts it, feeds it, and reads it. It runs at your pleasure. The observer has become the operator.

**Become it.** The last option isn't watching at all. You don't instrument someone else's agent; you build the agent, so the loop is yours and every intermediate state is a local variable. Total visibility, zero interpretation. And, of course, zero separation — there's no "the agent" and "the watcher" anymore. You threw out the thing you were trying to observe and replaced it with yourself.

## The axis nobody puts on the label

Read traces → install a hook → take over I/O → become it. Two things rise together along that line, and they rise together for the same reason. Intrusion goes up: you move from touching nothing, to running code inside the loop, to controlling the process, to being the process. And completeness goes up: from "whatever got written to disk" to "every internal state." They climb together because they're the same movement seen from two sides. The only way to close the gap between what the system reports and what it actually did is to get closer to where the doing happens — and every step closer is a step from observer toward participant.

This is not specific to coding agents. It's the shape of instrumenting any autonomous process you don't fully own. Profiling a program: sampling from outside is cheap and lossy, instrumenting the binary is precise and changes the timing you were trying to measure. Studying an organization: reading the memos is safe and shallow, sitting in the meetings makes you part of the meeting. Watching a market: the tape is public and lagged, being the market maker gets you every order and makes you a participant whose presence moves the price. Even physics has the polite version of this — you can't measure the small thing without the measurement being an interaction.

## Why it matters that you name the axis

The practical mistake is picking a paradigm for a reason that isn't the real cost. You reach for hooks because they're "easy to add," and you don't notice you've signed up to run code inside a loop you don't control until a slow handler stalls the agent. You reach for reading traces because it's "non-invasive," and you ship a dashboard that quietly reports the wrong context percentage because that number was never on disk and you were interpolating. Each rung has a failure mode that is invisible from the rung below it, and the failure mode is always the intrusion you didn't admit you were taking on, or the completeness you assumed you had and didn't.

So the honest way to choose is to say the trade out loud. If you must not perturb the thing — it's production, it's someone else's, a stall is unacceptable — you stay low on the axis and you *accept a lossy, lagging view* as the price, and you don't let anyone read a confident number off a field you were guessing at. If you need the complete picture — every token, the real context budget, the exact stop reason — you accept that you've climbed toward operator, and you own the failure modes that come with running inside the loop. What you don't get to do is want the completeness of taking over the I/O and the innocence of reading a log file. That vantage point isn't on the axis. Nothing is.

Watching a system and steering it are not separate acts you can dial independently. They're the same axis, and every honest observer eventually finds out where on it they've been standing the whole time.
