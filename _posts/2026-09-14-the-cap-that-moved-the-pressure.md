---
layout: post
title: "The Cap That Moved the Pressure"
subtitle: "I put a limit on the one input channel I could see growing. The limit worked exactly as designed — that channel shrank. Total usage went up anyway, on every single run. The pressure hadn't gone away; it had walked through a door I wasn't watching."
date: 2026-09-14
author: danmi
translation: /2026/09/14/the-cap-that-moved-the-pressure-zh.html
tags: [methodology, agents, systems, evaluation, debugging]
---

An agent was running out of working memory. I had traced it: a big fraction of what it loaded into context was one kind of input — large text reads. The obvious fix wrote itself. Cap the size of any single read; force the agent to page through big documents in chunks instead of swallowing them whole.

I ran it as a clean paired experiment. Three cases, each with a control and a treatment that differed only by the cap. Then I read the numbers, and they were not what I ordered.

The cap did exactly what it promised. In the treatment runs, the giant single reads were gone — text intake dropped to a fraction of the control. Within its own scope, the intervention was flawless.

And on all three cases, peak memory went **up**. Not flat, not noisy — up by a wide margin every time.

## Where the pressure went

The story the traces told was almost mechanical, once I stopped staring at the channel I'd capped and looked at the one next to it.

Cap a single read, and the agent doesn't read less. It reads the same document in more pieces. More pieces means more steps. More steps means the whole loop runs longer — the turn count roughly tripled. And a longer loop does more of everything it was already doing between reads, including the expensive part I hadn't been watching at all: pulling images back into context to check its own work. Those images were never capped. They were the real weight the whole time. By stretching the run, the cap on one door pressed harder on the other, and the other door was the heavy one.

There was a second case that made this undeniable. One run had no images at all. It still got worse — its peak rose purely because the loop lengthened. So there were actually two ways the load moved, not one: through the images, and through the sheer extra length of a paginated run. Capping the visible channel fed both.

## Two failure modes, both of them mine

The first was aiming at the wrong channel. "A big fraction is text reads" was true and useless — the kind of coarse attribution that points at the biggest slice of a pie without asking whether shrinking that slice shrinks the pie. It doesn't, if the thing you squeeze just relocates. I had measured *where the bytes were*, not *where they'd go if I pushed here*.

The second was subtler, and it's the one I want to keep. The intervention **succeeded within its declared scope and was net harmful anyway.** Text intake really did shrink. If I'd only measured the thing the cap was designed to control, I'd have shipped it and called it a win. The failure was only visible in a number the cap wasn't about — total peak — which is precisely the number that mattered and precisely the one a scope-local check ignores.

## The rule that survived

> A cap on one channel is not a reduction in load. It's a redirection. Before you claim a fix, measure the total, not the channel you touched — because the pressure you squeeze out of a visible channel tends to reappear in the one you weren't watching.

This is the same conservation you meet everywhere in systems work: push complexity out of one place and it surfaces in another, usually less visible, place. The version that fools you is the one where the local metric looks like a clean success. Text reads dropped. The dashboard for *that channel* would have been all green. The load hadn't vanished; it had changed address.

## What the failure was worth

The experiment failed to fix anything, and it was the most useful run in the batch — because a clean falsification is sharper than a vague suspicion. Before it, the target was "big reads, roughly." After it, the target was two named things: images pulled back into context, and the turn inflation that pagination causes. The first sits behind a door I now know to cap directly — store the artifact, look at a reference, don't haul the whole thing back in. The second is independent, proven so by the case with no images that got worse anyway; it needs a budget on the loop itself, not on any one channel.

The move that gets this wrong is the tempting one: cap the visible channel, watch that channel obey, ship. The channel obeys and the system gets worse, and you don't find out until something you weren't measuring falls over. The move that gets it right costs an extra step every time — measure the total, then ask which uncapped door the pressure just walked through. The narrow check is free and flattering. The whole-system check is the one that's actually true.
