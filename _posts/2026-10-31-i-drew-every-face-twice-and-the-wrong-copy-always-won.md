---
layout: post
title: "I Drew Every Face Twice, and the Wrong Copy Always Won"
subtitle: "I was building a small 3D game with a renderer I wrote by hand. One mesh came out shaded backward — lit as if it faced the ground. The bug wasn't in the lighting. It was in a helper I'd written to be safe, and the way it failed is a trap that shows up far outside graphics."
date: 2026-10-31
author: danmi
translation: /2026/10/31/i-drew-every-face-twice-and-the-wrong-copy-always-won-zh.html
tags: [graphics, rendering, debugging, redundancy, determinism, engineering]
---

I was building a small 3D game. No engine, no library — a renderer I wrote myself, down to the triangle submission. Most of it worked. One part didn't: a large curved surface came out dark, a flat slab of deep blue-black, as if someone had pointed a light at the floor instead of the sky.

My first instinct was to blame the lighting. The shader mixed a ground color and a sky color based on which way each surface faced — standard hemisphere ambient. A surface pointing up gets sky; pointing down gets ground. The dark slab looked exactly like a surface that thought it was pointing down. So I went digging in the lighting math.

The lighting math was fine. The bug was somewhere I'd stopped looking, because I'd written it to be convenient and then trusted it.

## The helper I wrote to be safe

Early on, building the mesh code, I wrote a small helper to emit a quadrilateral — four corners, two triangles. Submitting a quad as triangles means choosing a winding order: the order you list the three corners decides which way the triangle "faces," which decides its normal, which decides its lighting.

I didn't want to think about winding every time I called it. So I made the helper emit the quad **both ways**. Both triangle pairs. One winding and its mirror. My reasoning at the time, such as it was: whichever orientation is correct will be there, and the wrong one will be facing away, so it won't matter.

That sentence is the whole bug. "The wrong one will be facing away, so it won't matter." I never checked whether it was true. It felt true.

## Why both copies is worse than one wrong copy

Here is what actually happens when you submit two coplanar triangles that occupy the exact same pixels.

They are at the same depth. Every fragment one produces, the other produces too, at the identical distance from the camera. The depth test decides which one you see. And the depth test I was using — the standard one, keep the fragment that is nearer-or-equal — resolves an exact tie by draw order. The second one submitted wins, because it is drawn later and passes the "or-equal" check against the first.

The second one I submitted was the reverse winding. So the reverse-facing copy won every tie. On every quad. Always.

Read that again, because it's the part that surprised me. I didn't have a surface with one correct face and one wrong face where the correct one shows. I had a rule that guaranteed the **wrong** one shows, on every single quad that went through that helper. The redundancy didn't give me a safety net. It gave me a coin that always landed the same way, and the way it landed was backward.

The lighting then did exactly what it was told. Reverse winding means the normal points the wrong way. A surface that should face the sky now reports that it faces the ground. The shader mixed in ground color. The tone-mapping pass crushed it into that flat blue-black. Every step downstream was correct. They were all faithfully rendering a lie that was injected three stages earlier by a helper I'd written to save myself five minutes of thinking.

## The fix, and the thing the fix taught me

The fix was small: emit the quad **once**, with one winding, and when a surface is a mirror of another, reverse its corner order by hand so its normal points where it should. More thinking per call. Fewer triangles. No ambiguity for the depth test to resolve, because there's no tie to break.

But the small fix sits on top of a bigger mistake, and the bigger mistake is the one worth keeping.

I had reached for redundancy as a substitute for correctness. I didn't know which winding was right, so I shipped both and told myself the system would sort it out. The system did sort it out — deterministically, and against me. Because the rule that broke the tie (draw order, depth-equal) had no idea which copy was correct. It wasn't choosing the right face over the wrong one. It couldn't. It was choosing the *later* one. I had handed a correctness decision to a mechanism whose only input was submission order.

## This is not a graphics problem

Strip the triangles away and the shape is everywhere.

You write a job two ways because you're not sure which is right, and let whichever finishes last win. You keep a fallback path alongside the primary one, both producing output, and something downstream picks one by timestamp. You dual-write to two stores and let last-writer-win settle disagreements. You add a retry that re-runs the whole thing and takes the newer result. In every case the same thing is true: when two candidates both produce a result, something has to break the tie, and that something usually breaks it by an arbitrary rule — order, time, position — that knows nothing about which candidate is correct.

"Belt and suspenders" only helps when the belt and the suspenders can't both be wrong in the same place at the same time. Mine could. They were the same object, at the same depth, and the tiebreaker was blind. Redundancy without a tiebreaker that understands correctness isn't safety. It's a hidden, deterministic choice, and determinism means that if it's wrong once, it's wrong every time, silently, in exactly the same way — which is the hardest kind of wrong to notice, because it never flickers.

The lesson I pulled out: when you can't tell which of two versions is right, the move is not to ship both and hope the system favors the good one. The system has no concept of "the good one." The move is to do the thinking and commit to one. A single face you reasoned about beats two faces you didn't, even though two sounds safer. Especially because two sounds safer.

I spent an hour staring at lighting code that was correct, because the wrongness was wearing the costume of a lighting bug. The actual cause was a five-minute shortcut I took at the start and then trusted forever. That's usually where these live — not in the part you're debugging, but in the part you decided you didn't need to think about.
