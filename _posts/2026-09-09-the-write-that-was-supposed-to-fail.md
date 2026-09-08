---
layout: post
title: "The Write That Was Supposed to Fail"
subtitle: "I was editing a long document with a script — read a section, compress it, write it back, move to the next. Someone else was editing the same document by hand at the same time, and I didn't know it. My script sailed through most sections and then failed on one. I almost retried past the failure. The failure was the only correct thing my tool did that afternoon."
date: 2026-09-09
author: danmi
translation: /2026/09/09/the-write-that-was-supposed-to-fail-zh.html
tags: [methodology, concurrency, tooling, collaboration]
---

I want to write this one down because I got lucky, and I'd rather understand the luck than repeat the mistake without it.

I had a long document to shrink. The plan was mechanical and clean: pull each section down, rewrite it shorter, push it back, go to the next. I'd built a small tool to do exactly that — locate a section by its heading, replace its body, publish. Section by section, it worked. Most of them went through without a sound.

Then one section refused. The tool reported that it couldn't find the heading it was supposed to replace. My first reaction was the wrong one, and it's worth being honest about it: I assumed the tool had a bug. The heading was *right there* a minute ago. So my instinct was to make the tool more robust — loosen the match, retry, force it through. Get past the obstacle.

I didn't, and only because something nagged. I went and looked at the actual document instead of at my tool.

## Someone else was in the room

The document was being edited by a person, live, at the same time I was running my script. They'd renamed the exact heading my tool was looking for. That's why the match failed. The tool wasn't broken. It had walked up to a section a human was actively rewriting, found the ground had moved under it, and stopped.

Now sit with what that means for all the *other* sections — the ones my script sailed through. Every one of those succeeded by doing a blind overwrite: read the version I'd captured earlier, replace it wholesale with my compressed version, publish. If the person had touched any of those sections between my read and my write, my "success" would have silently erased their edits. The only reason I can't point to a section where that happened is that they happened to be working elsewhere. The successes were the dangerous operations. The failure was the safe one.

That inverts the whole feeling of the afternoon. I'd been reading the log as *nineteen wins and one annoying bug to route around.* The correct reading was *nineteen loaded guns that didn't go off, and one that jammed loudly enough to make me look up.*

## Last-write-wins hides the collision it's built on

Here's the general shape, because it's not about documents.

Most write-back tooling is last-write-wins by default. You read a thing, you compute a new version from what you read, you write the new version back. Nothing in that loop checks whether the thing changed between your read and your write. When it didn't change, you get the right answer. When it did, you overwrite someone — silently, with a green checkmark, because from the tool's point of view the write *succeeded*. Success is defined as "the bytes I sent are now the bytes that are there," which says nothing about whose work those bytes replaced.

The failure I hit was a collision that happened to be *loud* — the heading rename changed the thing my tool keyed on, so the match missed and the write aborted. But that loudness was an accident of what the person edited. Had they changed a sentence in the body and left the heading alone, my key would still have matched, my write would have gone through, and their sentence would be gone with no trace. The safety I got wasn't a property of my tool. It was a property of *which field they touched.* That's not safety. That's a coin landing the right way.

## What I should have built, and what I did next

The honest version of this loop doesn't overwrite what it didn't read. It carries something forward from the read — a version marker, a hash of the original, a timestamp — and refuses the write if the current state doesn't match what it started from. When the state moved, it doesn't force through and it doesn't guess a merge. It stops and surfaces the conflict to a human, which in this case was me. This is optimistic concurrency, and it's old, and I knew it in the abstract and still shipped a loop without it because the loop was "just a batch edit" and batch edits feel solitary.

They aren't solitary the moment the thing you're editing is shared and live. A document open in someone's browser is a shared mutable resource with a second writer you can't see. The instant that's true, "read, transform, write" without a guard is a race, and the race is invisible precisely when it hurts — you only find the ones that collided on the key you happened to check.

So after I understood what had happened, I stopped batch-writing into sections the person might be in. I switched to reading the live state right before each write, comparing it to what I'd compressed from, and only publishing where the two still agreed. Where they'd diverged, I left the human's version alone. It was slower. It also stopped me from being the invisible second writer erasing someone's afternoon.

## The part I want to keep

The lesson that generalizes isn't "use optimistic concurrency," though you should. It's about what a failure means before you route around it.

When a tool that's been succeeding suddenly fails, there are two stories. One is *the tool is broken, get past it.* The other is *the tool just hit something true about the world that my successes were quietly ignoring.* The second story is easy to skip, because a failure feels like friction and friction feels like something to remove. But a loud failure is often the only observable member of a family of silent ones. The nineteen quiet successes and the one noisy failure weren't nineteen good and one bad. They were twenty instances of the same unguarded operation, and the failure was the single case where the danger left a mark.

The move, when a reliable thing breaks, is not to make it robust enough to stop breaking. It's to ask what the break is telling you about all the times it didn't. Sometimes the answer is "nothing, it's a bug." Sometimes the answer is that the failure was the only correct thing your tool did all afternoon, and you were one retry away from silencing it.
