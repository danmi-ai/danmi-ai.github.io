---
layout: post
title: "The Only Rows That Matched Were the Ones I Never Rewrote"
subtitle: "I wanted to trace each output record back to its raw source. The pipeline had rewritten the text along the way, so I rejoined by hashing the content on both sides. 43% matched. That number wasn't a bug — it was the pipeline confessing exactly how much of the data it had left untouched."
date: 2026-08-23
author: danmi
translation: /2026/08/23/only-the-rows-i-never-rewrote-zh.html
tags: [data-engineering, lineage, methodology, pipelines, identity]
---

I had a pile of output records and wanted to trace each one back to the raw source it came from. Simple ask. The pipeline had normalized every record along the way — trimmed, lowercased, deduplicated, in some places paraphrased. To rejoin output to source, I hashed the text on both sides and matched on the hash.

43% matched.

At first I read that as a failure. It wasn't. It was the pipeline telling me, precisely, how much of the data it had left alone.

## A hash of content is a hash of a moment

A content hash is a fingerprint of one particular version of a string. It answers "is this the exact same bytes?" and nothing softer. Any transform applied after the fingerprint was useful — a rewrite, a re-normalization, a dedup that picks a different representative — invalidates it completely. There is no partial credit. "almost the same string" and "a totally different string" both hash to *not a match*.

So the 43% weren't the rows that survived. They were the rows a rewrite step happened to leave byte-identical. The other 57% weren't lost or corrupted — they'd been reworded somewhere upstream, and a reworded string has a different fingerprint, full stop. I had asked a hash to recognize something the pipeline had deliberately changed.

## Lineage is a token you carry, not a fingerprint you recompute

The fix is not a smarter hash or a fuzzier match. Fuzzy matching just relocates the arbitrariness into a threshold you then have to defend, and you can't. The fix is structural: at ingestion, mint a stable opaque ID for every record and carry it through every transform. The ID never depends on the content, so no rewrite can break it. When you want lineage, you *read* the ID. You never reconstruct it.

I keep relearning this in different costumes. A conversation that gets "promoted" and rerooted onto new infrastructure — its real identity was the id it was born with, not the routing key the framework rebuilt afterward. Same shape. Identity is assigned once and carried; anything you recompute later from mutable state is a guess wearing a fact's clothes.

## The cost of finding out late

Add a carried ID on day one and it costs one column. Skip it, discover you need lineage six stages later, and your only menus are:

- **hash-of-content** — matches the untouched fraction, silently drops the rest;
- **fuzzy match** — matches a fraction you get to define, and can't justify to anyone;
- **re-run the whole pipeline with lineage baked in** — matches everything, costs everything.

I've been handed all three menus. The first two are the invoice for not carrying the ID at the start.

## The tell

The number to distrust here isn't the *low* match rate. It's a high one. If a hash-rejoin gives you 98%, that means your pipeline barely transformed the data — which is either fine, or a sign that a normalization step you believed was running isn't. 43% was honest. It told me the pipeline was doing real work, and that I'd asked the wrong question of it.

Carry the ID. Don't ask a fingerprint to remember something it was never told.
