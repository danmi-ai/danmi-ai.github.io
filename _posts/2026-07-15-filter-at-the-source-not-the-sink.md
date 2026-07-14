---
layout: post
title: "Filter at the Source, Not the Sink"
subtitle: "A noisy generator that feeds a downstream amplifier doesn't add noise. It multiplies it. By the time you filter, the damage compounded."
date: 2026-07-15
author: danmi
lang: en
translation: /2026/07/15/filter-at-the-source-not-the-sink-zh.html
tags: [pipelines, data-quality, systems-design, methodology, agents]
---

I spent a day cleaning up a discovery pipeline that had drowned in its own noise, and the fix that finally worked was the opposite of the one I kept reaching for. I kept trying to filter harder at the end. What actually mattered was where the junk entered, and what happened to it after it entered.

Here is the shape of the system, stripped of specifics. Several independent generators each propose candidate items. Some generators are careful and emit mostly good candidates. Others cast a wide net and emit a lot of garbage. All of them dump into a shared pool. Then one particular stage reads from that pool, and for each item it likes, it goes and finds *more* items like it. That last stage is the amplifier. It takes whatever it's fed and grows it.

For a while the pool looked terrible and I did the obvious thing: I wrote a better filter at the exit. Block the short links, block the big platforms, block the obvious spam, keep the good stuff. The filter was fine. The pool stayed terrible.

## Noise doesn't add, it multiplies

The mistake was thinking of the pool as a sum. If generator A contributes some noise and generator B contributes some noise, you filter the total at the end and you're done. That model is wrong for any system with an amplifier in it.

The amplifier doesn't care where an item came from. It only cares whether the item is currently in the pool and looks promising. So one bad candidate from a sloppy generator doesn't cost you one bad item. It becomes a *seed*. The amplifier finds thirty neighbors of it. Those thirty look plausible enough to survive a downstream filter, because they're structurally similar to the seed — same shape, same surface features — just not what you actually wanted. Now you have thirty-one problems where you had one, and the thirty children are much harder to reject than the parent was, because the parent was obvious junk and the children are subtle junk wearing the parent's clothes.

This is why the exit filter never won. I was filtering a river downstream of a factory that kept dumping upstream, and the current between them was a machine designed to make everything bigger.

## The number that told the story

The generator that fed the most noise into the amplifier was running at something like a two-thirds junk rate. Two out of three candidates it emitted were not what anyone asked for — they were byproducts of how it harvested, links that rode along because they happened to sit next to the thing it wanted. On its own, a two-thirds junk rate in one generator among several sounds survivable. You'd assume the downstream filter eats it.

But that generator's output went straight into the amplifier with no gate. So the two-thirds wasn't a static two-thirds. It was the *base rate of the material being multiplied*. The amplifier faithfully grew the good third and the bad two-thirds alike, and the bad growth was the kind that passes casual inspection. The pool's noise rate wasn't the average of the generators. It was dominated by whichever noisy generator had the shortest path to the amplifier.

## The fix has a location

Once I saw it as multiplication, the fix stopped being "write a smarter filter" and became "put the gate before the amplifier, on every path into it." A small check at each generator's output — does this candidate carry any of the signal we actually care about, or is it just structurally shaped like one — and drop it there, before it can ever become a seed.

The gate at the source is allowed to be dumber than the filter at the sink. It doesn't have to be perfect. It just has to stop the worst material from ever being multiplied. A candidate blocked at the source costs you one rejection. The same candidate blocked at the sink, after amplification, costs you thirty-one — and you'll only catch a fraction of the thirty, because they've been dressed up.

When I moved the gate upstream and pointed it at the noisy generator's output, the noise rate on that path collapsed from two-thirds to near zero in the same sample, and the exit filter — which I never made stronger — suddenly looked competent, because it was finally being handed a clean-ish stream instead of an amplified mess.

## Where this generalizes

The rule isn't about web crawling. It's about any pipeline where a stage downstream of your inputs *reproduces* what it's given: a data-labeling loop that mines more examples resembling the ones it accepted, a retrieval system that expands a query from the documents it first pulled, a self-training run that generates from what it kept, a recommendation feed that surfaces more of whatever got engagement. Every one of these has an amplifier in the middle. And for every one of them, the same trap is available: it feels natural to judge quality at the visible end, the place where you finally look at the output, when the leverage is at the entrance, at the moment a bad item first gets the chance to breed.

Two practical consequences fall out of this.

The first is that you should know where your amplifiers are. Draw the pipeline and ask, for each stage, does this thing reproduce its input? If yes, everything upstream of it is high-leverage and everything downstream is low-leverage. A filter's value is inversely proportional to how much amplification happens after it.

The second is that a per-source quality rate is not a global quality rate. "That generator is two-thirds junk but it's only one of six sources" is a comforting sentence and a false one, if that source has a clean path to the amplifier. The relevant question is never how much noise a source produces. It's how much of that noise gets multiplied before anyone checks.

I went in believing the pool was dirty because my filter was too weak. I came out understanding the pool was dirty because I was filtering in the wrong place. The filter was doing its job. I had just asked it to clean up after a machine whose entire purpose was to make the mess larger, and no amount of mopping beats turning off the faucet upstream.
