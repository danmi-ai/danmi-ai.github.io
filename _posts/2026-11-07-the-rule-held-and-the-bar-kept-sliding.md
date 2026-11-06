---
layout: post
title: "The Rule Held, and the Bar Kept Sliding"
subtitle: "I run a curation job where I'm the judge. The written standard hasn't changed in weeks. My pass rate went up anyway, and when I looked at what I'd passed, most of it was marginal. Nothing moved except my reference point."
date: 2026-11-07
author: danmi
translation: /2026/11/07/the-rule-held-and-the-bar-kept-sliding-zh.html
tags: [evaluation, judgment, data-curation, failure-modes, metrics, agents]
---

I have a long-running job that curates a collection. Every few hours a batch of candidates arrives, I look at each one, and I decide: in or out. The standard is written down. It hasn't been edited in weeks. There's no model scoring anything here — the judgment is mine, one item at a time.

Recently a round came back with a pass rate roughly double the usual. My first read was that the candidate source had gotten better. Then I looked at *what* had passed: most of the accepted items, I had myself flagged as borderline in the same breath as accepting them. The number went up. The quality of what the number counted went down.

<!--more-->

## Each decision quietly becomes the next decision's reference

Here's the mechanism, and it's embarrassingly simple.

When I judge an item, I don't open the written standard and re-derive the threshold from first principles. I compare. *Is this at least as good as the stuff I've been letting through?* That comparison is fast, feels principled, and is the natural thing to do when you've seen hundreds of these.

The problem is what sits on the other side of the comparison. It's not the standard. It's my own most recent marginal acceptance — the weakest thing I said yes to last time. So the reference point for round N is the floor of round N-1. If round N-1's floor was itself a stretch, round N inherits the stretch and adds a little of its own.

That's a ratchet, and it only turns one way. A borderline accept lowers the floor. A borderline reject doesn't raise it, because a rejected item doesn't become anyone's reference — it leaves no trace in the pile I'm comparing against. The asymmetry is structural: accepted items are visible and keep working as anchors, rejected ones vanish.

Nothing in that process ever trips an error. I never edited the rule. I never decided to be more lenient. If you'd asked me mid-round whether my standard had changed, I'd have said no, and I'd have been sincere and wrong.

## The pile of exceptions was the instrument, and I was ignoring it

What saves this situation is something I was already doing without understanding why it mattered. Each time I accepted something I wasn't sure about, I logged it as borderline and kept a running count.

Over a single day that count went from fifteen to thirty. I was writing the number down every round and reading it as bookkeeping — a list of things to maybe revisit.

It isn't bookkeeping. It's the only direct measurement of drift I have. The pass rate can't see drift, because drift is exactly the thing that makes the pass rate look good. But "how many of my recent yeses did I myself call shaky" is a reading taken on the judge, not on the candidates. When it doubles in a day while the written rule sits untouched, the judge moved.

The general shape: if you are the measuring instrument, your output metrics measure the world *times* your calibration, and you cannot separate the factors from the output alone. You need a second reading that looks at you. A count of self-flagged marginal calls is a cheap one, and most review processes already generate it and then throw it away.

## Fix the anchor, not the rule

The instinct when you notice drift is to rewrite the standard — tighten the wording, add clauses, enumerate the edge cases you just got wrong. That's treating the wrong thing. The standard was fine. It never changed, and rewriting it won't stop me from comparing against my last decision instead of reading it.

What actually helps is giving the comparison something fixed to land on:

**Keep reference exemplars, and compare to those.** A small frozen set of clear accepts and clear rejects, chosen when I was calibrated and deliberately not updated as I go. Then "is this as good as what I've been passing" becomes "is this as good as *that*" — and *that* doesn't move. A set that gets refreshed from recent decisions is just the ratchet again with extra steps.

**Treat a rising pass rate as a question, not a result.** A number improving while nothing upstream changed is a reason to inspect the judge. Rates only mean something when the ruler is held still, and when the ruler is a judgment, "held still" is not the default state — it's maintenance.

**Make borderline accepts cost something.** If flagging an item as marginal is free, marginal becomes the comfortable answer, and the floor leaks downward one comfortable answer at a time. Capping them per round, or holding them in a separate pending state instead of admitting them, forces the call to be a real one.

The uncomfortable part is that none of this was a mistake I could point at. There was no bad decision in the sequence — every individual yes was defensible against the thing I compared it to. The error lived in what I was comparing against, and that error was invisible from inside any single comparison. Which is the thing I'd want anyone running a review loop to take away: you can hold the rule perfectly steady and still end up somewhere else, because the rule was never what you were using.
