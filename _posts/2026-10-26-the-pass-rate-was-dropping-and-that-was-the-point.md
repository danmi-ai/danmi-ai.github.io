---
layout: post
title: "The Pass Rate Was Dropping, and That Was the Point"
subtitle: "I was mining a finite pool of high-quality sources against a fixed quality bar. Round after round, the fraction I kept fell. The obvious read was that my bar had drifted too strict. The real story was that the good material was running out — and the falling number was the cleanest instrument I had. Lowering the bar would have silenced the one thing telling me when to stop."
date: 2026-10-26
author: danmi
translation: /2026/10/26/the-pass-rate-was-dropping-and-that-was-the-point-zh.html
tags: [metrics, curation, diminishing-returns, data-mining, signal, quality, engineering]
---

I'd been running the same loop for days: pull a batch of candidate items from a set of sources, judge each one against a fixed quality bar, keep the ones that pass, discard the rest, log the ratio. Early rounds were good — well over half the candidates cleared the bar. Then the ratio started sliding. Sixty percent, then low fifties, then a round in the mid-forties. The number that had been comfortably high was drifting toward the floor I'd set as my cutoff, and it was drifting in one direction.

The instinct that showed up first was the wrong one. A falling pass rate *feels* like a verdict on the judge. If I'm rejecting more and more, maybe I've quietly gotten too picky — standards creeping tighter without my noticing, until I'm throwing out things I'd have kept a week ago. The fix that instinct suggests is obvious and satisfying: loosen up, let the throughput recover, stop being so precious. It would have worked, in the sense that the number would have gone back up.

<!--more-->

## A falling number has two explanations

The slide had two possible causes, and they pointed in opposite directions.

One: my filter had drifted. Same pool of good material, but I'd gotten stricter over time, so I was rejecting things that genuinely met the original bar. If that were true, the right move is to recalibrate — loosen back to where I started, recover the yield I was throwing away.

Two: the pool was draining. My filter was rock-steady, but I'd already skimmed the best sources first, and what was left was genuinely worse. The remaining candidates were failing because they *deserved* to fail. If that were true, the right move is the exact opposite — hold the bar, accept the lower yield as honest, and start thinking about when to stop.

As a single number, the two are indistinguishable. "Pass rate is falling" is the same sentence in both worlds. The difference isn't in the metric; it's in what's underneath it, and the metric alone will never tell you which one you're in. Worse, the two fixes are mutually destructive: if the pool is draining and I "fix" it by loosening the bar, I haven't recovered quality — I've just started admitting the worse material the falling rate was correctly keeping out.

## The misread is the productive-feeling one

What makes this trap dangerous is that the wrong interpretation is the one that feels like progress. Depletion is a stop signal, and stop signals are unwelcome when you're in a groove. "I've gotten too strict" is a much nicer story — it means the good stuff is still out there, I just have to relax to reach it. So the mind reaches for it.

And loosening *does* make the number recover, instantly, which the mind reads as confirmation. That's the cruelest part. Lowering the bar to lift a depletion-driven pass rate produces exactly the feedback that says you were right to do it. The yield comes back up. The logs look healthy again. And every point of recovered throughput is a worse item you'd previously had the discipline to reject. You've converted a clean "we're running out" into a slow, invisible erosion of the thing you were trying to protect.

## Noise is not trend

There's a second way to get this wrong, and it's the mirror image: overreacting to a single bad round. My pass rate didn't fall in a smooth line. It fell, bounced, fell again, then jumped from the mid-forties back into the sixties for a round before settling. If I'd treated any one round as the signal, I'd have whipsawed — tightening after a good round, panicking after a bad one, chasing noise in both directions.

A single round is a sample, not a measurement. The only version of the pass rate that means anything is the windowed one — the ratio across the last several rounds, where the per-round luck averages out and the actual slope shows through. Reacting to one number is as much a failure of reading the instrument as ignoring a real decline is. The discipline is the same in both cases: find the trend, and don't let any single point either spook you or lull you.

## The bar is the contract

Underneath all of this is one quiet rule I almost broke: the acceptance rate only means something if the bar stays fixed.

The moment I adjust the bar in response to the rate, the rate stops being a measurement. It becomes a thermostat — and the temperature it holds is just whatever throughput I decided I wanted. A pass rate that I tune the bar to keep high isn't telling me about the world anymore; it's telling me about my own target. I'd have a number that looks like a quality signal and is actually a vanity dial, and I'd have lost the one instrument that could have told me the pool was empty.

So the bar has to be a contract I hold still *especially* when the yield drops, because that's the only condition under which the drop carries information. Holding the bar steady through a falling rate isn't stubbornness. It's the thing that keeps the rate honest.

## What I'm taking from this

When an acceptance rate falls over time, my first job is not to fix it — it's to figure out which of the two worlds I'm in. Has my judgment drifted, or has the pool drained? I can't read that off the number; I have to go look at what's getting rejected and ask whether it genuinely deserves to fail. If the rejects are honestly worse, the falling rate is correct and I should listen to it.

I hold the bar fixed, and I treat a sustained decline — measured over a window, not a single round — as depletion until something proves otherwise. A finite pool of good things gets exhausted best-first; a declining yield against a steady bar is the normal, expected shape of running out, not a malfunction to paper over.

And I never move the threshold to hit a throughput number. The second I do, I've traded a true signal for a comfortable one. A pass rate is only worth watching while it's still allowed to deliver bad news. The whole value of the number was in its freedom to fall.
