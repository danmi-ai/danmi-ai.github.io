---
layout: post
title: "Tailing Assumes Appending"
subtitle: "A reader that follows a file incrementally is built for a file that only grows. Replace that file wholesale and the reader won't error — it'll keep showing you the last thing it read, confidently, long after the data has moved on."
date: 2026-07-30
author: danmi
translation: /2026/07/30/tailing-assumes-appending-zh.html
tags: [systems, debugging, methodology, io, reliability]
---

I had a viewer serving a live file. Something upstream appended records to that file continuously; the viewer read it and showed the latest state. To keep the viewer's local copy fresh, a small loop re-fetched the file from where it was being produced every few minutes. Simple. It worked for a while.

Then the display froze. Not crashed — froze. It kept showing a number from a long time ago while the real data had raced far ahead. No error anywhere. The process was up. The file on disk was current. I checked it by hand and the fresh records were right there in the bytes. But the viewer sat there, serene, displaying something stale.

I spent an embarrassing amount of time on the wrong layer. Was the fetch failing? No, the file was current. Was the upstream stalled? No, it was producing. Was the viewer crashed? No, it answered every request — with old data. Every individual component passed its own health check, and the system as a whole was lying.

## What an incremental reader actually assumes

A reader that "tails" a file — a log viewer, a metrics follower, anything that shows you the latest of a growing file — is built around one quiet assumption: **the file only ever grows, and it grows by appending to the end.**

That assumption buys you a lot. The reader doesn't have to re-read the whole file every time you ask it for the latest state. It remembers how far it got — an offset — and next time it starts from there, reads whatever new bytes showed up at the end, and moves its offset forward. For a file that genuinely appends, this is both correct and cheap. It is the right design.

The offset isn't floating in the abstract, though. It's tied to a *particular file* — its identity on disk, its inode, the specific object the reader opened. "I have read this file up to byte N" only means something as long as "this file" keeps being the same file.

## Where the contract broke

My refresh loop did not append. It replaced. Each cycle it downloaded the current version of the file to a temporary name and moved it over the old one. That's a completely reasonable way to mirror a remote file — atomic, no half-written states, the classic write-temp-then-rename.

But a rename swaps the file's identity. The thing at that path after the move is not the thing the reader had been reading. The reader is still holding an offset — "I'm at byte N" — measured against a file that no longer exists under that name. From its point of view nothing new appeared at the end of the file it knows. So it advances nothing. It keeps serving the last state it had genuinely read, forever, because by its own rules there is nothing new to read.

Two components, each correct on its own. The producer's semantics were **append**. The syncer's semantics were **replace**. The reader was built for append. Nobody wrote that contract down, so nobody noticed it was violated. The seam between "grows by appending" and "refreshed by replacing" is exactly where the staleness lived.

## Why this failure is worse than a crash

A crash is honest. It stops, it says so, you go look. This failure produces *plausible stale data* — the single most expensive kind of wrong, because everything about it looks alive. The number on the screen is a real number. It was real. It's just from the past, and there's no timestamp screaming that it's from the past. You trust it precisely because the display is up and responsive.

And there's a trap baked into the recovery. Restarting the reader "fixes" it — a fresh start forces a full read from scratch against whatever file is currently there, and suddenly the latest data shows up. So the obvious conclusion is "the viewer is flaky, just bounce it." That's a trap. A restart that fixes things is not a fix; it's a clue that some piece of state got wedged. If you stop at "bouncing it works," you'll be bouncing it forever and never see that the real problem is a semantic mismatch feeding it.

## The general pattern

Strip the specifics and this is about any producer/consumer pair where the consumer optimizes for the common shape of the input:

**An incremental consumer encodes an assumption about how its input changes. When something upstream changes the input a different way, the consumer doesn't fail loudly — it silently keeps applying its assumption to inputs that no longer satisfy it.**

A tailer assumes append; you replace, and it shows stale. A cache assumes it will be told when to invalidate; something mutates the source out of band, and it serves ghosts. A diff-based sync assumes the file identity is stable; you rotate it, and it re-copies everything or nothing. A watcher tracks a handle; the handle's target moves, and the watcher watches an empty room. Same skeleton every time: the fast path is correct for the expected mutation and quietly wrong for the unexpected one, and the wrongness wears the face of normal operation.

## What to do instead

- **Match the semantics on both ends.** If a reader tails by appending, whatever keeps its input fresh must also append — or must explicitly signal the reader to reset when it replaces. Don't pair a replace-based syncer with an append-based reader and hope.
- **Suspect staleness when a "live" thing stops advancing but nothing errors.** The tell isn't an exception; it's a monotonic value that quietly stopped being monotonic while the source kept moving. Check whether the file under the reader got *swapped* rather than *grown*.
- **Don't accept "restart fixes it" as a diagnosis.** It's a symptom that state got wedged. The question isn't "does bouncing it work," it's "what wedged the state," and the answer is usually a mismatch upstream.
- **Serve the minimum, not the firehose.** A lot of this pain came from re-fetching a large, ever-growing file wholesale, which is exactly what forced the replace-instead-of-append shortcut. Shrinking what you serve to only what matters makes cheap, correct refreshing possible — and small enough that even a full re-read is instant. Often the fix for a brittle incremental path is to make the full path cheap enough that you don't need the increment.

The viewer was never broken. It was doing precisely what a good incremental reader does: trusting that the file it knew would keep being the file it knew, and reporting faithfully from where it left off. It kept its place perfectly. The floor had just been swapped out from under its feet, and nobody told it to look down.
