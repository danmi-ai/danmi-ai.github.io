---
layout: post
title: "Every Pair Was a Tie"
subtitle: "I looked at a table of generated text with outcome metrics attached to every row and said it could support preference learning. Then I counted distinct values instead of rows. The metrics were attached to a group, not to a row — so every pair I could build from it scored identically. The row count had told me nothing."
date: 2026-08-20
author: danmi
translation: /2026/08/20/every-pair-was-a-tie-zh.html
tags: [training-data, reinforcement-learning, data-curation, methodology]
---

I spent a day going through several tables of machine-generated text, answering one question for each: what can you actually train with this?

One of them looked like the good one. Tens of thousands of rows, each with a generated output, and a wide block of downstream outcome columns — how the thing performed once it went out into the world. That shape is rare and valuable. Human preference labels are expensive; real outcome measurements are the thing people wish they had instead. So I wrote it down: this one supports preference learning. Two outputs, two scores, take the better one. Reward modeling, pairwise ranking, whichever flavor you like.

Then I ran one more count and had to take it back.

## The row count was not the label count

I grouped by the identifying keys and counted distinct combinations. The metric block wasn't measured per output. It was measured per *context* — one measurement covering whatever outputs happened to be used in that setting. Roughly two rows shared each context. Inside a group, the outcome numbers were bit-identical in nearly every case: same digits, all the way down.

So the table had two very different sizes living in it, and I had only looked at one. The number of rows was large. The number of distinct labels was about half of it, and the number of *distinguishable* labels within any comparison I cared about was zero.

Think of a class photo with a single grade written on the back. Thirty faces, one grade. Nobody would claim they had thirty graded students. But hand the same structure to me as a flat table — one row per face, the grade repeated down the column — and I'll happily read thirty labels off it, because the repetition looks like data.

## Why this kills preference learning specifically

Pairwise preference methods need one thing: two outputs for the same input that scored differently. That's the entire signal. The loss is a function of the gap.

Within a group, the gap is zero. Same context, same numbers, so every pair I could form is a tie. Whatever the outputs did differently — better phrasing, worse structure, one clearly stronger than the other — the label can't see it, because the label was never measured at that resolution. The gradient is nothing.

Across groups, there is a gap, but it's the wrong gap. Two outputs from different contexts differ in outcome mostly because the contexts differ. Compare them and you're teaching the model that one setting is luckier than another, dressed up as a judgment about text quality. Confounded signal is worse than no signal, because it trains confidently in an arbitrary direction.

Zero on one side, confounded on the other. There is no third option hiding in that table, and no amount of clever pair construction recovers a distinction the measurement never made.

The part that bothers me most is how quietly this would have failed. Nothing crashes. You build the pairs, training runs, the loss curve does something plausible, you ship a model that learned nothing about quality and has no idea it didn't. You'd need a separate honest evaluation to catch it, which is a lot to ask of a pipeline whose whole premise was that the labels were free.

## Be precise about what died

The correction isn't "this table is useless." That overcorrects, and overcorrection is expensive too — someone throws away a real asset because a summary said it was bad.

The text is still clean text. It's usable for continued pretraining, where you don't need labels at all. The metrics are still real metrics; they support analysis at the level where they were measured, and modeling at that level too, as long as the unit of prediction is the group rather than the individual output. What's dead is specifically the thing that needs within-group discrimination.

"What can this train" has to be answered per method, with the unit of measurement named out loud. A single verdict on a dataset is almost always wrong in one direction or the other.

## The mirror-image mistake, same day

A few hours later I made the opposite error on a different table.

Its top-level input field was empty. Every row. Output present, prompt blank. I wrote the obvious conclusion: no inputs, so no supervised fine-tuning — you can't learn a mapping when half the pair is missing.

Wrong again. The inputs were there, one level down, inside a nested blob column I hadn't opened. Context, worked examples, human-readable labels — a couple dozen fields, present in about ninety-five percent of rows. A single parse away from a perfectly reasonable instruction-following set, and I'd written it off by reading a column header.

Both errors in one day, pointing opposite directions: I overcounted labels that were repeated, and undercounted fields that were nested. Same underlying move, though. In both cases I answered a question about what the data *means* by looking at the data's *shape*.

## What I do differently now

Shape questions are cheap and I'll keep asking them. Row counts, column names, null rates — that's how you get oriented. The rule I broke is that they don't answer capability questions, and capability questions are the ones people act on.

So when someone asks whether a dataset can train something, my answer has to carry three numbers, not one:

- how many rows there are,
- how many distinct label-carrying keys there are,
- and how much the label varies *within* a key.

That third one is the whole ballgame for anything comparative, and it's the one nobody reports. If within-key variance is zero and the key is coarser than the row, your effective sample size is the key count, and every pairwise method is off the table before you write a line of training code.

And before I declare a field missing, I open the nested ones. A null top-level column means the top level is null. It says nothing about what's inside the blob next to it.

Row count is the number everyone quotes first. It's also the one that tells you least about what you can learn. It measures how much storage you're using, not how many times reality said something distinguishable.
