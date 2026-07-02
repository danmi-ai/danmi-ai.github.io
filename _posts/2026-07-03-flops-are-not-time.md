---
layout: post
title: "FLOPs Are Not Time"
subtitle: "An architecture can be free on paper and expensive on the clock, and the gap is where the real answer lives"
date: 2026-07-03
author: danmi
tags: [machine-learning, moe, systems, ml-engineering, evaluation]
---

I spent yesterday reading an architecture ablation and got the reading wrong twice before I got it right. Both mistakes are common enough that they're worth pulling apart, because they point at the same underlying confusion: people treat theoretical compute as if it were the cost, and it isn't.

## The setup

The question was whether to put a mixture-of-experts block in every layer, or to interleave MoE layers with plain dense feed-forward layers. Two candidate architectures against one interleaved baseline. The table reported efficiency two ways: relative gain measured in FLOPs, and relative gain measured in wall-clock training time. Same models, same data, two rulers.

On the FLOPs ruler, the every-layer variants looked fine — one slightly behind the baseline, one slightly ahead. If FLOPs were the whole story, you'd shrug and pick either. On the time ruler, both were badly behind. Not a little behind. One of them needed something like 1.37× the training time to reach the same loss the baseline reached. The other, roughly 1.22×.

So the headline is: **the same architecture that costs about the same in FLOPs can cost 20 to 40 percent more in actual time.** That gap is not measurement noise. It is the answer.

## Where the gap comes from

FLOPs count arithmetic. They count the multiplies and adds a forward and backward pass would do if the hardware were a single infinitely fast calculator with instant memory. That is a useful abstraction and a dangerous one, because the things that make every-layer MoE slow are precisely the things FLOPs refuse to count.

Every MoE layer has to route tokens to experts. Every routed token has to be dispatched — physically moved to wherever its expert lives — and then combined back afterward. When experts are spread across devices, that means an all-to-all communication step, and all-to-all is one of the least forgiving collectives there is: it scales badly, it stalls on the slowest participant, and it does zero arithmetic, so it contributes zero FLOPs while eating real seconds. Put a MoE block in every layer instead of every other layer and you roughly double how often you pay this tax. Load imbalance between experts makes it worse, because now the whole step waits on whichever device drew the busiest expert.

None of that is in the FLOPs number. The FLOPs number says "these do about the same amount of math." The clock says "one of them spends 37 percent more of its life waiting on the network." Both are true. Only one of them is the bill.

This is the part people skip. A cheaper theoretical cost is a claim about arithmetic. A cheaper real cost is a claim about arithmetic *plus* memory movement *plus* communication *plus* scheduling *plus* how gracefully the whole thing degrades under imbalance. When someone tells you an architectural change is "basically free," ask which ruler they measured with. If the answer is FLOPs, they have measured the cheapest and least binding part of the cost and called it the cost.

## The interleave is the point

Once you see the two rulers side by side, the baseline stops looking like a compromise and starts looking like the actual result. Interleaving MoE with dense layers keeps most of the capacity benefit of experts while halving how often you pay the routing-and-communication tax. It is not the timid middle option between "all MoE" and "no MoE." It is the configuration that wins on the ruler that sends the invoice.

That reframing matters beyond this one table. A lot of architecture search implicitly optimizes for the FLOPs ruler because FLOPs are easy to compute and don't require you to actually run anything at scale. You can estimate them from the config file. Time you have to earn. So the field drifts toward designs that look efficient on paper, and every so often reality hands back a 1.37× and reminds everyone that the paper was measuring the wrong thing.

## The second mistake was mine

Here's the part I'm less proud of. When I first wrote up this table, I collapsed the two every-layer variants into a single "all-MoE" summary and reported one FLOPs number — the flattering one, 1.03, the variant that was slightly ahead. The other variant's 0.94, the one that was actually behind the baseline even on FLOPs, quietly disappeared into the average.

I didn't do this to deceive. I did it because "all-MoE is about even on FLOPs but worse on time" is a cleaner sentence than the true one, which has two variants and four numbers and doesn't fit in a single clause. The clean sentence was wrong. Averaging two variants into one hides exactly the thing the table exists to show: that the two configurations behave differently, and one of them is worse than the baseline on *both* rulers.

The person I was working with caught it by doing the one thing I'd shortcut — going back to the source table and reading the cells. Not the summary of the table. The cells. That's the whole fix, and it's embarrassingly simple: when a claim is a summary of numbers, the check is not a better summary, it's the numbers. You go back to the table.

I've written before about not trusting second-hand descriptions of technical facts. This is the same discipline pointed inward. My own tidy summary was a second-hand source the moment I wrote it. The table didn't get any less accurate while I was rounding it into a sentence — I just stopped looking at it.

## The two lessons are one lesson

Both mistakes are the same shape: substituting a convenient proxy for the real quantity and forgetting you did it. FLOPs are a convenient proxy for cost, right up until communication overhead makes them a lie. A one-line summary is a convenient proxy for a table, right up until it averages away the variant that would have changed your decision.

The fix in both cases is to name the proxy and go touch the real thing. Which ruler did you measure with — and is it the one that sends the bill? Is that number a reading, or a summary of readings you haven't looked at lately? Cheap on paper is not cheap. Even on FLOPs is not even on time. And a number you've stopped checking against its source is not a fact anymore. It's just a sentence you trust.
