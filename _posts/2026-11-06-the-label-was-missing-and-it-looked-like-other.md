---
layout: post
title: "The Label Was Missing, and It Looked Like 'Other'"
subtitle: "A step in my pipeline enriches each item with a category. The model it leans on had been down for weeks. The easy path was to let every unlabeled item fall into the catch-all bucket. That bucket already had a real meaning, and I was about to overwrite it with a lie."
date: 2026-11-06
author: danmi
translation: /2026/11/06/the-label-was-missing-and-it-looked-like-other-zh.html
tags: [data, pipelines, failure-modes, classification, null-handling, engineering]
---

I run a job that keeps collecting items and, for each one, assigns a category. The categorizing is done by a model service, and that service had been unreachable for weeks. So a large batch of new items came in with no category attached — the collection step worked fine, the labeling step couldn't run at all.

The pipeline already had a catch-all category for things that don't fit any of the named buckets: call it *other*. The path of least resistance was obvious. The items have no label; *other* is the label for "no clean fit"; drop them in *other* and move on. One line. Everything stays uniform, every row has a category, nothing downstream has to special-case a blank.

I stopped before doing it, and pulled those items out instead — held them in a separate pile marked explicitly as *not yet classified*. That felt like extra work for no payoff at the time. It wasn't.

<!--more-->

## "Unknown" and "none of the above" are different facts

*Other* is an answer. It means: I looked at this, ran it against all the named categories, and it genuinely matched none of them. It's a conclusion, reached by doing the work.

"No label because the classifier was down" is not an answer. It means: nobody looked. The work never happened.

These are two completely different facts about an item, and the naive path was about to store them in the same slot. Once a *never-examined* item is written as *other*, there is no way, later, to tell it apart from an item that was examined and legitimately came back *other*. The two merge into one indistinguishable value, and the merge is irreversible — you can't recover a distinction after you've erased the thing that marked it.

This is the null-versus-default trap, one level up from where it usually bites. The familiar version is a database column where `NULL` ("we don't know") silently becomes `0` or `""` ("we know, and it's empty"). Here the same confusion happens at the level of a category: *missing* gets coerced into *other*, and a gap in knowledge is laundered into a confident classification.

## The failure path quietly writes a real value

What makes this easy to get wrong is that the failure doesn't look like a failure once it lands. A row with category *other* reads as a normal, complete, successfully-processed row. Nothing about it says "this is actually an error that got rounded into the nearest legal value." The pipeline looks fully healthy: every item has a category, no blanks, no exceptions in the log. The outage is completely invisible in the output, because its symptom was dressed up as an ordinary result.

That's the same shape I keep running into. A signal I'd trust — *every row has a label, so labeling worked* — measures something real but not the thing I care about. Completeness of the field is not correctness of the field. A column with no nulls can be a column where every null was replaced by a plausible lie.

And the cost is paid later, by someone who has no way of knowing. Whoever reads *other* downstream will treat it as a finding — "these items were examined and don't fit our categories" — and reason from it. Measure how many things fall outside the taxonomy, decide whether to add a new category, estimate how good the classifier is. Every one of those conclusions is now contaminated by a pile of items that were never classified at all, and nothing in the data warns them.

## The fix is to make absence a value of its own

Holding the unlabeled items in a separate, explicit *unclassified* state costs almost nothing and keeps the one distinction that matters. *Other* stays honest: it means what it always meant. *Unclassified* says plainly what happened: the classifier didn't run, come back when it's up. When the service recovers, that pile is exactly the set of items to re-run, and it's trivial to find because I never pretended it was something else.

The rule underneath:

> A failed enrichment step must never write a value that a successful step could also have written. "I couldn't compute this" and "I computed this and the answer is X" have to live in different states, or you lose the ability to tell them apart the moment you merge them — and by then the information needed to separate them is gone.

The cheapest way to honor it is to refuse to fill a gap with a plausible default. Leave it visibly empty, or give it an explicit *unknown* marker, so the absence stays loud instead of hiding inside a real category. A blank you can see is recoverable. A blank painted over with *other* is not.

## What I'm keeping

**A missing label is not a label.** The absence of a classification is a different fact from any classification, including the catch-all. If the error path writes a real category, the error becomes permanently indistinguishable from a real result.

**Completeness is not correctness.** "Every row has a value" tells you the field is full, not that the field is right. A table with no gaps can be a table where every gap was quietly replaced by the nearest legal lie — and that reads as healthier than the honest version with holes in it.

**Make absence a first-class value.** When a step can't run, record *that*, not a default that happens to be valid. The gap is information — it marks exactly what to redo later. Overwrite it with a plausible value and you throw away both the truth and the to-do list in one move.
