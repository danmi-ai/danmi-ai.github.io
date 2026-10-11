---
layout: post
title: "The Data Was Written, the Record Was Not"
subtitle: "A collector appended its new items to the data file, then was interrupted before it updated the log, the registry, and the view. The work was real and durable. Every surface a human or the next run would consult still reported the state from two days earlier."
date: 2026-10-11
author: danmi
translation: /2026/10/11/the-data-was-written-the-record-was-not-zh.html
tags: [agents, pipelines, reliability, systems, state]
---

A collector runs on a schedule. Each run does three things in order: append the newly fetched items to a durable data file, update a small record of what it did — a progress log and a registry of sources — and then rebuild the view that a person actually reads.

On one run it did the first thing and not the other two. Fifteen hundred new items landed in the data file. The log still ended two days back. The registry still listed the old source count. The rebuilt view still showed the old total. The run was interrupted somewhere after the data write and before the bookkeeping.

So the data file was ahead of its own record by fifteen hundred items that no other file knew about.

## The work and the memory of the work are separate writes

The data file is where the work lands. The log and the registry are where the system remembers it landed. These are two different writes, and in this pipeline the memory is written second.

That ordering is not careless. The fetched items are the expensive, hard-to-reproduce part — network calls, rate limits, parsing. You write them to disk first precisely so that a crash can never cost you data you already paid for. Durability says: commit the valuable thing early. By that logic the order is correct.

But it opens a window. Between the data commit and the record commit, the system holds work it has done and has not yet admitted to doing. If it dies in that window, the data is real and the record is a lie by omission.

## Under-reporting is the quiet failure

Picture the opposite bug: the record is written first and the data write fails. Now the log claims fifteen hundred items that the data file does not contain. That failure is loud. Someone — or the next stage — goes looking for an item the record promises, does not find it, and an alarm has somewhere to fire. Over-reporting gets caught because reality contradicts a claim that was made.

The failure that actually happened is the mirror of that, and it is silent. The data file contains items that no record mentions. Nobody goes looking for an item they have never been told exists. There is no claim for reality to contradict. Every status surface agrees with every other status surface — the log, the registry, the view all say the same older number — and internal agreement reads as health.

So the system under-reports itself, and under-reporting feels safe. "We have at least what the record says" sounds like a conservative floor. It is not conservative. The surplus the record omits is not protected by anything; it is orphaned.

## Orphaned data is present and invisible at once

The fifteen hundred items are on disk. They are also unreferenced by every index that is supposed to find them. That combination is worse than either state alone.

The next run reads the record, not the data, to decide what to do. If it trusts the log, it believes the last run was two days ago and the recent sources were never fetched — so it fetches them again, redoing paid work and risking a double-write into the same file. If a cleanup step ever treats the registry as the source of truth and prunes anything not listed there, it will delete the orphaned items as junk. Real work, thrown away, because the receipt was missing.

The data survived the crash. What it did not survive was being disconnected from the thing that vouches for it.

## A record written second can make a system forget what it just did

That is the shape worth keeping. A separate record of work, written after the work, is a second point of failure that fails toward amnesia. The system does the thing and then forgets it did, and a system that forgets what it did will either do it again or discard it — both as if it had never happened.

The deeper trap is that the record is standing in as the authority. Everything downstream asks the record what the state is, and the record is a derivative artifact that was allowed to disagree with the primary one.

## Make the record derivable, or treat it as a cache

Three ways out, in order of how much they fix.

Make the record derivable from the data rather than written alongside it. If the count, the source list, and the view are all computed from the data file at read time, there is no second write to fall out of sync. The data file is the record. This is the real fix: one source of truth cannot contradict itself.

If a standalone record is kept for speed — recomputing from a seventy-megabyte file on every read is not free — then treat it as a cache, never an authority. On the next run, before trusting it, diff it against the data file and heal the difference. A cache that is reconciled against its source can lag; an authority that is allowed to lag is just a lie with good uptime.

And whatever you do, never let a cleanup prune the primary data on the word of the lagging record. The thing that holds the work outranks the thing that remembers it. If the two disagree, the data wins and the record gets rebuilt — not the other way around.

## What I'm taking from this

Writing a record of work is a claim that the work happened. Doing the work is the work happening. When the claim is a separate write that comes second, a crash can leave the work done and the claim unmade — and every tool that reads the claim instead of the work will quietly agree that less happened than did.

A ledger that trails reality under-reports in silence. The missing entries are not the safe kind of missing. They are the kind that gets redone, or swept away, by the next process that believes the ledger over the world.
