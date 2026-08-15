---
layout: post
title: "The Model Didn't Get Worse, the Room Did"
subtitle: "A system scored well on its own benchmark and mediocre inside a popular general-purpose scaffold. The easy read was that the benchmark was inflated. The real story was that a score is never a property of the component alone — it belongs to the whole room the component was standing in."
date: 2026-08-16
author: danmi
translation: /2026/08/16/the-model-didnt-get-worse-the-room-did-zh.html
tags: [methodology, evaluation, attribution, systems]
---

Someone put a capable model through a widely used general-purpose agent framework and came away unimpressed. It felt weaker than its published numbers promised. The obvious conclusion floated up on its own: the benchmark was generous, the model is overrated, the marketing outran the reality.

Then I looked at how the published number had actually been produced. It came from a stripped-down harness: a one-line system prompt, two tools, no injected runtime context, no summary compaction. The general-purpose framework the disappointed user ran it through was the opposite — a large system prompt, dozens of tool schemas, session context spliced in, a compaction layer folding old turns into summaries. Same weights. Completely different room.

Nobody had changed the model. They had changed everything around it, and then read the change as a fact about the model.

## A score is a joint property

Here's the thing I keep having to relearn: when you evaluate a component embedded in a system, the number you get out is not a measurement of the component. It's a measurement of the *pair* — the component plus the scaffold it's sitting inside, plus the inputs that scaffold shapes and feeds it. Move the component into a different scaffold and you are measuring a different pair. You should fully expect a different number, and you have no license to attribute the difference to the component.

The mechanism, in this case, is concrete and not mysterious. A model behaves best on inputs that look like the ones it was tuned and evaluated on. The lean harness produced inputs close to that distribution: short instruction, few tools, clean context. The heavy framework produced inputs far from it: a wall of instructions, a forest of tool schemas, injected history the model never asked for. The model didn't get dumber. It got fed a kind of input it had less practice with, and it performed like anything performs off its home turf — worse, and not because of what it is, because of where it was standing.

So the published number was real. The disappointing number was also real. They were just numbers about two different rooms, and comparing them as if they described the same object is a category error.

## Why the wrong attribution is the default

The pull toward blaming the component is strong, and it's worth naming why. The component is the thing with a name. It's the noun in the sentence. The scaffold is ambient, boring, invisible — it feels like "the environment," like neutral air the model breathes rather than an active ingredient in the result. So when the result changes, the mind reaches for the labeled object and pins the change there. The model has a version number and a marketing page; the harness is just "how we happened to run it." One of those is easy to blame. The other doesn't even register as a variable.

But the harness *is* a variable, often the dominant one. The set of tools, the length and content of the system prompt, whether context gets injected, how compaction rewrites history — these aren't neutral packaging. They are the input distribution. They decide what the model actually sees, and what it sees decides what it does. Treating that as fixed background while you vary "the model" is like comparing two runners' times and forgetting that one ran uphill.

## You've met this outside the machine

Strip the specifics and the shape is everywhere.

A person who was excellent on one team becomes mediocre on another, and everyone concludes the person regressed — when what changed was the manager, the tooling, the amount of context handed over, the shape of the work. The employee is the noun; the environment is the air; so the environment escapes suspicion and the person takes the blame.

A treatment that works in the controlled conditions of a trial underdelivers in messy real-world use, and the instinct is "the treatment doesn't really work" — when the honest statement is "the treatment plus trial conditions produced that result, and we changed the conditions." A teaching method, a diet, a process that shone in one setup and stumbled in another. Same pattern each time: a joint outcome, attributed to the one part that had a name.

## The correction is about what you're allowed to conclude

The fix isn't a better metric. It's a discipline about attribution:

- **Report the scaffold with the score, always.** A number without the harness that produced it isn't interpretable — it's a rumor. "It scores X" is meaningless; "it scores X under this specific setup" is a claim you can actually reason about and reproduce.
- **When performance shifts after you move a component, suspect the interface before the component.** The thing that most obviously changed is the environment you moved it into. Look there first. The component is the same object it was five minutes ago; the room is not.
- **Don't compare two numbers produced under two different setups as though they measure the same thing.** They don't. If you want a fair comparison, hold the scaffold fixed and swap only the component — or hold the component fixed and swap only the scaffold. Change one variable, learn one thing. Change both and you've learned nothing you can attribute.
- **When something works in one place and not another, the useful question isn't "is it good?" but "what did the working environment supply that the failing one didn't?"** That question points at the actual cause. "Is it good?" points at a fight over a noun.

The model that disappointed was the same model that impressed. Nothing about it had changed between the two verdicts. What changed was the room it was asked to perform in — the instructions around it, the tools in its hands, the context poured over it — and every bit of the difference lived there, in the setup, not in the thing everyone was busy judging. The number was never describing the runner. It was describing the runner and the track together, and someone had quietly swapped the track and kept blaming the legs.
