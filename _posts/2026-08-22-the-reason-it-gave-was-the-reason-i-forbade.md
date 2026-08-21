---
layout: post
title: "The Reason It Gave Was the Reason I Forbade"
subtitle: "I wrote an exemption into a grading rubric — one line telling the judge not to reject items for a specific reason. Then I read the rejections, and the reason they gave was almost a verbatim restatement of the thing I had forbidden. The model hadn't ignored my instruction. It had reasoned its way past it."
date: 2026-08-22
author: danmi
translation: /2026/08/22/the-reason-it-gave-was-the-reason-i-forbade-zh.html
tags: [prompt-design, llm-as-judge, evaluation, methodology, data-curation]
---

I built a rubric for a model to grade a large pile of candidate tasks — keep, rewrite, or reject. The rubric had two kinds of rules, and only one kind held. That's the whole post, but the *why* is the part worth keeping.

## Two kinds of rules in the same prompt

Near the top was a hard gate: if a task fails a specific structural check, reject it immediately. Short, imperative, no discussion.

Near the bottom was a softer clause, inside a list titled roughly *do not use these as grounds for rejection*. One line of it said: don't reject a task just because it needs live or external data, or asks the agent to fetch a URL — the agent has tools, that's expected, it's in scope.

Both were in the same prompt, submitted in the same request, read by the same model. I assumed they'd carry the same weight. They did not.

## The exemption came back inverted

Someone asked me whether tasks that required an external lookup were getting wrongly rejected. I pulled the reject reasons to check.

They were. And the reasons read like a rebuttal to my own exemption, written in the model's voice:

- "the agent can't reliably obtain or verify this; the core input is missing"
- "this depends on a real-time external platform, the data can't be fabricated"
- "requires a live source with a publish date and a link that can't be invented"

Read those again against the exemption. The exemption said *needing external data is fine, the agent has tools.* The rejections said *it needs external data the agent can't verify, therefore reject.* The model had reconstructed, in its own words, the exact criterion I had explicitly told it not to use.

Meanwhile the hard gate at the top worked perfectly. Every task that tripped it was rejected, cleanly, no drift. So this wasn't a model that ignores instructions. It was a model that honored one instruction and reasoned straight through the other.

## Why the gate held and the exemption didn't

The difference isn't strictness of wording. Both lines were clear. The difference is *where each rule sits relative to the model's reasoning.*

A short-circuit gate — "if X, reject now" — is evaluated as an action. The model checks a condition and emits a verdict. There is no gap for reasoning to fill, because the rule fires before any argument gets built.

An exemption inside a "do not penalize for Y" list is something else entirely. It's a negative constraint on a conclusion the model reaches *through its own reasoning*. By the time the model asks itself "should I reject this?", it has already assembled a case: this task needs data the agent can't guarantee, so the core input is unreliable, so the task is weak. That case feels like competent judgment — because it is, locally. The exemption is now asking the model to drop a conclusion it independently reasoned its way into.

Reasoning wins that fight almost every time. And here's the uncomfortable part: the model doesn't experience it as disobedience. It experiences it as applying good judgment. My one line at the bottom of a list is a weak prior, and it's up against a locally compelling argument the model built itself. A weak prior loses to a strong argument. That's not a bug in the model; that's what reasoning is for.

## Negative instructions are the weakest control you have

Generalize it. "Don't do X." "X is not a reason." "Avoid Y." These are the weakest form of control you can hand a reasoning model, because they sit *downstream* of the reasoning they're supposed to constrain. The model reasons first. Then the prohibition has to reach back and overturn a conclusion the model already trusts.

That's precisely the worst position to instruct from. You're not shaping the thought; you're asking the model to distrust a thought it already had. The more capable the model, the more confidently it reasoned its way to the conclusion, the harder your "don't" has to push — and the softer and more buried your "don't" is, the less chance it has.

Prohibitions work fine for cosmetic things the model has no strong prior about ("don't use bullet points"). They fail for anything the model can build a case around, which is exactly the class of rule you care most about getting right.

## The fix is to move the rule upstream and make it positive

The exemption failed because it was negative and late. So make it positive and early.

Instead of "don't reject for needing external data," buried in a list, put near the top, at gate level: *If a task requires live or external data, treat that as expected and in scope — the agent has tools. A task that needs a live lookup is a keep, not a reject.* Then give it a worked example: here's a task that needs external data, here's why it's fine, verdict → keep.

Now the exemption is a short-circuit rule with a positive form and a concrete case, evaluated at the same level as the hard gate — *before* the model assembles its own rejection argument. You've moved it upstream of the reasoning instead of leaving it to fight the reasoning after the fact. The gate held for the hard check; give the exemption the same shape and it holds too.

Positive, early, exemplified. All three matter. Positive so the model executes it instead of overruling it. Early so it fires before the counter-argument exists. Exemplified because a worked case is a stronger anchor than an abstract clause, especially against the model's own fluent reasoning.

## What I do differently

Any rubric constraint I actually care about, I now state as a positive action at gate level with an example — *when you see X, do Y* — never as a prohibition in a "do not" list. If I can't phrase a rule that way, that's a signal the rule is weak and the model will reason around it, and I'd rather find that out while writing the prompt than while reading a wall of wrong verdicts.

And I test exemptions specifically. Not the whole rubric — the exemptions, in isolation. Feed the judge the exact class of item each exemption is meant to protect, and read the verdicts. Because a prompt that *contains* an exemption and a model that *honors* it are two different things, and the gap between them is invisible until you go looking for it. I found this one because someone asked. I'd rather the test find the next one before someone has to.
