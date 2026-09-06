---
layout: post
title: "The Cost Didn't Vanish, It Moved"
subtitle: "Two groups noticed the same weakness in the same kind of model and proposed the same repair: take something computed deep in the network and feed it back to somewhere shallow. One paid for it in training. One paid for it at inference. Reading them side by side, the interesting thing wasn't either fix. It was that the bill never actually got smaller — it just changed which pocket it came out of."
date: 2026-09-07
author: danmi
translation: /2026/09/07/the-cost-didnt-vanish-it-moved-zh.html
tags: [machine-learning, architecture, methodology, recurrence, tradeoffs]
---

Spend enough time reading papers that all orbit the same problem and you start to see a pattern that no single paper is willing to state, because stating it would undercut the paper. I ran into a clean example of it recently, reading two pieces of work from two unrelated groups that had, independently, diagnosed the same weakness in a familiar class of model and reached for what looks like the same repair.

The weakness, in plain terms: in a network built as a stack of layers processing a sequence, information computed *late* — deep in the stack, after the model has done real work to resolve an ambiguity — has no clean way to get back to the *early* layers. A deep layer figures something out, but the shallow layers that could have used that resolution never see it. They already ran. The insight arrives too late to help the part of the computation that needed it.

Both groups looked at this and had the same instinct: close the loop. Take a representation from deep in the network and route it back to somewhere shallower, so the model can, in effect, reconsider with the benefit of what it worked out. Feed the answer back to the question. It's an old, good idea — recurrence, feedback, second looks. And here is where the two papers quietly diverge in a way that turned out to be the whole lesson.

## Same fix, two invoices

The first group made the feedback a *trained* part of the model. They added the connection, added a small amount of new machinery to fuse the fed-back signal with the original input, and paid the price where you'd expect: in training. Their method needs a special training procedure — running the forward pass multiple times, stabilizing it, regularizing it so the loop doesn't collapse or explode. Once that's done, inference is cheap. The model runs at test time almost exactly as it did before; the loop is baked into the weights.

The second group refused to train anything. They took an off-the-shelf model, untouched, and added the same kind of deep-to-shallow feedback *at inference time only* — a fixed, parameter-free mixing of the deep representation back into a shallow position. No retraining, no new weights, nothing to learn. It works on a model you already have. But there's a catch, and it's a big one: the feedback makes the computation serial. The trick of processing a whole sequence in parallel — the thing that makes these models fast to run — breaks, because now an early position has to wait for a late computation before it can be finalized. They bought a free lunch on the training side and paid for it, in full, at inference.

Put the two side by side and the shape is unmistakable. Same diagnosis. Same architectural move. Opposite invoices. One pays in training complexity and keeps inference clean; the other keeps training untouched and pays in inference serialization. **Neither made the cost go away. They chose which pocket to pay from.**

## Why "free" always has a footnote

This is the part worth carrying out of the specific example, because it generalizes far past this one class of model. When someone shows you a capability added for "free" — no training, no new parameters, drop it into what you already have — the correct reflex is not gratitude. It's to ask *where the bill went*. It didn't disappear. Conservation of difficulty is close to a law: if a real weakness is genuinely being repaired, the repair costs something, and if the headline says it costs nothing on axis A, your next move is to check axes B, C, and D.

In this case the footnote was enormous and easy to miss if you only read the abstract: *training-free* sounds like pure upside until you notice it silently traded away parallelism, which for real deployment is often the entire ballgame. A method that doubles or worse your per-token latency is not "free" in any sense a person running a service would recognize. It's free the way a payday loan is free — the cost is real, it's just deferred to a moment you weren't looking at when you said yes.

The mirror image is just as true. The trained version's "expensive training, cheap inference" is the better deal *if and only if* you're going to run the model enough that amortizing the training cost over many cheap inferences comes out ahead — which, for anything deployed at scale, it usually does. Neither invoice is wrong. They're priced for different customers. The mistake is reading either headline as the whole price.

## The citation that gave the game away

There was a smaller thing in the reading that I keep thinking about, because it's a trick for seeing structure that papers work hard not to show you. The training-free paper, listing related work, pointed at a *third* piece of work as its nearest neighbor and described it in a single dismissive clause — something like "that approach requires retraining and a learned fusion module." I read that clause and realized it was, almost word for word, a description of the *first* paper I'd just read. The training-free authors had characterized their closest relative without knowing (or at least without saying) that a concrete instance of exactly that relative existed and had been published. And the two papers I was holding didn't cite each other at all.

That's the tell. When you want to know the real map of a research area — who is actually doing the same thing as whom — the abstracts won't tell you, because every paper is incentivized to look novel. The related-work section is more honest, but the *most* honest signal is the throwaway clause where one paper dismisses a neighbor. That dismissal is a fingerprint. If paper B dismisses "approaches that need retraining and a learned fusion," and paper A *is* an approach that needs retraining and a learned fusion, then A and B are siblings who haven't been introduced — regardless of what either title claims. Reading the dismissals against each other reconstructs a family tree the authors never drew, sometimes because they never noticed it themselves.

## The rule I took from it

Two, actually.

First, when a fix is advertised as free on some axis, find the axis it isn't free on before you adopt it. Difficulty is conserved; the interesting question is never *whether* it costs something but *where*, and whether that where is a pocket you can afford. "Training-free" and "cheap at inference" are not the same virtue, and a method can loudly have one while quietly lacking the other.

Second, to place a piece of work in its real family, read the sentence where it dismisses a neighbor, and check whether some other paper *is* that neighbor. The convergences that matter most are the ones nobody in the conversation has acknowledged yet — two groups solving the same problem with the same move, each thinking the other is a hypothetical they can wave off in a subordinate clause. Find those, and you understand the field better than any single paper in it does.
