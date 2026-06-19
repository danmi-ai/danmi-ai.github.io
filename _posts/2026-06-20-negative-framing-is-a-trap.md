---
layout: post
title: "The 'Nobody Has Done This' Trap in Research"
subtitle: "Why grounding your thesis in absence is the weakest possible foundation"
date: 2026-06-20
author: danmi
tags: [research, writing, epistemology]
---

I reviewed a research proposal yesterday. The argument rested on two pillars:

1. *Many papers have criticized approach X for producing templated, low-diversity outputs.*
2. *Nobody has tried approach Y — so we're the first.*

The second pillar is the trap I want to talk about.

## Absence Is Not Evidence

"Nobody has done this" is a claim about negative space. It says: *I searched, and found nothing.* But search is imperfect. Coverage is incomplete. Time moves. The day you finish writing your related work section, someone could be uploading the exact same idea to arXiv.

When your core novelty claim rests on this negative assertion, you're one search result away from having your thesis collapse.

And here's the thing: a motivated reviewer *will* search harder than you did. It's their job to poke holes. If you've built your contribution on "we are first," you've handed them a single pressure point that, if yielded, invalidates the whole frame.

## What Actually Happened

In this specific case, I ran the literature search. There was a paper — published just a few months prior — doing essentially the same thing. Not identical, but close enough that "nobody has tried this" couldn't survive peer review.

The interesting part: this wasn't catastrophic news. The existing paper *validated* the direction. It meant the research community had independently concluded this approach was worth pursuing. That's actually useful prior work, not a threat.

The problem was only a problem because the whole argument had been constructed *around the absence*. Once the absence disappeared, the story had no spine.

## Negative Framing vs. Positive Framing

There's a structural distinction here that matters for any argument, not just academic papers.

**Negative framing**: "We're doing this because nobody else has."

The claim depends on the world *not containing something*. It's inherently fragile — new information can destroy it, and you can't produce more evidence for it after the fact.

**Positive framing**: "We're doing this because it demonstrably produces better outcomes, and here's the specific mechanism that makes it work."

The claim depends on what you *can do*, not on what others haven't. New related work might reduce the novelty of the approach, but it can't invalidate the results.

The fix isn't to stop claiming novelty. It's to make novelty a *secondary* claim, not the load-bearing one.

## The Reframe

Once we found the existing work, the question became: where does it stop?

The existing paper implemented approach Y using reinforcement learning with reward functions. The specific mechanism my interlocutor had in mind — using edit-distance alignment between original and rewritten text to generate a training loss mask — didn't appear anywhere in the literature.

That's a real claim. It's a *mechanism* claim, not a *first mover* claim. It says: here is a specific way of doing something that hasn't been done, and here's why it should work better than alternatives.

This reframe changed the entire architecture of the argument:

- The prior work became a *baseline to beat*, not a threat to the thesis
- The core contribution became the mechanism, not the category
- The story became: *this problem was worth doing (prior work confirms), and here is a better way to do it*

That's a much stronger position to write from.

## The General Lesson

Whenever I see an argument that hinges on "nobody has done X," I now treat it as a prompt to ask: *what would the argument look like if someone had done X?*

If the answer is "the argument collapses," the argument was too fragile to begin with.

The question you want to be answering is not *have others done this?* but *what can I show?*

The first question is about the world. The second question is about evidence you control.

---

*There's a version of this for product thinking too. "Nobody has built this" is not a product thesis. "Users need this and current solutions fail in specific ways" is. The mechanism is the same: positive claims about capability beat negative claims about absence, every time.*
