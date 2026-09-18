---
layout: post
title: "The Switch Was Off, the Pipeline Was On"
subtitle: "A tool quietly shipped copies of your work to a server, and the company called it a feature. The interesting part wasn't the intent behind it — it was that you could classify the thing correctly without ever knowing the intent, just by looking at how it behaved."
date: 2026-09-19
author: danmi
translation: /2026/09/19/the-switch-was-off-the-pipeline-was-on-zh.html
tags: [methodology, ethics, systems, privacy, trust]
---

A while back people noticed that a coding tool was doing something in the background: after you logged in, it would periodically package up your project and send an encrypted copy to a cloud bucket. Not once. Dozens of times a session. The company's explanation, when it came, was that this powered a nice feature — the tool builds an index of your repo so it can answer questions about it, generate a wiki, be smart about your code. A feature. A side effect of a feature, really.

I want to set aside whether the intent was benign, because I think the intent is a distraction, and the reason it's a distraction is the useful part.

## Two things that look identical from the outside

There is a feature that happens to send some data. And there is a data-exfiltration pipeline that happens to also produce a feature. From a marketing page these are the same sentence. From the user's chair they feel the same — you clicked install, something got smarter, some bytes went somewhere. The words "we index your repo to help you" describe both of them perfectly.

So the story can't tell them apart. The story is compatible with either. If you try to classify the thing by the narrative attached to it, you will classify it however the narrator wants, because the narrator picked the narrative *after* building the thing, to fit the thing.

What tells them apart is operational shape. Not what it's *for* — what it *does*, mechanically, when nobody is framing it.

## What the shape said

A few features of the behavior did the classifying on their own.

It was default-on. You didn't turn it on; it was on, and you'd have had to know to turn it off.

The off switches didn't switch it off. There were toggles in the UI with names like "improve my experience" and "index my repo," and flipping them did not stop the capture-and-upload loop. That's the one that matters most, and I'll come back to it.

The frequency was wildly past what the stated feature needs. If the point is to build an index of your repo, you build it, and you rebuild it when the repo changes. You do not need to snapshot and ship the whole thing sixty times in one working session. A feature has a frequency that matches its function. This frequency matched a different function.

None of those three facts is about intent. All three are observable from the outside, in an afternoon, with a proxy and some patience. And all three point the same direction — away from "feature that sends data" and toward "pipeline that also has a feature bolted on the front for the pitch."

## The off switch is the whole tell

Of everything, the switch that doesn't switch is the one I'd teach.

A default-on data collector with a working off switch is a defensible design. Aggressive, maybe rude, but defensible: the user can inspect it, understand it, and stop it, and the stopping is real. The system is honest about the boundary of your consent even if it starts on the wrong side of it.

A default-on data collector with an off switch *that doesn't stop the collection* is a different animal, and the difference is not degree, it's kind. The switch exists to make you feel like the boundary is yours. It renders the appearance of consent while the pipeline ignores it. That's not a stronger version of the first thing. It's the thing that first thing pretends not to be. The presence of a decoy control is more damning than no control at all, because no control is just aggressive, while a decoy control is aggressive *and* knows you'd object.

So: when you're trying to decide whether a system respects a boundary, don't read its promise about the boundary. Toggle the boundary and watch the bytes. A control you can't verify is a control that isn't there, and a control that's there but inert is worse than one that's absent.

## The unverifiable reassurance

There was also a reassurance that made this concrete: the uploaded copy, they said, is used to generate the index and then immediately destroyed — never stored.

Maybe. But notice you cannot check that, and you cannot check it *by construction*. The data is encrypted on your machine to a key that lives on their server. Everything after the upload happens somewhere you can't see, under a key you don't hold. "We delete it" is a claim about the inside of a box you were specifically prevented from opening. It might be true. It is not *verifiable*, and an unverifiable safety claim about your own data, made by the party holding the only key, is worth exactly its enforceability, which is zero.

This is a general tell too. When someone reassures you about what happens to your data *after* it leaves your control, the reassurance is only as good as your ability to audit it. If the design specifically removes your ability to audit it — keys on their side, processing off your machine — then the reassurance isn't a weak guarantee, it's not a guarantee. It's a feeling, priced at the cost of saying it.

## The rule I took out of it

Consent can't be inferred from feature value. "This is useful" is an argument for why you *might* have agreed, not evidence that you *did*. A thing being good for you does not convert into your permission, and a company that treats "but it's a useful feature" as a stand-in for "you opted in" has quietly swapped a question about your rights for a question about their product.

Two lines to carry out:

Classify a system by its operational shape — default state, whether the off switch actually stops it, whether its frequency matches its stated function — not by the story told about it, because the story was written to fit whatever got built.

And treat any safety claim about data you can no longer see as worth only what you can verify. If the design removed your ability to check, it also removed the claim's weight. Judge the pipeline, not the pitch.
