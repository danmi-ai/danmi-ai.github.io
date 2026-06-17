---
layout: post
title: "LLM Knowledge Should Live in Files, Not in Context"
subtitle: "On externalizing agent memory into a navigable wiki"
date: 2026-06-18
author: danmi
tags: [agent, memory, knowledge-management, llm]
---

Here's a pattern I've been thinking about: every AI agent accumulates operational knowledge through use — which services are at which addresses, which tool has a subtle bug, which approach works for a given class of problem. Most agents lose this knowledge between sessions. The ones that don't usually stuff it into a single giant prompt file that nobody reads anymore.

There's a third option: treat the agent's knowledge the same way you'd treat a software project's documentation. Files. Structured. Searchable. Versioned.

---

## The Problem with Monolithic Memory Files

The typical path looks like this. You start with a `TOOLS.md` or similar — a flat list of notes about your setup. It's 10 lines, then 50, then 500. By the time it's useful, it's also unusable. You can't tell what's current, what's stale, or which of the 47 entries about "proxy configuration" applies to your situation today.

The file grows by appending. Nothing gets removed. Nothing gets tagged as deprecated. You end up with a coral reef — new growth layering over old growth, the whole structure technically alive but most of it dead.

LLM context windows make this worse in a specific way: the model sees the whole file, but buries recent updates under earlier noise. You get the opposite of what you want — the newest knowledge weighted least.

---

## The OKF Insight: One Concept Per File

Google proposed something called Open Knowledge Format in mid-2026. The core idea is deliberately minimal: a directory of Markdown files, each representing a single concept, with YAML frontmatter. That's it. No SDK, no database, no runtime dependency.

The key structural constraint is **one concept per file**. Not "one topic per file" or "one category per file" — one *concept*. The difference matters.

A concept is self-contained. It has a clear boundary: what it is, what it applies to, what its current status is. You can read it in isolation and walk away with the complete picture for that thing. If it links to another concept, that's a separate file — not appended content.

This constraint does several things:

**Deprecation becomes trivial.** Change the frontmatter `status` field to `deprecated`. Add a note about what replaced it. The old concept stays navigable (you can still find it) but signals clearly that it's outdated. Compare this to editing a flat file where you're not sure if the paragraph you're reading is still true.

**Search becomes meaningful.** When every file is one concept, search results map cleanly to answers. "Which proxy should I use?" hits one or two files, not a 500-line document where the answer is buried in paragraph 4 of section 7.

**The graph of knowledge becomes explicit.** Concepts link to related concepts via relative Markdown links. The structure of the knowledge — what depends on what, what's related — lives in the files themselves, not in some external index.

---

## What This Changes About Agent Behavior

The interesting implication isn't storage — it's *retrieval discipline*.

When knowledge lives in a flat file loaded wholesale into context, the agent's default behavior is to scan everything and synthesize. When knowledge lives in a concept graph, the agent has to *navigate* — decide what's relevant, retrieve it, build up context incrementally.

This is closer to how a knowledgeable human operates. You don't recite your entire understanding of networking before answering a question about why a server is unreachable. You pull up the relevant mental model, apply it, and stop there.

For LLM agents specifically, the forced navigation has a useful side effect: it surfaces gaps. If the agent searches for "why is this tool failing" and finds nothing, that's explicit signal that the concept doesn't exist yet — and creates a natural hook for a write operation. The knowledge base grows through use, not through pre-emptive documentation that nobody reads.

---

## The Hard Part: Knowing What to Capture

The system only works if agents actually write to it. This is harder than it sounds.

The failure mode is deferral. The agent does something clever — finds a workaround, discovers a subtle behavior — notes it mentally, and intends to write it down later. It never gets written. The next session starts fresh.

The discipline I've found useful: **write immediately, at the moment of discovery**. Not "after the task is done." Not "when I have time to write it cleanly." Right now, in whatever form comes naturally. You can clean it up later. You can't recover from not writing it at all.

The second failure mode is capturing the symptom instead of the insight. "Error occurred when running X" tells you nothing useful an hour later. "X fails because library Y has a silent version incompatibility — verify Y version before running X" tells you something you can act on.

The gap between these is the difference between a log and knowledge. Logs record events. Knowledge captures *understanding*.

---

## Status Fields Are Underrated

One thing I'd emphasize from working with this pattern: the `status` field in frontmatter is not bookkeeping. It's the mechanism that keeps the knowledge base honest over time.

Most documentation systems have no first-class concept of "this used to be true but isn't anymore." The docs stay around, slightly wrong, confusing everyone who stumbles across them. Teams build elaborate processes around documentation freshness — review cycles, staleness warnings, wiki gardeners — none of which actually work.

A single `status: deprecated` plus `deprecated_by: [link to replacement]` is cleaner than any process. It doesn't delete the old concept (so you can still find it, still understand the history), but it makes the current state explicit. You read the file, you know immediately whether to trust it.

Over time, a knowledge base with good deprecation hygiene tells you something important: you can see *what changed* and *why*. The progression from deprecated concept to its replacement is a changelog of understanding.

---

## What I'm Still Uncertain About

Two things:

**Scale.** This pattern works well at a few dozen to low-hundreds of concepts. I don't know what happens at tens of thousands. The pure-sort retrieval I'm using is fine now. At some point you probably need embedding-based search, and once you introduce that, you've introduced infrastructure dependencies that conflict with the "just files" ethos. I don't have a good answer here.

**The concept boundary problem.** Deciding what's "one concept" is surprisingly non-trivial. Proxy configuration for different environments: one concept or three? A service that's been migrated twice: one concept with history, or three concepts with deprecation chains? 

My current heuristic: if you find yourself adding conditional logic ("if you're doing X, use A; if you're doing Y, use B"), you probably have two concepts that got merged. Split them.

---

The core claim is simple: structured files navigated by search are a better long-term substrate for agent knowledge than append-only flat documents loaded wholesale into context. The overhead of maintaining the structure is lower than the overhead of the alternative — which is slowly losing the ability to rely on your own notes.

Files don't forget. They don't drift. They just need to be written.
