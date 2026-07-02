---
layout: post
title: "Open Weights Are Not Open Training"
subtitle: "A model can be 'open source' and still hide the only part that would let you rebuild it"
date: 2026-07-03
author: danmi
tags: [open-source, machine-learning, reproducibility, ml-engineering, methodology]
---

I spent a day mapping how open a batch of "open source" large models actually are, and the exercise kept collapsing the word *open* into things that turned out to be very different. By the end I had stopped asking "is this model open?" and started asking a sharper question: **open at which point in its life?**

The distinction matters more than the label, and most of the public conversation flattens it.

## The endpoint fallacy

Here is the shape of the mistake. Someone releases a set of weights, adds a permissive license, publishes a decent technical report, and everyone files it under "open." Fair enough — you can download it, run it, fine-tune it. But a trained model is the *last frame* of a very long movie. What got released is an endpoint. The endpoint is useful. It is not the thing that would let you reproduce, audit, or genuinely learn from the work.

Think about what a training run actually produces over time:

- **Data** — the corpus, the mixture ratios, the filtering rules, the decontamination.
- **Code** — the training framework, the optimizer, the schedule, the loss.
- **Trajectory** — the intermediate checkpoints, the loss curves, the point where they switched stages.
- **Endpoints** — the base model and the final aligned model.

Almost everyone releases the endpoints. Very few release the trajectory. Fewer still release the data and code that would let you *regenerate* the trajectory. So "open" fractures into a ladder, and the rung most people stand on is the lowest one that still earns the label.

## Having a stage is not releasing the stage

The trap I actually fell into, twice, was conflating two different sentences:

1. "This model was trained with a mid-training stage."
2. "This model released its mid-training weights."

These read almost identically and mean nothing alike. The first is a claim about *methodology* — somewhere between pretraining and alignment, there was a distinct phase (call it mid-training, annealing, a reasoning stage; the naming is a mess and everyone picks their own word). The second is a claim about *artifacts* — that the checkpoint at the end of that phase is something you can download.

Nearly every serious model now has some form of intermediate stage. The report will describe it, sometimes in detail. That is the methodology being open, in the sense that they told you it happened. It is emphatically not the checkpoint being open. When I first read the reports I let the word "mid-training" in the paper stand in for "mid-training weights on the hub," and I was wrong. You have to go check the actual release, file by file, because the paper describing a stage and the repository containing that stage's weights are two independent facts.

The gap between them is enormous in practice. A described stage lets you *understand* the recipe. A released checkpoint lets you *branch* from it — start your own experiment from the point just before alignment, or study exactly what the base model knew before it was tuned. One is a diagram. The other is a fork point.

## Why the trajectory is the expensive part to give away

If the endpoints are cheap to release and useful to receive, why does almost nobody release the trajectory?

Because the trajectory is where the actual competitive information lives. The final weights tell you *what* the model became. The intermediate checkpoints, the data mixture, and the training code tell you *how* — and "how" is the thing that took a year and a large budget to figure out. A base model is a capability you can rent. A training pipeline is a capability you can *rebuild*. Companies are, understandably, far more willing to hand you the former than the latter.

There is also a size asymmetry that shows up once you look closely: the more flagship a model is, the *less* likely even the base checkpoint appears. Smaller models get their base weights released; the biggest ones often ship only the aligned final. The reasoning is obvious once stated — the base of your best model is the closest thing to a blueprint, and blueprints are the last thing anyone gives up.

## The one team that gives up the whole movie

The reason this whole taxonomy is worth writing down is that the ceiling exists and it's public. There are model families that release the *entire trajectory* — intermediate checkpoints stored as separate branches, sometimes hundreds or thousands of them, one per training step region, plus the data, plus the code. From those you can reconstruct almost the full arc of training and ask questions like "when did this capability actually emerge?" against real checkpoints instead of hand-waving.

That is what fully open training looks like, and it's rare enough that when you find it, it stands out against everyone else by a wide margin. Most releases that call themselves open are, on this ladder, several rungs down. That's not an accusation — releasing usable weights under a good license is a real contribution. It's just a reminder that the word is doing a lot of quiet work, and the interesting differences all live below the label.

## The rule I'm keeping

When someone tells me a model is open source, I now ask three follow-ups before I believe the word means what I want it to mean:

1. **Open at which point?** Final only, or base too, or the intermediate trajectory?
2. **Described or released?** Does the report *mention* the stage, or can I *download* the checkpoint from it?
3. **Weights only, or the means to regenerate them?** Data and code, or just the artifact?

The answers usually place a model two or three rungs lower than its press release implies. That's fine. The point isn't to be cynical about openness — it's to stop letting one word stand in for a whole ladder, and to know which rung you're actually standing on before you plan work that assumes you can climb higher.

An endpoint lets you use a model. A trajectory lets you understand one. Only a handful of releases give you the second, and knowing the difference is the difference between "I have the weights" and "I could have built this."
