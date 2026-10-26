---
layout: post
title: "The Number Was Invented, and It Matched a Real One"
subtitle: "I handed a generator a set of verified figures as approved facts, then asked it to add a few illustrative numbers for a diagram. It produced a toy value that happened to be identical to one of the real statistics, and it wasn't marked as a toy. To any reader, a number I'd made up read as a cited fact — and the reason it collided wasn't bad luck. I'd caused it."
date: 2026-10-27
author: danmi
translation: /2026/10/27/the-number-was-invented-and-it-matched-a-real-one-zh.html
tags: [hallucination, generative-content, prompting, verification, llm, failure-modes, engineering]
---

I was building an explainer artifact from a source I'd read carefully. Before generating anything, I did the responsible thing: I pulled out the real figures that mattered, checked them against the source, and handed that set to the generator as *approved facts* — these are true, use them, don't change them. Then, in the same instruction, I asked for a few illustrative numbers to decorate a diagram. Toy values. Not claims. Just something to make the picture concrete.

The output put a number in the opening frame that was numerically identical to one of the real statistics — and it carried no label saying it was illustrative. A reader has no way to tell the difference between a figure I verified against a source and a figure I pulled out of the air. Both are just digits on a surface. The one I'd invented was sitting exactly where a cited fact would sit, wearing the same clothes. I'd generated a hallucination that looked like scholarship, and the mechanism that produced it was one I'd built myself three sentences earlier.

<!--more-->

## A fake number that matches a real one is worse than an obvious fake

If a generator invents a wild, obviously-wrong value — a percentage over 100, a date in the wrong century — the error announces itself. It fails loudly, a reviewer catches it, nobody is misled. The dangerous invention is the plausible one: a value in the right range, formatted like the real ones, placed where a real one belongs. And the most dangerous version of *that* is the invention that happens to equal an actual figure from the source. At that point the number is indistinguishable from a citation, because it *is* the citation's value — just arrived by the wrong road, carrying none of the checking that the real one carried.

This is the part worth sitting with. The harm isn't the wrongness of the number. The number is "right" in the sense that it matches something true. The harm is the **false provenance**: a reader will treat it as supported by the source, trace nothing, and build on it. An unverified value that coincidentally lands on a true one has laundered itself. It looks like it went through verification. It didn't. And the collision is precisely what erases the seam.

## Credibility is contagious in a mixed artifact

The deeper leak is structural. Any artifact that interleaves *verified* content and *generated* content — a report with real citations and invented examples, a slide with true headline numbers and a toy chart, a summary that quotes accurately and paraphrases loosely — lets the generated parts borrow the authority of the trusted parts. A reader doesn't audit each sentence for its origin. They form one impression of the whole thing's reliability from the parts that are visibly solid, and then extend that impression to everything sitting next to it. Trust spreads by adjacency.

So the invented numbers in my diagram weren't being read as "the model's guesses." They were being read as part of the same careful document that contained the real figures, because they were in the same careful document. Putting verified and generated material in one surface doesn't average their credibility. It levels it up — the weakest content inherits the trust earned by the strongest. If you want generated filler to read as filler, the artifact has to *mark the seam*, because the default behavior of a mixed surface is to hide it.

## I caused the collision — the priming was self-inflicted

Here's the turn that changed how I think about this. The collision wasn't random. I made it likely.

By feeding the model my verified numbers as "approved facts," I put those exact values into the most salient part of its context — the instructions, repeated, emphasized, framed as the things that matter. Then I asked it to produce an illustrative value. Where does a generator reach when it needs a plausible number? Toward whatever numbers are most available to it. I had just spent a paragraph making a specific set of numbers maximally available. The "random" toy value wasn't random at all; it was an echo of the real data I'd primed it with. I handed it the answer key and then asked it to make something up, and it made up the answer key.

This inverts the usual intuition about grounding. We give models real facts to *reduce* hallucination, and for claims that's correct. But the same priming that anchors a claim also contaminates the invention: any value the model is now asked to fabricate is drawn from a well I just filled with real numbers. Grounding a model's *facts* and asking it to *invent* in the same breath are in tension. The facts I provided to keep it honest were the exact material it reached for when I asked it to be fictional.

## "Label the illustrative ones" is not enough

The obvious fix is to tell the generator: mark anything illustrative as illustrative. I did add that, and it helped — most toy values came out tagged. But one didn't, and the one that slipped through was the one that collided, which is the worst possible one to miss. A rule that works "most of the time" is no defense for a failure whose entire danger is that it looks correct. You can't rely on the model to label the exact case it's least equipped to recognize as needing a label.

The real fix is structural, not a plea. Invented values must be **provably distinct** from real ones — drawn from a visibly different range, or a reserved placeholder form (the round, obviously-synthetic `100`, the blatant `X`), or explicitly forbidden from equaling any approved fact. The constraint I added afterward was blunt and effective: *no invented number may be equal to any of the real numbers.* That turns a collision from a thing I hope doesn't happen into a thing the output cannot contain. Don't ask the model to remember to flag the trap. Remove the trap from the space of possible outputs.

## What I'm taking from this

First: in a pipeline that mixes trusted and generated content, the generated content is only as safe as its *most authoritative-looking* instance, not its average one. I have to assume filler will be read as fact, because adjacency makes it so, and design the artifact to mark its own seams rather than hoping the reader finds them.

Second: grounding and invention don't coexist cleanly in one prompt. The real values I provide to keep claims honest are the same values the model will reach for when I ask it to fabricate. If an artifact needs both verified facts and invented illustration, the invention has to be fenced off — different range, reserved form, explicit inequality to the real set — so the priming I use for accuracy can't leak into the fiction.

And third, the one I'll keep: a made-up number that matches a true one is not a lucky near-miss. It's the most expensive error in the set, because it's the one that passes review by looking exactly like the thing it isn't. The goal was never to make my inventions *plausible*. It was to make them unmistakable — impossible to confuse with the facts they sit beside. Plausibility, for a placeholder, is the bug.
