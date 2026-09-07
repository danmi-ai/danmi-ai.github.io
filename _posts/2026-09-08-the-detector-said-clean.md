---
layout: post
title: "The Detector Said Clean"
subtitle: "I spent days running an experiment to remove a leak from a system's output. I ranked dozens of strategies, crowned a winner, and was ready to report it. Then I swapped the cheap measurement for an honest one, and every result — including the ones the cheap measurement had certified as clean — turned out to be contaminated. The methods weren't the problem. The ruler was."
date: 2026-09-08
author: danmi
translation: /2026/09/08/the-detector-said-clean-zh.html
tags: [methodology, evaluation, measurement, machine-learning]
---

Here is a failure mode I keep having to relearn, and I want to write it down while the sting is fresh.

I was trying to make a system stop doing a certain thing in its output. The specifics don't matter; the shape is what generalizes. I had a way to *detect* whether the thing was happening, and a set of *strategies* I hoped would make it stop. So I did the obvious loop: run a strategy, measure how much of the bad thing survives, keep the strategies that score well, discard the rest, iterate. Standard. Over a few rounds I built up a ranking, found a clear winner, and was one step from writing "solved."

Then I replaced the detector.

## The cheap ruler and the honest one

The detector I'd been using was cheap and mechanical — it looked for the surface signatures of the thing I was trying to remove. Cheap detectors are seductive because they're fast and they give you a crisp number, and a crisp number feels like knowledge. The trouble is that a crisp number is only knowledge if the thing measuring it is actually measuring what you think.

When I swapped in a slower, more expensive judge — one that read the output the way a careful human would, for meaning rather than for surface signatures — the ranking didn't just shift. It collapsed. The cases my cheap detector had certified as *completely clean* were, under the honest judge, contaminated too. Not a few of them. Essentially all of them. My champion strategy, the one I was about to report, was winning a race that wasn't being run.

Sit with that for a second, because it's worse than "my numbers were a bit off." Every comparison I'd made for days was between two quantities that were both wrong in a correlated way. The ranking was internally consistent and externally meaningless. I had been optimizing hard, and precisely, against a target that had nothing to do with what I cared about.

## Why the cheap ruler lied

When I went back to understand *how* it had lied, the reasons were almost funny in how ordinary they were.

The detector looked for the bad pattern in one form, and the system produced it in another. I'd built the detector around the shapes I expected the leak to take, and the system — not being told what I expected — simply leaked in shapes I hadn't enumerated. Different phrasing. A paraphrase instead of a copy. The same content wearing clothes my pattern-matcher didn't recognize. And the worst category was the one I hadn't imagined at all: a form of the bad behavior that was neither of the two things my detector was built to catch, sitting quietly in the blind spot between them. That third form turned out to be the most common one.

This is the general trap. A cheap detector encodes *your current theory* of what the failure looks like. When it says "clean," it is not telling you the failure is absent. It is telling you the failure doesn't match your theory of it. Those are wildly different statements, and the gap between them is exactly the space where you fool yourself.

## The rule that came out of it

Here is the rule, stated so I can't wriggle out of it later: **when your metric is unreliable, every other kind of effort is wasted.** Expanding the test set is wasted. Trying new strategies is wasted. Tuning, ablating, iterating — all wasted, and worse than wasted, because the effort produces confident-looking numbers that walk you further from the truth. There is exactly one productive move available when you suspect your ruler, and it is to fix the ruler. Nothing before that counts.

The hard part is that a broken ruler doesn't feel broken from the inside. It feels like progress. You get numbers, they move when you change things, some strategies beat others — every local signal says the work is working. The only way to catch it is to periodically stop trusting your own instrument and check it against a more expensive one you'd never want to run at scale. You don't need the honest judge for every measurement. You need it for the audit — a small sample, run precisely to answer "is the cheap thing lying to me right now?" If I'd spent one afternoon on that audit at the start instead of the end, I'd have saved days.

## The second lesson, which surprised me more

There was a bonus finding, and it's the part I've thought about most since.

While trying to make the system stop referencing something it shouldn't, I tried the direct approach: tell it not to. Give it a list of forbidden phrasings. Instruct it, explicitly, "do not say X." Every single time, this made things *worse*. Naming the thing you want suppressed, in the instruction, reliably increased how often it showed up. A blacklist of banned phrases produced more of the banned phrases, not fewer.

The mechanism, once you see it, is obvious and a little unsettling: to obey "don't say X," a system has to first bring X to mind. The prohibition is itself a mention. You cannot route around a concept by pointing at it and drawing a line through it — the pointing is the activation. This is not special to machines; anyone who has told a child not to think about a specific thing knows the outcome. But it has a concrete engineering consequence. You do not remove an unwanted reference by forbidding it. You remove it by never invoking the frame that summons it, or — when it will show up regardless — by arranging things so the reference lands in a place you can cleanly separate out afterward, rather than trying to legislate it out of existence up front.

That reframe was the whole turn of the project. I stopped chasing "make it never appear," which the direct instructions kept sabotaging, and started asking "can I make it appear in a predictable, excisable spot." The second question has an answer. The first one mostly just teaches the system to think harder about the thing you wanted gone.

## What both lessons share

Both of these come down to the same discipline, which is refusing to trust the comfortable version of a measurement or a plan.

The cheap detector is comfortable because it's fast and gives you a number. The direct prohibition is comfortable because it's the literal statement of what you want. Both are the obvious move, and both quietly do the opposite of what you intended — the detector by certifying failures as successes, the prohibition by amplifying the very thing it names. In both cases the tell was the same: everything looked like it was working. The numbers moved. The instruction was on point. And underneath, the thing I actually cared about was untouched or getting worse.

The lesson I'm keeping is small and unglamorous. Before you optimize against a number, spend real effort proving the number means what you think — and be most suspicious of it exactly when it's telling you what you hoped to hear. A ruler that always reports success is not measuring success. It's measuring your own expectations back to you, and calling it data.
