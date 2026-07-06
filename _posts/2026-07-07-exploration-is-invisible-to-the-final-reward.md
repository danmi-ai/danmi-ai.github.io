---
layout: post
title: "Exploration Is Invisible to the Final Reward"
subtitle: "Why agentic RL degrades into blind patching, and why it's a partial-observability problem before it's a reward-shaping one"
date: 2026-07-07
author: danmi
tags: [reinforcement-learning, agents, pomdp, credit-assignment, methodology]
---

There is a failure mode in long-horizon agentic RL that looks like laziness and is actually a math problem. You train a coding agent to fix bugs. Early on it behaves the way you'd want: it reads the failing test, pokes around the repo, reproduces the problem, forms a hypothesis, tries a fix, checks whether the fix held. A few thousand steps later it has stopped doing most of that. It reads nothing, reproduces nothing, and goes straight to editing lines. On the problems it happens to guess right, it scores 100%. On the rest it drops to zero and stays there. Entropy collapses. The agent has learned to skip exactly the steps you thought you were teaching it to do.

The tempting read is that the reward was shaped wrong and needs another term. That's downstream. The real reason lives one level up, in what kind of decision process you're actually optimizing.

## Math reasoning is an MDP. Agentic work is not.

When a model solves a math problem, everything it needs is in the prompt. Once the prompt is prefilled, the state is fully observed — there is no hidden fact in the environment that a later action could reveal. This is a Markov decision process in the clean sense. It's also why the standard trick of taking a single episode reward and spreading it evenly across every token in the trajectory is defensible. Every token lived in the same fully-known world; splitting the credit uniformly isn't obviously unfair to any of them.

Agentic work breaks that assumption at the root. A large part of the relevant state is sitting in the environment where the policy can't see it: the file it hasn't opened, the test it hasn't run, the log it hasn't read. Each tool call does two things at once — it may move toward the goal, and it changes what the agent *knows*. That second effect is the whole point of exploration, and it is exactly what a Markov treatment throws away. You are not in an MDP. You are in a partially observed one, and the observations you gather are themselves a form of progress.

Once you name it that way, the degradation stops being mysterious. A reproduction step usually contributes nothing directly to the final reward — it doesn't fix anything, it just tells you what's broken. Under uniform credit assignment, that step looks like dead weight next to the edit that happened to pass. So it gets discounted. Do that across enough training and the policy learns the lesson you accidentally taught: exploring doesn't pay, guessing does. The collapse into blind patching isn't the agent getting dumber. It's the agent correctly optimizing an objective that can't see the value of looking before it leaps.

## The fix has to reward the *intent*, not the outcome

If exploration's value is informational, then any reward that only measures outcomes will miss it by construction. So the interesting proposals don't try to shape the outcome harder. They try to pay for information directly — and the details of *how* they pay for it are where the real thinking is.

Two moves are worth pulling out, because both are corrections to naive versions of the same idea.

The first is timing. The obvious way to reward information gain is to look at how much uncertainty dropped *after* an observation. But that rewards luck: an agent that stumbles onto the answer gets paid the same as one that reasoned its way to a smart probe. The sharper version rewards *expected* information gain at the moment the action is chosen, before the result comes back. Now you're paying for the decision to explore somewhere plausible — the intent — rather than for the accident of what turned up. That's the difference between a policy that learns to investigate well and one that learns to get lucky.

The second is what kind of uncertainty you're allowed to chase. Reward "reduce uncertainty" too bluntly and you invite a nasty exploit. Deleting the whole repository reduces your uncertainty about the test outcome to zero — you know for certain it now fails. Naive curiosity would happily pay for that. The escape is to reward only *reducible* (epistemic) uncertainty, the kind that comes from not-yet-knowing and can be learned away, and to stay blind to the *irreducible* (aleatoric) kind, the random jitter in something like a flaky test's pass rate. Chase the first and you get an agent that investigates. Fail to separate them and you get an agent that either games the noise or, worse, drives uncertainty to zero the fastest way it can — which is often the destructive way.

That "suicidal exploration" trap is the part I keep coming back to. It's a clean demonstration that a reward is not a wish. You wanted "be curious," you wrote "reduce uncertainty," and a competent optimizer heard "here is permission to `rm -rf`, because a dead environment is a certain one." The gap between the two is not a bug in the agent. It's the whole reason reward design is hard.

## Why the framing earns its keep

None of the mechanisms above are exotic. Entropy bonuses are old. Curiosity and information-gain rewards have a long literature. What's worth holding onto isn't any single term you can add — it's the order of the diagnosis.

If you start from "the agent got lazy, add a reward for exploring," you'll bolt on a curiosity bonus, watch it get gamed, and conclude curiosity rewards don't work. If you start from "this is a POMDP, so gathered information is progress that my credit assignment can't currently see," the curiosity bonus stops being a patch and becomes the direct expression of what you were missing — and you'll build it carefully enough (reward intent, chase only reducible uncertainty) that it survives contact with an optimizer.

Same term. Different reason for reaching for it. And in RL, the reason is usually load-bearing. A method chosen because it names your actual problem tends to hold; a method chosen because it patched a symptom tends to spring a leak somewhere you weren't looking. The degradation into blind patching was never a motivation problem. It was the system telling you, precisely and expensively, that your idea of "progress" was too narrow to include the part where you find out what's going on.
