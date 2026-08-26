---
layout: post
title: "It Was Already Fluent"
subtitle: "I wanted a model to transform text by editing it. I could ask in a tidy little schema of my own invention, or in the exact format it had already seen millions of times. Same task, two dialects. The one I made up kept slipping — half-following, then drifting back to just writing more text. The one it already knew barely missed. The interface was the intervention, and I'd almost spent it on the wrong side."
date: 2026-08-27
author: danmi
translation: /2026/08/27/it-was-already-fluent-zh.html
tags: [agents, methodology, tool-use, interfaces, evaluation]
---

I wanted a model to change a piece of text by editing it — take the thing, rewrite parts of it, hand back a cleaner version. Not compose something new. Surgery, not writing.

There were two ways to ask.

The first was to invent a format. A compact little schema: a tag for "here is the span to replace," a tag for "here is what to put there," some structure to keep it parseable. My language, designed for exactly this job. Clean on paper.

The second was to ask in the format the model had already seen millions of times. The way editing tools issue changes — find this, replace with that, apply to the file. Nothing I designed. A surface the model had lived inside during training, over and over, until it was reflex.

Same task. Two dialects.

The one I invented mostly worked. But it kept slipping. Sometimes it half-honored the tags and half-ignored them. Sometimes — this is the tell — it stopped editing and just started *writing*, continuing the text as if it had forgotten the job was surgery. Under any pressure, it reverted to the thing it had done most: produce more prose.

The native format barely missed. It didn't drift. It didn't continue. It did the edit and stopped.

## The choice wasn't whether it could

Here's what took me a beat to see. The model already knew how to do the thing. Both times. The capability was never in question. What I was actually choosing was not *can it edit* but *which language do I ask in*.

And when I asked in a language it had never spoken, I wasn't unlocking an ability. I was teaching an ability it already had — in an accent that guaranteed mistakes. Every token of my invented schema was a small demand to relearn, in a dialect, something already fluent in the mother tongue.

The relearning leaks. That's the part worth remembering. A model asked to operate in an unfamiliar format doesn't just make random errors. It fails *toward its training* — it forgets which mode it's in and reverts to its most-practiced behavior. For a language model under a novel format, the most-practiced behavior is: keep writing. So the failure isn't noise. It's gravity, pulling the model back toward the thing it does by default.

## The interface is a lever, and we forget it

We spend enormous effort on the model and the objective. Bigger base, better reward, more data. The surface of the ask — the interface, the action space, the exact shape of the request — gets treated as plumbing. Decide it once, move on to the real work.

But the surface is one of the biggest levers there is, and it's nearly free when you get it right. A capability expressed in the distribution the model already inhabits arrives almost for nothing. The same capability, expressed in a dialect you invented, has to be relearned — and pays the relearning tax on every call, forever, in drift you'll spend the rest of the project chasing.

The custom schema *felt* like the serious engineering choice. It was legible, minimal, mine. The native format felt like cheating — I hadn't designed anything, I'd just borrowed the model's own habit. But cheap and reliable beat clean and slipping, and it wasn't close.

## The rule I took away

Before inventing a format for a task, ask what format the model already fluently produces for something shaped like this. Then borrow it. The cheapest capability is the one you don't have to teach — you just have to *address correctly*.

And there's a clean way to check whether the interface was the intervention. Hold everything else fixed — same model, same data, same objective — and swap only the dialect. If the native surface wins big while nothing else changed, you've found where the leverage actually was. It wasn't in the model. It was in which language you asked.

I almost spent that leverage on the side that made me look busier. The model was already fluent. I just had to stop making it translate.
