---
layout: post
title: "A Cheap Proxy Is Not a Valid Proxy"
subtitle: "Averaging two models approximates training on both — but only because the geometry lines up."
date: 2026-06-15
author: danmi
lang: en
translation: /zh/2026/06/15/a-cheap-proxy-is-not-a-valid-proxy/
tags: [model-merging, data-selection, proxies, methodology, machine-learning]
---

Here is a fact that should not be true. Take two models fine-tuned from the same base on two different datasets. Average their weights, parameter by parameter. The thing you get behaves a lot like a model trained on both datasets at once.

Stop and feel how strange that is. Joint training is a long, nonlinear, path-dependent optimization. Weight averaging is arithmetic you could do on a napkin. One of these is supposed to be a cheap imitation of the other, and yet the imitation lands close enough that people now build real pipelines on it.

It works for a reason, and the reason is the whole point of this post.

## Why averaging stands in for training

Near a shared starting point, fine-tuning doesn't scatter weights in arbitrary directions. It moves them along directions that add up roughly linearly. The displacement a dataset induces — call it that dataset's task vector — composes with another dataset's displacement about the way you'd hope: you can add them, scale them, subtract them, and the merged weights still mostly mean what the arithmetic says they should.

So merging isn't a trick that happens to work. It's exploiting a structure that's genuinely there: in the right neighborhood, the loss landscape is flat enough and the fine-tuning moves are small enough that the model lives in something close to a linear regime. The merge approximates joint training because, locally, training is approximately additive.

That qualifier — *locally* — is doing enormous work, and it's the part everyone forgets.

## The move this enables

Picking a data mixture is expensive. If you want to know whether 30% code and 70% prose beats 50/50, the honest answer requires training a model on each mixture and comparing. Do that across a grid of ratios and domains and you've burned a small datacenter to answer a config question.

The merge gives you a shortcut. Train an expert per data source once. Then *merge* them in different proportions to simulate different mixtures — no gradient steps, just weight arithmetic. Search the whole mixture space cheaply, find the promising region, and only then spend the real joint-training run on the winner.

It's a lovely move. Expensive search problem, cheap composable surrogate, commit the budget only at the end. And it's the kind of move that feels so efficient you stop asking why it's allowed.

## Cheap is not the property that matters

Here's the thing I keep relearning: we adopt proxies because they're cheap, and then we trust them as if cheap were the same as faithful. It isn't. Cheapness is what makes a proxy *attractive*. Structural fidelity is what makes it *trustworthy*. These are different axes, and most bad decisions I've watched come from collapsing them into one.

The merge is a good proxy for joint training not because it skips the gradient steps, but because — in its valid region — it preserves the geometry of the thing it replaces. The shortcut and the real computation share a shape. Take that shared shape away and you still have a cheap operation; you just no longer have a proxy. You have a fast way to compute the wrong number.

And the failures arrive exactly where the geometry stops lining up. Push the fine-tuning too far from the shared init and the linear approximation rots; the task vectors stop composing and the merge starts lying. The proxy doesn't degrade gracefully or announce its own breakdown. It keeps returning confident numbers that used to mean something.

## Every proxy you rely on is the same bet

Once you see proxies this way, the pattern is everywhere, and it's always the same bet: *I claim this cheap thing shares structure with that expensive thing, inside some region I had better know the edges of.*

- A small-scale run as a proxy for a large-scale one. Valid until a capability shows up only past a parameter or data threshold, and then the small run isn't a smaller version of the answer — it's a different answer.
- An offline metric as a proxy for online behavior. Valid until the act of deploying changes the distribution the metric assumed.
- A benchmark as a proxy for capability. Valid until the model has effectively seen the benchmark, at which point the score measures memorization wearing the costume of skill.

Each is cheap. Each is fine inside its region. Each will betray you the instant you carry it past the boundary where the shapes still match — and none of them puts up a fence at that boundary for you.

## The discipline is mapping the edge

So the useful question about a proxy was never "how cheap is it?" Cheap is the bait. The question is "where does it stop sharing structure with the real thing?" Every proxy has a domain of validity — the region where the geometry lines up — and its entire trustworthiness lives inside that domain. The skill isn't collecting cheap proxies. It's knowing each one's edge and refusing to read its output as truth past that edge.

A proxy is a loan taken against the real computation. Inside the region where the two share a shape, it pays back honestly and you got your answer for almost nothing. Step outside that region and you haven't measured the thing you cared about. You've measured how far the proxy has drifted from it — and then called the drift by the name of the thing.

Find the edge first. The cheapness will still be there when you get back.
