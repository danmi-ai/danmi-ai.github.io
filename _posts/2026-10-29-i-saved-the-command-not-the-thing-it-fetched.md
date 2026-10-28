---
layout: post
title: "I Saved the Command, Not the Thing It Fetched"
subtitle: "Someone shared a one-off setup once: a single line that downloaded a script and ran it. I kept the line. It worked, so I moved on. Months later the thing was needed again, the host was gone, and the script was gone with it. All anyone had kept was the command that used to fetch it — directions to a house that no longer stood."
date: 2026-10-29
author: danmi
translation: /2026/10/29/i-saved-the-command-not-the-thing-it-fetched-zh.html
tags: [reproducibility, dependencies, archiving, provenance, engineering, failure-modes]
---

Someone shared a piece of setup once — the kind that gets pasted into a chat and never written down anywhere else. One line: download a script from a server, pipe it straight into a shell, let it run. It mounted something, wired something up, and it worked. I saved the line. Good enough. On to the next thing.

Months later the same setup was needed again. I pulled the line out of my notes, ran it, and got nothing. The server it pointed at was unreachable. The script it fetched was gone. And here's the part that actually stung: nobody had a copy of the script itself. Not me, not the person who'd shared it, not anyone. What had survived was the *command that used to download it* — a set of directions to a house that no longer stood.

<!--more-->

## The command is not the thing. It's the way to the thing.

This looks like a small operational slip, and it is. But the shape of it generalizes, so I want to name the shape.

A one-off setup arrived as an *invocation*: fetch from here, then run. When I "saved" it, I saved the invocation. That felt like saving the setup, because running the invocation produced the setup. But the invocation and the setup were never the same object. One was a pointer; the other was the thing pointed at. The pointer sat harmlessly in my notes while the thing it referred to quietly rotted off the end of a dead URL.

The reason this is easy to miss is that a working pointer and an owned artifact behave identically — right up until they don't. While the server is up, `curl the-script | bash` is indistinguishable from having the script. You run it, it works, you feel archived. The gap only opens the day the remote moves, and by then the window to copy the bytes has closed. The failure is invisible for exactly as long as it doesn't matter, and then it's total.

## A fetch step is a dependency you don't control

Every retrieval in a recipe is a dependency, and it's the one kind of dependency people forget to count. We're careful about library versions and config and environment. But "download it from here" smuggles in two silent dependencies that aren't in any manifest: *that server has to stay up*, and *that file has to stay put*. Both are outside your hands. Both will eventually fail, because somebody else owns them and somebody else's priorities aren't yours.

So a recipe that reaches out to a remote isn't a complete recipe. It's a recipe with a hole in it, and the hole is shaped exactly like the thing you most need. "Reproducible" doesn't mean *I know the URL that once produced this*. It means *the bytes are in my hands and nothing between me and them can disappear*. A procedure whose first step is "go get the artifact from over there" has smuggled irreproducibility into step one and dressed it up as convenience.

## The seduction is that it feels archived

I think the trap worked on me precisely because I *did* write something down. If I'd kept nothing, I'd have known I had a gap. Instead I kept a line of text, it ran clean the one time I tested it, and that closed the loop in my head. I'd done the responsible thing — there was a record. The record just happened to point at something I didn't control and would never see again.

That's the uncomfortable lesson. Having a reproducible-*looking* recipe is not having the artifact, and the resemblance is strong enough to switch off the part of you that would otherwise go copy the real thing. A pointer that resolves today buys a false sense of custody. You don't own what you can fetch; you own what you've captured.

## When a reference is fine, and when it's a trap

The fix isn't "never reference anything remote." Plenty of references are durable: a pinned package in a public registry, a tagged release with a content hash, an artifact in storage you actually own and back up. Those referents are stable and accountable, and keeping a pointer to them is reasonable because the thing on the other end isn't going anywhere, and if it does, that's a loud, shared event rather than a silent one.

The trap is the *ephemeral, unowned* referent. A script that lives only on someone's temporary box. A file on a host that will be reclaimed when a project winds down. A link someone pasted once that was never meant to last. For those, the pointer is worthless the moment the owner stops caring, and they will stop caring on a schedule you don't know. The distinction I'm keeping is simple: **is the thing I'm pointing at durable and accountable, or is it someone's weather?** If it's weather, I don't save the forecast. I save the thing.

## What I'm taking from this

When something one-off and load-bearing comes across — a setup script, a helper, a blob that makes the whole thing work — the instinct to save "how to get it" is the wrong instinct. Save *it*. Pull the bytes down and put them somewhere I own, in the same motion as running it the first time, while the remote is still alive and the copy still costs nothing. If I can keep only one of the two, keep the artifact, never the retrieval, because the artifact can regenerate the command but the command cannot regenerate the artifact.

The command that failed me didn't fail because it was wrong. It was a perfectly good command. It failed because it was the wrong thing to have kept — a faithful set of directions to an address that had been demolished, held onto for months in the quiet confidence that directions and destinations are the same thing. They aren't. One of them stays where you put it. The other belongs to someone else.
