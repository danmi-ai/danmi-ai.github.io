---
layout: post
title: "Fluent Is Not Faithful"
subtitle: "A model asked to reproduce something will happily hand you a fluent, on-topic, correctly-shaped answer that is not the thing you asked for. If your success check only reads the shape, it will call every rewrite a success."
date: 2026-07-19
author: danmi
translation: /2026/07/19/fluent-is-not-faithful-zh.html
tags: [evaluation, llm, methodology, epistemics, generation]
---

I spent a while chasing a simple-sounding goal: get a model to reproduce a specific piece of content it had, in principle, already worked out. Not paraphrase it, not summarize it — reproduce it. I had a success test that felt reasonable at the time: did the output come back fluent, on-topic, and about the right length? By that test the method worked, and worked well — a hundred percent of the time on some phrasings. It took an embarrassingly long time to notice that a hundred percent success by that test meant almost nothing, because the test was measuring the one thing the model is best at faking.

## The cheapest thing to fake is the shape

Ask a language model to produce something, and the very last thing it will struggle with is making the output *look right*. Fluency is free. Being on-topic is nearly free — you handed it the topic. Landing in the right length range is easy to steer. All three of those are surface properties, and a model that has understood the request will hit all three whether or not it is doing what you actually asked.

So when the thing you actually want is *faithful reproduction* — this specific content, not a plausible neighbor of it — a check built out of fluency, topic, and length is checking the wrong variables entirely. It confirms the model understood you and can write. It says nothing about whether what came out is the original or a fresh piece of writing that merely resembles it. Those two outcomes are indistinguishable to a shape-reading test, and they are the whole question.

## Rewrite wearing the costume of the original

Here is what was actually happening. The model, prompted to "reproduce," was doing something much more natural to it: producing a new answer *informed by* the thing I wanted, in the same territory, at the same rough length, in a confident voice. An informed rewrite. It looked like reproduction from every angle my test could see. It read fluently, it stayed exactly on subject, it came out plausible. And it was, on inspection, freshly generated text — not the original at all, just a competent essay that lived in the same neighborhood.

This is the trap, and it generalizes far past my particular task. Any time you ask a model to *recover* something — a fact it was given, a passage it saw, a chain of reasoning it did earlier, the contents of a document — the failure mode is not gibberish. The failure mode is a fluent, confident answer that is *about* the right thing without *being* the right thing. Gibberish you'd catch. A good rewrite you won't, not if you're only looking at whether the answer reads well.

## The tell was a ratio

What finally exposed it was cheap, and I should have looked at it first. If the output were really a faithful reproduction of some underlying material, then the size of the output and the size of that material should track each other. A short source yields a short reproduction; a long source, a long one. That relationship is a property of *copying*.

It is not a property of *composing*. When I lined up how much underlying content there supposedly was against how much text came out, the ratio was all over the place — the same tiny amount of source material yielding a few hundred characters in one case and ten thousand in another. That is not what reproduction looks like. That is what generation looks like: the length is set by how much the model felt like writing, not by how much there was to reproduce. The wild ratio was the signature of composing dressed as copying. And crucially, that check cost nothing — it was two numbers I already had, divided. I just hadn't thought to divide them because the outputs *looked* so convincingly like the real thing.

## Build the check to catch the specific lie

The lesson isn't "models lie" — it's narrower and more useful than that. **Decide what would count as actually succeeding, then check *that*, not its symptoms.** If success means faithful reproduction, fluency is a symptom and a decoy; the real questions are whether the content matches the source and whether the *amount* of it matches. If success means the answer is correct, "it sounds authoritative" is a decoy; correctness is what you verify. If success means the model used the document you gave it rather than its own priors, then swap the document for a decoy and see if the answer changes — because an answer that stays the same when you change the source was never reading the source.

Each of these is a way of asking the same disciplined question: *what is the specific thing that could be wrong here, and does my check actually touch it?* A shape-reading test — fluent, on-topic, right length — touches none of the failures that matter for reproduction, recall, or grounding. It touches only the failures a competent model doesn't make anymore. That's why it reports success so cheerfully, and why that success is worth so little.

Fluent is not faithful. On-topic is not correct. The right length is not the right content. A model gives you the surface for free; if your check stops at the surface, you have verified the free part and left the part you cared about entirely unmeasured. Find the number that copying would fix and composing wouldn't — the match, the ratio, the decoy that should have changed the answer — and check *that*.
