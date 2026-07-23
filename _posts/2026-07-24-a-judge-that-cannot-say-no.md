---
layout: post
title: "A Judge That Can't Say No"
subtitle: "An LLM asked whether something is useful will say yes to almost everything — and a rubric where the honest answer is nearly always yes ranks nothing, even when every single score is defensible."
date: 2026-07-24
author: danmi
translation: /2026/07/24/a-judge-that-cannot-say-no-zh.html
tags: [evaluation, llm-as-judge, methodology, data-selection, epistemics]
---

I was using a language model to sift a big pile of web pages. The goal was mundane: for each page, decide how useful it would be as raw material for a particular kind of build — could you learn something from this page that helps you construct that kind of thing. The model scored each page from zero to one, I planned to keep the high scorers and drop the rest, and the whole thing ran fine. Then I looked at the distribution of scores and the pipeline quietly fell apart, because the model had rated almost everything useful.

Not "many things." Almost everything. Page after page came back at 0.7, 0.8, 0.9. And here is the part that took me a moment to sit with: the model was not wrong. Each individual judgment was defensible. Could you learn something about building a web page from a SaaS landing page? Yes. From a blog? Yes. From a documentation site, a portfolio, a government form, a news homepage? Yes, yes, yes, yes. Almost any web page teaches you *something* about making web pages. The model answered the question honestly, one page at a time, and the honest answer was nearly always yes.

Which meant my ranking was noise. A score that everything gets is not a filter. I had built a judge that could not say no.

## Individually correct, collectively useless

This is the trap, and it is subtler than the usual "the model hallucinated" complaint. The model didn't hallucinate. It didn't lie. If I'd audited any single score, I'd have nodded along. The failure lived entirely at the level of the *distribution* — a property no individual judgment can reveal. You can only see it by lining the scores up and noticing they don't spread.

The reason is in the question, not the model. I had asked something of the form "could X be useful for Y?" — and "could" is a low bar that reality rarely trips over. Almost anything *could* be useful for almost anything, if you squint. Ask a permissive question and you get a permissive answer, correctly. The model faithfully reported that the world is full of things that could conceivably help, which is true and which discriminates nothing.

A metric earns its keep by *saying no*. A rubric where most items pass isn't lenient; it's blind. It has thrown away its negative half, and a measurement with only a positive half isn't a measurement — it's a rubber stamp with a decimal point.

## The tell is the spread, not the value

The cheap diagnostic here is one I now reach for early: don't look at whether the scores seem reasonable, look at whether they *separate*. Sort them. If the top of the list and the bottom of the list are both "yes, useful," the axis is dead no matter how sensible each number looks in isolation. A healthy discriminating metric produces a distribution with a real low end — items the judge was willing to reject, and not just a handful of obviously broken ones.

If nearly everything clusters near the top, you don't have a selective filter. You have a detector for one narrow failure — the page that's blank, the file that's corrupt — dressed up as a quality score. That detector might be worth keeping, but it is not the thing you thought you built, and treating its output as a ranking will select essentially at random from everything above the floor.

## Fix the question, not the threshold

The instinct is to raise the bar: if everything scores 0.8, keep only the 0.9s. This almost never works, because when the whole distribution is compressed against the ceiling, the difference between 0.8 and 0.9 is exactly the noise you were trying to escape. You're now ranking on the model's rounding behavior.

The real fix is to ask a question most things should *fail*. Instead of "could this page be useful," ask something with a built-in scarce resource — "is this among the best examples of the specific structure I need," or "does this page do the one hard thing I'm trying to learn, or merely sit near it." A good rubric names what would make an item *not* qualify, concretely, before any scoring happens. If you can't state what a clear "no" looks like, the model can't produce one either, and you will get a wall of polite yeses.

There's a companion move that helps even when the rubric is fuzzy: force scarcity from the outside. Don't ask for an absolute score per item; ask the judge to rank a batch and take the top few, or to pick the single best of a group. Comparison creates a "no" that an isolated judgment won't — even if everything is somewhat useful, something is the most useful, and now the metric has to spread.

## The general shape

This isn't really about web pages, or even about LLM judges. It's about a class of evaluation that feels rigorous — per-item scores, clean thresholds, a model dutifully rating everything — and quietly measures nothing, because the question was answerable "yes" for the whole population. The scores were all real. The ranking they produced was fictional.

Before you trust a judge, look at what it rejects. A judge that passes almost everything hasn't told you your data is good. It has told you your question doesn't discriminate — and a question that can't produce a "no" was never asking anything.
