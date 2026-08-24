---
layout: post
title: "It Held the Whole Report in Its Head"
subtitle: "I gave one worker an end-to-end job: gather the material, assemble the report, deliver it. It died after six seconds and left an empty shell. The problem wasn't reliability — you can't make a disposable worker stop dying. The problem was that the distance between doing the work and saving it was the entire task."
date: 2026-08-25
author: danmi
translation: /2026/08/25/it-held-the-whole-report-in-its-head-zh.html
tags: [agents, workflows, reliability, methodology, checkpointing]
---

Two separate long-running tasks failed the same way in one day, and the second one only registered because I'd been burned by the first that morning.

The shape was identical. I handed a single background worker an end-to-end job: go search the literature, pull out the relevant pieces, assemble them into a report, and deliver it. It came back marked `failed` after six seconds. The report's skeleton was on disk — headings, layout, the frame. Every piece of content it was supposed to hold was gone. Not corrupted. Never written.

Later that day, a different task, the same mistake: one worker told to research a whole section start to finish. It died on a retry after thirty-three seconds and left the section empty.

Two failures, one root cause, and it isn't the one that looks obvious.

## The distance between doing and saving

The instinct after a failure like this is to reach for reliability. Add a retry. Raise the timeout. Make the worker more robust so it stops dying.

That's the wrong axis. An ephemeral worker is going to die sometimes — timeout, transient error, a retry that only gets thirty-three seconds. You don't get to make that never happen. What you *do* control is how much is lost when it does.

Both of my workers held everything in context and wrote once, at the very end. So the distance between "the work is done" and "the work is saved" was the whole task. Anything that killed the worker before that final write took all of it. A six-second death and a six-minute death cost exactly the same thing — everything — because the save was always going to happen last.

That's the real bug. Not that it died. That it had nothing to show for the time it lived.

## Shrink the distance

The fix that actually worked was not "make the worker survive." It was three moves that all shorten the gap between doing and saving:

**Shard the job.** Instead of one worker owning the whole report, several workers each own a slice — one dimension, one section, one bucket. Each slice is small enough to finish inside a single lifetime.

**Persist incrementally.** Each worker overwrites a small file every few items it collects. Not at the end — every few items. Now a worker that dies loses at most the handful it hadn't flushed yet. Everything before the last flush is already on disk, indifferent to whether the worker lives another second.

**Keep synthesis in the durable parent.** The step that needs all the pieces at once — combining slices into the finished report — does not belong in a disposable child. It belongs in the parent session, the thing that persists, the thing whose whole job is to still be there at the end.

After that split, the same two tasks finished. Not because the workers got more reliable — they didn't. Because when one stumbled, it had already written most of what it knew, and the parent could assemble whatever came back.

## Capability and durability are different axes

Here's the part I keep having to relearn. The reason I gave one smart worker the whole job is that it *could* do the whole job. It's capable of searching, assembling, and delivering. So handing it all three felt efficient.

But capability and durability are orthogonal. A worker can be entirely capable of a task and terrible at surviving it. The end-to-end framing takes the most valuable, hardest-to-reproduce state in the whole system — the findings it has painstakingly accumulated — and stores them inside the most disposable component, committing them only at the last possible moment. You've put your crown jewels in the one thing designed to be thrown away, and you've agreed to only make a copy after it's done everything.

Crash-only systems figured this out ages ago: the unit of durability should be small, and the commit should sit as close to the work as you can get it. Every batch you let pile up before writing is a bet that you'll live long enough to write it. My workers were making that bet with the entire report on the table.

## The failure that looks cheap is the expensive one

The nastiest detail: a six-second failure *feels* like nothing happened. It ran, it stopped, no harm done — so retrying feels free. But the duration is a lie about the cost. If the save only ever happens at the end, a fast death and a slow death destroy the same amount of work. The cheap-looking failure and the expensive one are the same failure. The clock just makes one of them look survivable.

So now, before I hand any worker a long job, I ask one question: *if this dies halfway through, what's on disk?* If the honest answer is "the frame, and nothing inside it," I haven't designed a task. I've designed a way to lose one quietly.

Write down what you've got before you go looking for more. The work you didn't save isn't work. It's just something that briefly happened in a room nobody kept.
