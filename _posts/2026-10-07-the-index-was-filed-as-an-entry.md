---
layout: post
title: "The Index Was Filed as an Entry"
subtitle: "A crawler looks for a conventionally named file, parses its frontmatter, and writes a record. Two repositories put a human-readable index at that path instead of a skill definition. Nothing errored. The crawler produced a record with no name and no description, and never descended into the dozen real skills sitting one directory down."
date: 2026-10-07
author: danmi
translation: /2026/10/07/the-index-was-filed-as-an-entry-zh.html
tags: [agents, data-engineering, ingestion, schema, systems]
---

A crawler I run collects agent skill definitions from public repositories. The convention it relies on is simple and widely followed: a file named `SKILL.md`, YAML frontmatter at the top carrying a name and a description, procedure text below. Find the file, parse the frontmatter, write a record, move on.

Two repositories broke it in the same way. Their `SKILL.md` had no frontmatter at all — because the file was not a skill. It was an index: a page for humans, listing a dozen sub-skills that each lived in its own subdirectory with its own `SKILL.md`. The correct reading of that file is "this is a directory node, go down." The crawler's reading was "this is a leaf, take it."

Nothing failed. The crawler wrote a record whose name was empty and whose description was empty, and never looked at the subdirectories. Two losses from one misreading: a blank row entered the collection, and a dozen real skills stayed outside it.

<!--more-->

## A convention tells you where to look, not what is inside

A filename convention is a locator. It answers *where do I find the thing?* A schema is a contract about shape. It answers *what will be inside when I get there?* These are different claims, and the crawler had quietly fused them into one: finding the file was treated as authorization to parse it as a particular shape.

That fusion is easy to make because in the early life of any convention the two really do coincide. When `SKILL.md` was new, every `SKILL.md` was one skill with frontmatter, so the filename did predict the shape, and code that assumed as much was correct every time. The assumption wasn't lazy — it was empirically true.

What breaks the coincidence is adoption. Once enough tools recognize a filename, that filename becomes the way to be seen, and people start putting adjacent things there. A repository publishing twelve skills names its top-level overview `SKILL.md` not out of confusion but because that is the file other systems will open. The same pull produces registry pages, catalogs, per-repo READMEs wearing the conventional name, bundles whose root file describes the bundle rather than a procedure.

So the count of document kinds living behind a popular filename only goes up over time. A consumer that hard-codes one kind doesn't fail at adoption-time; it degrades continuously as the ecosystem grows, and the degradation looks like data rather than like breakage.

## The missing frontmatter was the type signal, and it was discarded

Here is the part worth dwelling on: the information needed to classify these files correctly was present in the files themselves. A leaf skill has frontmatter. An index page does not. The absence of frontmatter was a reliable discriminator between the two kinds — and the parser threw it away by treating it as a defaulting problem instead of a typing problem.

When frontmatter is missing, there are two things you can do. You can fill the fields with empty strings and continue, which is what "be lenient in what you accept" tends to decay into. Or you can treat the absence as a positive signal — *this is not the kind of document I parse records out of* — and branch. The first option is lossy in a way that hides itself: the empty record looks like a parsed skill that happened to have a thin author, not like a document that was never a skill at all. The second option costs one conditional and recovers both the discarded good data and the mis-admitted bad data.

Lenient parsing has a good reputation it doesn't fully deserve. Filling a missing required field with a blank is not leniency, it's silent coercion of a type error into a valid-looking value. The record validates. The downstream count goes up by one. Nobody is told that the thing counted has no content.

## Absence is data, and defaulting erases it

The general shape: a required field is missing; the easy move is to substitute a neutral default and proceed; the default is indistinguishable from a legitimate value, so the fact that the field was *absent* — which was itself a signal — is gone the moment the default is written.

There is a difference between "this skill's description is the empty string" and "this document has no description because it is not a skill." Both end up as `description: ""` after lenient defaulting, and the second meaning, which is the one that should have changed control flow, is unrecoverable from the row. You cannot audit your way back to it later, because the evidence was discarded at parse time.

The fix is to let absence raise a question instead of answering it. Three outcomes where the lenient parser had one:

- Frontmatter present and well-formed → it's a leaf skill, write the record.
- Frontmatter absent, but the directory has `SKILL.md` files one level down → it's an index, recurse into the children.
- Frontmatter absent and no children → it's an unknown, quarantine it for review instead of writing a blank.

The recursion step is what recovered the dozen hidden skills. They were never unreachable; the crawler just stopped descending the moment it found a file at the expected name, because finding the file was its definition of "arrived."

## Arrival is not the same as a leaf

Underneath the parsing bug is a traversal bug wearing its clothes. The crawler conflated *I found a file at the path I was looking for* with *I have reached a terminal node*. In a flat world those are the same. In a world where the convention is also used for index pages, a hit on the filename can mean "you've arrived" or it can mean "you've reached a signpost" — and the only way to tell is to look at the content and the surrounding directory, which is exactly the look the early-exit skipped.

This is why the two bugs are really one. Treating the file as a leaf is what stopped the descent; treating missing frontmatter as a blank value is what turned the stopped descent into a plausible-looking record instead of an obvious error. Either check alone would have surfaced the problem. Together their absence made a structural miscategorization look like a slightly incomplete piece of data.

## What I'm taking from this

When you consume a convention that other people produce, separate two questions that feel like one. *Did I find the file?* is a locator question. *Is this file the kind of thing I think it is?* is a type question. A naming convention answers only the first. If your code treats a successful locate as a successful type-check, every off-type document that adopts the convention — and more of them adopt it the more successful the convention gets — enters your pipeline as a malformed instance of the type you expected rather than as the different thing it is.

Two checks worth adding to any ingester that walks a convention:

1. Before writing a record from a found file, confirm it is a leaf and not an index. The cheap test is whether the same convention appears below it; if it does, descend instead of recording.
2. When a required field is absent, branch on the absence before you default. Absence is frequently a type signal, and a default destroys it. Quarantine the unknown; don't launder it into a blank row.

The failure here produced no error line and no stack trace. It produced a collection that was one row larger and a dozen skills smaller than the truth, and a crawler that reported success on both counts.
