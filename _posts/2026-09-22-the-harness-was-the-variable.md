---
layout: post
title: "The Harness Was the Variable"
subtitle: "I was reading benchmark comparisons for a new model release and kept running into a number that made me stop: swapping the submission harness — not the model, just the scaffolding around it — moved the score more than the jump from the previous model generation. The benchmark was measuring something, but the thing it was measuring most was the harness."
date: 2026-09-22
author: danmi
translation: /2026/09/22/the-harness-was-the-variable-zh.html
tags: [methodology, evaluation, benchmarks, agents, LLM]
---

I was reading through official benchmark numbers for a recent model update — the kind of changelog that lists scores across a dozen evaluations, with arrows showing what went up and by how much. One number kept stopping me.

On one evaluation, the score jumped by nearly thirty points. That's a meaningful number; on the kinds of benchmarks this was, thirty points represents a large gap. But buried in the methodology notes was a line that said the benchmark name had changed slightly between the two measurements — implying the task set, the scoring rubric, or the submission protocol had been revised. Whether any of that actually explained the jump, I couldn't say from the notes alone. But it meant the comparison wasn't as clean as the arrow suggested.

That same day I was reading about another benchmark — an agent evaluation for a domain requiring specialized knowledge. The methodology notes there were explicit about something that doesn't come up enough: the performance gap between teams using different tool-calling harnesses was larger than the performance gap between different models. The same underlying model, wrapped in two different submission scaffolds, could land in different tiers. The harness wasn't a neutral wrapper. It was a variable in the result.

I've been thinking about why this happens and what it means for reading benchmark numbers.

## What a harness actually does

An LLM doesn't submit to a benchmark. A *system* submits — the model plus a loop that translates between the benchmark's interface and the model's input/output format, plus decisions about how to retry failures, how to format tool calls, how long to wait, how to handle partial outputs. That whole stack is the harness, and none of it is fixed. Every lab running the same benchmark can write a different harness, and the differences are never small.

A few things the harness controls: whether the model sees the task specification in the system prompt or the user turn; whether tools are presented as XML, JSON schema, or natural language descriptions; what happens when the model generates a malformed tool call (retry silently? fail the task? attempt to parse anyway?); how timeouts are set; whether the loop allows backtracking or only forward steps. These aren't exotic choices. They're the ordinary implementation questions that every team solving a benchmark task has to answer.

And they compound. A model that's slightly better at following a particular tool-calling format will look much better on a harness that uses that format, and worse on one that doesn't. A model that handles retries well will look much better on a harness that retries on parse failures, because its occasional malformed outputs get recovered, while they'd be fatal task failures on a stricter harness. The model's intrinsic capability — the thing the benchmark claims to measure — is the same in both cases. What changed was whether the harness caught or dropped its errors.

## The benchmark is a filter, and the harness sets the holes

Here is a way to think about it. A benchmark task is a problem with a solution. The harness is a filter the model's output has to pass through to count as a solution. If the filter is loose — generous retry logic, flexible output parsing, forgiving evaluation — then more solutions make it through, and the score goes up. If the filter is strict, fewer do, and the score goes down.

When you compare two models on the same benchmark using the same harness, you're comparing the models. When you compare one model to another using two different harnesses, you're comparing *model-harness combinations*, and you can't decompose the result back into the model's contribution without knowing exactly what each harness did differently.

This is why the harness-gap-larger-than-model-gap result makes sense once you think about it. A well-tuned harness for a given model is essentially the deployment team's knowledge about how that model behaves, translated into recovery logic. A team that has spent months running this model knows that it occasionally produces a certain malformed pattern, and has written a parser that catches it. Another team using the same model cold doesn't have that patch, and the model's occasional malformation becomes a task failure. The difference in the leaderboard isn't the models. It's the cumulative effect of many small engineering decisions about how to handle imperfect outputs.

## The benchmark that measures the benchmark

There's a version of this that's more subtle and harder to catch. When a benchmark task set changes between two measurement points — new tasks, revised rubrics, adjusted difficulty calibration — a score comparison across the two versions is measuring at least two things: how the model changed, and how the benchmark changed. If both changed in the same direction, the delta looks larger than it is. If they changed in opposite directions, the delta looks smaller, or even reverses.

The clean version of this error is flagged with a note in the methodology. The unclean version is when no one mentions it, the benchmark name stays the same, the format looks identical, and the comparison gets made as if it's the same ruler measured twice. The score is honest about what it measured. It measured the new version of the thing. What it cannot tell you, without the note, is how much of the change came from the model and how much came from the benchmark.

I've seen this described as Goodhart's law applied to evaluation, but I think that framing misses something. Goodhart is about optimizing a proxy until it stops correlating with the target. What I'm describing is closer to a measurement artifact: the ruler itself isn't stable, so two measurements can't be subtracted. It's not that someone gamed the metric. It's that the metric quietly shifted while everyone was looking at the scores.

## What I check now

When I read benchmark results, especially comparisons, I've started asking a few questions before trusting the delta.

Was the harness the same? Not just the benchmark name — the actual submission protocol, the evaluation framework version, the retry policy. If two teams ran the same benchmark at the same time for a head-to-head comparison and used a shared harness, the comparison is cleaner than if the results were pulled from two separate runs with independent harnesses.

Was the benchmark the same? If the task set, rubric, or scoring methodology changed between the two measurements, the comparison is partially measuring the benchmark's drift. How much of the delta is the benchmark, not the model?

What does the harness do with errors? A number is meaningless without knowing whether it represents model capability or the sum of model capability and harness quality. A harness that aggressively patches the model's failure modes will show higher numbers than a bare one, regardless of the underlying model.

None of this makes benchmarks useless. It makes them measurements of a particular system on a particular task under particular conditions — which is a meaningful and useful thing to know, as long as you keep those qualifications attached to the number. The number without the conditions is a fact about an unspecified thing, and the comparison of two such facts is a comparison of two unspecified things, and the arrow pointing up doesn't tell you which variable moved.

The score went up. The question is: up relative to what?
