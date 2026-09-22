---
layout: post
title: "The Judge Only Saw the Flaw I Already Knew About"
subtitle: "I built a system where a language model played reviewer, and every reviewer rejected every submission for the exact gap I'd deliberately left in and didn't care about. The evaluation ran perfectly and told me nothing about the thing I wanted judged. The problem wasn't the judge's competence. It was that I'd asked it to judge holistically, and holistic judgment means fixating on the biggest visible flaw."
date: 2026-09-23
author: danmi
translation: /2026/09/23/the-judge-only-saw-the-flaw-i-already-knew-zh.html
tags: [methodology, evaluation, LLM, judge, prompting]
---

I was building a system where a language model played the role of a reviewer. Submissions came in, and a panel of model-reviewers scored them and wrote critiques, and a final decision got made from those scores. To test the pipeline before it was fully built, the submissions were intentionally incomplete along one dimension: the empirical results were placeholders — stand-in numbers, not real measurements. I knew that. It was the whole point of a dry run. I wanted to see whether everything *else* worked: the framing, the reasoning, the structure of the critique.

Every reviewer rejected every submission. And every rejection said the same thing: the results are not real, there is no empirical evidence, this cannot be accepted.

## The evaluation ran perfectly and measured nothing

Nothing was broken. The reviewers produced well-formed scores. The decision logic aggregated them correctly. The critiques were coherent. If I'd only checked that the pipeline *ran*, I'd have called it a success.

But the output carried zero information about what I was trying to test. I already knew the results were placeholders — I put them there. The reviewers had spent their entire evaluation discovering the one fact I'd handed them at the start, and then stopping. They never got to the framing or the reasoning, because they never got past the missing evidence. The most salient flaw ate the whole review.

This is the trap: a judge that latches onto the single most nameable deficiency and never moves past it will produce a confident, well-structured, completely useless verdict. Useless not because it's wrong — the results really were placeholders — but because it answers a question I wasn't asking and had already answered myself.

## Holistic judgment means "find the biggest problem"

When you ask a model to "review this" or "evaluate this," with no further scoping, you've asked for a holistic judgment. And holistic judgment, for a reviewer, resolves almost immediately into a search for the largest visible weakness. That's what reviewing *is* by default: find the thing most wrong with this, and let it dominate the verdict. If a submission has one glaring hole, every holistic reviewer finds that hole, reports it, and rates accordingly. They're not being lazy. They're doing exactly what "evaluate this" asks — they just all converge on the same most-obvious target.

A human reviewer handed an obviously unfinished paper does the same thing. They'll write "the evaluation section is incomplete, I can't assess the contribution" and put down the pen. The difference with a model is reliability and completeness: it will do this *every time*, and it will spend its entire budget on the first flaw it can name, with none left over for anything underneath. There's no human tendency to think "well, they said this was a draft, let me look past that and comment on the idea." The model takes the artifact as it is and grades it as it is.

## The fix wasn't a better judge. It was a scope.

I added one thing to the reviewer's instructions: an explicit statement that the placeholder results were a known, accepted condition of this review, and that reviewers must not reject or downgrade on the grounds of missing empirical evidence. Judge everything else. Treat the results as given.

The reviews changed completely. Freed from the one objection they'd all been parking on, the reviewers went to the actual substance — and their criticism got sharp and useful. They found real weaknesses in the reasoning. The final decision flipped from unanimous rejection to a genuine, mixed assessment of the idea's merits. Same model, same panel, same submissions. The only change was telling the judge what *not* to judge.

That's the part worth keeping. I didn't make the judge smarter or the prompt longer in the direction of "be more thorough." I made it *narrower*. I defined what was out of scope. An evaluation instruction that only says what to look for will, by omission, invite the judge to look for everything — and "everything" collapses to "the biggest flaw." Saying what to ignore is what forces the judge past the surface.

## What I take from it

An LLM judge with no scope defaults to fault-finding, and fault-finding defaults to the single most salient fault. If that fault is something you already know about and don't care about for this evaluation, the judge will burn the entire review on it and hand you a verdict with no signal in it.

So when I set up a model to evaluate something now, I don't just tell it what to assess. I tell it what to treat as given. Known limitations, deliberate simplifications, things outside the current question — I name them and rule them out of scope explicitly, because a judge won't infer that a known gap is uninteresting. It will find the gap, because finding gaps is the job, and it can't tell the difference between the gap I care about and the one I built in on purpose.

The general shape: a judgment is only as informative as its scope is precise. "Evaluate this" is not a question — it's an invitation to find the biggest problem, and the biggest problem is often the one you already knew was there. If you want to learn something you don't already know, you have to fence off the things you do. The signal you're after is usually sitting just past the flaw the judge can't stop talking about.
