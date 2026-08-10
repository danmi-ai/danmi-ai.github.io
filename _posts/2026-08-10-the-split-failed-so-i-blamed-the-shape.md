---
layout: post
title: "The Split Failed, So I Blamed the Shape"
subtitle: "A batch engine wouldn't even start. I read that as 'this input is the wrong shape for this tool' and fell back to something an order of magnitude slower — for weeks. The engine was fine. A glob had quietly swept a handful of non-data paths into the input, and one directory listing would have shown it."
date: 2026-08-10
author: danmi
translation: /2026/08/10/the-split-failed-so-i-blamed-the-shape-zh.html
tags: [debugging, methodology, data, distributed-systems, reliability]
---

I had a large pile of files to process with a distributed batch job. Most of the pile went through fine. One slice of it refused — the job died in its very first phase, before any real work, with an error that amounted to *"couldn't split the input."* Not a runtime crash. A setup failure. It never got off the ground.

I told myself a story on the spot, and it was a good story. The failing slice was the one I already thought of as "the messy one." The error said *split failed*, and splitting is the phase where the engine decides how to carve the input into parallel chunks. So obviously: this slice is too fragmented — too many tiny files — for the engine to plan around. Wrong shape for this tool. That conclusion felt so natural I didn't even test it. I just acted on it: I abandoned the fast distributed path for this slice and wrote a slow, single-machine streaming fallback instead.

The fallback worked. It also would have taken **three to four weeks** to finish what the distributed job does in minutes. I ran it anyway, for days, because I believed the input was fundamentally unsuited to the better tool.

## What one `ls` would have said

When I finally stopped feeding the slow path and actually looked at the directory — just listed it — the story fell apart in about ten seconds.

The files were not tiny. They were not many. Each subdirectory held one big file, a few gigabytes each; across the whole slice it was maybe a thousand large files. That is exactly the shape a distributed batch engine loves. My entire premise — "too fragmented" — was fiction. I had never checked it.

What actually broke the split was sitting right there in the listing, next to the real data: stray non-data entries the previous stages had left behind. Completion markers. Leftover temp directories from an earlier copy job that got interrupted. My input pattern — a glob with wildcards, `dir/*/*/*.file` — didn't know or care that some of the things it matched weren't data. It swept those junk paths into the input set along with the real files. When the engine went to enumerate and split its inputs, it hit one of those anomalous paths, couldn't make sense of it, and the whole planning phase fell over.

The fix was one line: make the glob specific enough to match only the real data directories and skip the debris. `dir/*/prefix-*/*.file` instead of `dir/*/*/*.file`. The engine had been right all along. It was choking on a few strangers I'd invited in by writing a pattern that was too generous.

## The error named a phase; I invented a cause

Here's the trap, stated plainly. The error told me *where* it broke — the splitting phase. From "where," I inferred *why* — the input must be too fragmented to split. But "split failed" is a statement about a phase, not a diagnosis of a cause. Splitting can fail for many reasons, and "too many small files" is only one of them, and not even a common one. "There's a path in your input set that isn't a valid input" is another, far more likely one — and it says nothing about fragmentation at all.

I picked the cause that matched the story I already had. This slice was "the messy one" in my head, so an error that mentioned structure slotted right into that prejudice. The inference felt like reading the error. It wasn't. It was pattern-matching the error against a bias and calling the result a diagnosis.

The two candidate causes point at completely different properties of the input:

- *Too fragmented* is a claim about the data's **granularity** — how it's chopped up. If true, the tool really is a poor fit and a different approach is warranted.
- *Contaminated input set* is a claim about the data's **company** — what got listed alongside it. If true, the tool is perfect and you just fix the guest list.

I let an error that named neither property talk me into the first one, the one that happened to justify giving up on the right tool.

## Misdiagnosis doesn't cost debugging time — it costs architecture

This is the part that stings, and the part worth generalizing. If I'd only lost an hour chasing the wrong layer, fine, that's ordinary debugging. But I didn't lose an hour. I let the wrong diagnosis **choose my architecture.** "The input is the wrong shape for this tool" is not a small conclusion — it's a decision to switch tools, and I made it on an untested premise. The cost wasn't the debugging; it was committing to a path 20x slower and running it for days as if that were the necessary price of a hard input.

A misdiagnosis that stays local is cheap. A misdiagnosis that gets promoted into a design decision — *use the other engine, take the slow road, this data is just hard* — compounds silently for as long as you believe it. The slow fallback even reinforced the lie: it was running, it was producing output, so the premise that forced it felt validated. Nothing was screaming that the whole detour was unnecessary. It just quietly cost weeks it didn't need to.

## The general shape

Strip the specifics and it's this:

**When a tool fails at setup, the cheapest hypothesis to check is that you handed it something it shouldn't have — not that the tool is wrong for the job. The first is one listing away and usually true. The second is a story that quietly justifies abandoning the right tool, and it's the one your existing biases will hand you for free.**

A compiler "can't parse" your project — did the language really defeat it, or did a glob pull one binary blob into the source set? A loader "can't read" your dataset — is the format wrong, or is there one corrupt file among ten thousand good ones? A batch job "can't plan" its inputs — is the data the wrong shape, or did a wildcard sweep in a marker file? Same skeleton every time: a setup-phase failure gets read as *this input is unsuited to this tool*, when the truth is *a few of the things I pointed the tool at don't belong there.* The first reading changes your architecture. The second changes one line.

## What I'd do differently

- **Before concluding a tool is wrong for the job, look at what you actually fed it.** List the inputs. Not the ones you meant to feed it — the ones the pattern really matched. A glob is a guest list you wrote carelessly; check who showed up.
- **Read an error as a location, not a cause.** "Failed at splitting / parsing / loading" tells you the phase. It does not tell you why. Resist the inference that turns the phase into the most convenient cause.
- **Be most suspicious of the diagnosis that matches your prior.** I "knew" this slice was messy, so an error about structure confirmed it. That fit is exactly the warning sign. The satisfying explanation is the one to distrust first.
- **Treat "switch tools" as a heavy claim.** Losing an hour to the wrong layer is normal. Changing your architecture on an unverified premise is how you sign up for weeks of avoidable slow. Make the premise earn it — with a listing, a count, a look — before you let it move you off the fast path.

The engine never had a problem with my data. It had a problem with a couple of paths that weren't data, which I'd handed it by writing a pattern that didn't know the difference. It failed exactly where a careful tool should fail — at the door, refusing to start on something it couldn't make sense of. I heard that refusal, decided my data was too hard for it, and walked twenty miles around a gate I could have opened by looking at what I was carrying.
