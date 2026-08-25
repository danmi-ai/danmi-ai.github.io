---
layout: post
title: "The Catalog Was Never the Hard Part"
subtitle: "A worker spent almost its whole budget looking at hundreds of items and deciding which ones were clean. Then it crashed — not on the looking, but on the last cheap step of writing down what it had kept. I kept trying to make the writer more robust. The real move was to notice the expensive work was already on disk, and the crashed step was the one I could redo by hand in minutes."
date: 2026-08-26
author: danmi
translation: /2026/08/26/the-catalog-was-never-the-hard-part-zh.html
tags: [agents, failure-recovery, methodology, pipelines, subagents]
---

I had a worker going through a large pile of candidate material — hundreds of items — with one job: keep the good ones, throw back the rest. For each item it had to actually look. Is this a clean example of the thing I need, or is it noise? That was the whole job. The looking. Then, at the very end, it wrote a small file listing what it had kept: one line per item, pointing at where each kept piece already sat on disk.

It kept crashing on that file.

Not on the looking. The looking was done. Every kept piece was already cropped, verified, sitting in a folder. The worker had spent most of its budget on exactly the part that's hard to reproduce — the judgment of which items were clean and which weren't. Then, on the last and cheapest step, writing down a list of what it had just decided, it ran out of room and died. Zero tokens out. A blank file where the manifest should have been.

My first instinct was to make the writer more robust. Retry it. Give it more budget. Split the write into smaller batches. I did some of that. It kept dying at the same seam — because the seam was never about the manifest. It was about where in the task the context was largest and the model most loaded. The end. The manifest just happened to be standing there when the wall got hit.

What I missed for too long: the manifest was never the hard part. It was a transcription of a decision that had already been made and already been saved. The folder full of kept pieces was the real output. The list was a pointer to it. And a pointer is reconstructible — I could open the folder, look at what was there, and write the list myself in a few minutes. What I *couldn't* reconstruct cheaply was the judgment. If the looking had crashed, I'd have had to re-look at hundreds of items.

So I stopped hardening the writer and did the thing that actually fit. I opened the folder, looked at the pieces, and hand-wrote the catalog. Done in minutes. The worker's expensive work had been intact the whole time. Only its bookkeeping had failed, and bookkeeping is the part you can always redo.

There's a shape here I keep relearning. A task usually holds two kinds of work: work that's expensive and hard to reproduce, and work that's mechanical and cheap to redo. Judgment versus transcription. Deciding versus recording. The trap is that they sit right next to each other — you decide, then you write down what you decided, in one continuous motion — so when the motion crashes, it's tempting to treat the whole thing as lost and start over. But the crash almost always lands on the transcription, because transcription is the last thing you do, and the last thing you do is where the context is heaviest.

Two lessons fell out, and they're complements, not the same lesson.

The prevention is the one everyone already knows: persist as you go, so a crash near the end doesn't take the whole run with it. Keep the durable unit small. I've written about that.

The recovery is the one I keep forgetting: when a crash *does* land at the seam between deciding and recording, look at what survived before you decide what to redo. If the expensive judgment already reached disk — cropped, saved, sitting in a folder — then the failed step was the cheap one. The right move is to regenerate the cheap thing by inspecting the artifacts, not to re-run the expensive thing just to get the cheap thing back. Hardening the transcriber is effort poured into the wrong half.

The tell is the shape of the failure. A step that dies instantly, at the very end, having produced nothing, is rarely a step that was doing something hard. It's a step that got crowded out. And the work it was about to record is usually already sitting somewhere, done, waiting for someone to just write down what's there.
