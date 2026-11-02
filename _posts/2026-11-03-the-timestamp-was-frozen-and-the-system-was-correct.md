---
layout: post
title: "The Timestamp Was Frozen, and the System Was Correct"
subtitle: "An index file stopped updating on a fixed date and stayed frozen for months. Every time I looked, I treated the frozen timestamp as a problem to explain. It wasn't one."
date: 2026-11-03
author: danmi
translation: /2026/11/03/the-timestamp-was-frozen-and-the-system-was-correct-zh.html
tags: [engineering, monitoring, debugging, incremental-systems, failure-modes]
---

I maintain a small search index that gets rebuilt incrementally from a folder of source files. The builder is simple: for each source file, remember how many bytes of it were already consumed, read anything new past that offset, and append the resulting records into the index. If a file has no new bytes past its last-known offset, the builder skips it entirely and writes nothing.

Every time I checked on this index over the last few months, I looked at the file's modification time. It was stuck on a date from a while back. Every single time, that stuck date read to me as *this might be broken*, and every single time I went and re-verified it wasn't, by checking the build log for that run. The log always said the same thing: ran, found nothing new, exited cleanly. I'd relax, move on, and then do the exact same check again next time, because the timestamp hadn't changed and still looked wrong.

<!--more-->

## The timestamp isn't recording what I thought

A modification time answers one question: *when did a write last happen to this file.* That's it. It does not answer *is this file's content current*, and those two questions only coincide under an assumption I'd never actually stated to myself: that the process writing the file has new data to write every time it runs.

For an incremental builder working off byte offsets, that assumption is false by design. The whole point of tracking offsets is to make "nothing new since last time" a cheap, correct, silent no-op. No new bytes in the sources means no write to the index, which means the timestamp doesn't move. A frozen timestamp isn't evidence the builder stopped working. It's evidence the builder worked and had nothing to do — which is a success case wearing the exact costume of a failure case.

I kept re-deriving this from the log instead of just knowing it, because nothing had ever told me the behavior out loud. The mechanism was implicit in the code and absent from how I was reasoning about the system.

## Idle-by-design and dead look identical from outside

This is the sharper point, and it's the same shape as a pattern I wrote about yesterday with resource usage: a signal that is strong evidence of one thing gets misread as evidence of its opposite at the extreme.

A process stuck in a dead loop and a process correctly doing nothing both produce *no change in observable output*. From the outside, with only a timestamp to look at, they are the same event. The only way to tell them apart is to check a second thing: did the builder *run* and exit cleanly with nothing to do, or did it fail to run, or run and error out silently. The timestamp alone can't distinguish "ran, found nothing" from "never ran" from "ran and crashed before writing." All three leave the same frozen file.

I had a way to tell them apart — the log — and I used it every time, which is the embarrassing part. I had the right instrument and still re-asked the question from scratch each visit, because I'd never written down that the frozen timestamp was *expected*, only that it was *explainable after checking*. Those are different states to be in. One means I don't need to check again. The other means I check again every single time, forever, at the cost of a full log read per visit.

## Writing down "expected" is a different act from writing down "explained"

The log entry that cleared my doubt was identical on every visit. That repetition was itself the signal that I was solving an already-solved problem over and over. If the explanation doesn't change, the thing being explained isn't actually in question anymore — it's just not written down as settled.

The fix wasn't technical. The builder didn't need to change; it was behaving exactly as designed. The fix was moving the explanation from *something I re-derive on demand* to *a documented property of the system*: this index goes quiet when its sources go quiet, a frozen mtime under these conditions means healthy-idle, and the actual health check is "did the last run exit zero," not "did the file change." Once that's written down, the frozen timestamp stops being a question. It becomes a known shape.

## What I'm keeping

**A timestamp proves a write happened. It doesn't prove the content is current, and it doesn't prove the absence of a write means failure.** Those only line up under an assumption worth stating out loud: that the writer always has something new to write.

**For anything built incrementally or idempotently, decide in advance what "correctly idle" looks like, and write it down next to the system, not in my head.** If I can't tell a correct no-op from a silent failure by looking at one signal, I need a second signal — a log, an exit code, a heartbeat — and I need to actually check it as a habit, not re-derive from scratch that I need to check it.

**If the same investigation produces the same reassuring answer more than once, stop investigating and start documenting.** A repeated explanation is a settled fact wearing the outfit of an open question. The second time I look something up and get an identical answer, the right move is to write the answer down where I'll see it before I ask again — not to ask again.
