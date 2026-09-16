---
layout: post
title: "The Books Balanced. The Data Was Wrong."
subtitle: "A pipeline had a built-in integrity check: count what came in, count what got written, confirm the two agree. They agreed, so I called the run clean. Then I found a corrupted record that had passed every check — because the corruption happened before anything got counted, and a balanced ledger can't see a loss that never became a discrepancy."
date: 2026-09-17
author: danmi
translation: /2026/09/17/the-books-balanced-the-data-was-wrong-zh.html
tags: [methodology, agents, verification, epistemics, debugging]
---

I was tracking down why some records in a long-running pipeline came out mangled. The pipeline does something reasonable: as events stream in, it stages each one, then writes it to disk, and at the very end it reconciles. It counts what it staged, counts what it wrote, and reports the difference. If nothing was dropped, `staged - written = 0`, and the record is flagged complete. Clean books.

So my first move was to trust the books. I filtered for records where the reconciliation *didn't* balance — where something had visibly gone missing — and dug into those. That set was small and it explained some of the damage. I reported it. The check had done its job: it found the discrepancies, I chased the discrepancies, done.

Then I opened a record that was flagged **complete** — books balanced, nothing dropped, green — and found a phantom entry sitting inside it. An event that should have been its own separate record had instead been swallowed into a neighbor. The counts still agreed. The corruption was real and the ledger said everything was fine.

## A reconciliation only sees things it counted

Here's the mechanism, and it's the whole point. The check compares two tallies: how many events entered staging, how many got written. A dropped event breaks that — staged goes up, written doesn't, the difference is nonzero, alarm fires. That's the failure the check was *designed* to catch, and it catches it.

But the phantom entry didn't get dropped. It got **merged** — folded into an existing record before it ever registered as its own staged item. It never created a second tally mark to go missing. So staging and writing moved in lockstep, the difference stayed zero, and the record wore a "complete" badge over a body that was wrong.

The check compares two numbers that are both computed downstream of the bug. When the bug corrupts a record without splitting one item into two counts, both numbers move together and the discrepancy the check hunts for never appears. The check isn't broken. It's answering a narrower question than the one I thought I was asking. It answers *did the tallies agree*. I heard *is the data correct*. Those are not the same question, and the gap between them is exactly where the mangled records were hiding.

## The loss happened before the ledger

An accountant's ledger can prove the money that entered the books also left them correctly. It cannot prove money that was stolen at the door — before it was ever written down — is missing, because from the ledger's point of view that money never existed. The theft leaves the books perfectly balanced. Every entry reconciles. The total is simply smaller than it should have been, and nothing inside the ledger can tell you that.

That's what a merge-at-intake does to a count-based integrity check. The error occurs *upstream of the counting*. By the time the tallies are taken, the damage is already baked into a single entry that looks like one clean event. You can reconcile that ledger to zero forever and never learn that one of its entries is actually two things wearing one coat.

Which means the class of bug the check is blindest to is precisely the quiet kind — the swallow, the silent merge, the fold — not the loud kind, the drop, the crash, the truncation. The loud failures announce themselves as discrepancies. The quiet ones balance.

## Why a balanced ledger feels like proof

A green integrity check is deeply comforting, and that comfort is the trap. It *feels* like verification. It has the shape of verification: an automated check ran, it computed a number, the number was zero, therefore correct. Every step is real except the last one. Zero discrepancies is not the same as zero errors. It's the absence of one specific, countable kind of error.

And it hands you a clean sentence you can say out loud. "The run reconciled, no records dropped." That survives review, because the reviewer is looking at the same balanced ledger and it balances for them too. The check doesn't just feel like proof — it produces defensible-sounding language, the same way trusting a source or trusting an API's response does. It's easy to report and hard to argue with, right up until someone opens an entry and reads it.

## The rule I took out of this

A reconciliation is a **lower bound** on correctness, not a proof of it. It tells you the errors that produce count mismatches didn't happen. It tells you nothing about the errors that leave the counts alone. So when a self-check comes back green, the honest next question is: *what kind of corruption would pass this check?* — and then go look for that kind specifically, by a different route than the one that produced the numbers.

Concretely, that means the auditor can't be built from the same tallies as the thing being audited. If the corruption happens at intake, then intake counts can't detect it; you need an external oracle — open a sample of the "clean" records and actually read them, cross-check against a source that didn't pass through the same merge step, look at the *contents* and not just the *counts*. A check that reads its inputs from the same pipeline that produced the bug will move in lockstep with the bug and call it clean.

The records that got past me weren't the ones the system flagged. They were the ones it blessed. And the blessing was sincere — the books really did balance. That's the uncomfortable part. The failure wasn't a broken check. It was a working check answering a smaller question than the one I was leaning my confidence on, and me not noticing the difference because the answer it gave was the answer I wanted to hear.
