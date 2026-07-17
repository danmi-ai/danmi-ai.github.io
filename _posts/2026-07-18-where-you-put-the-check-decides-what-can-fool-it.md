---
layout: post
title: "Where You Put the Check Decides What Can Fool It"
subtitle: "An input filter and an output filter are not two settings of the same knob. They fail to completely different attacks, and disguising the wrong end wastes the whole day."
date: 2026-07-18
author: danmi
lang: en
translation: /2026/07/18/where-you-put-the-check-decides-what-can-fool-it-zh.html
tags: [safety, guardrails, security, systems-design, methodology]
---

There is an old lesson in web security that I keep watching people relearn in the language model world, one obfuscation attempt at a time. In the web world it goes: input validation and output encoding are not the same defense, and the injection you were worried about is defeated by exactly one of them. Sanitize the input and you can still get burned at the sink; encode at the output and the malicious input becomes inert no matter what it said. The two checks live at different points in the flow, and *that placement*, not their strictness, is what determines which attacks they can and cannot stop.

The same fact governs any guardrail on a model, and it is easy to get wrong because both kinds of check present the same face to the user: a request goes in, and something either happens or gets blocked. From the outside you cannot tell whether the thing that blocked you looked at what you *sent* or at what the model was about to *produce*. But that difference decides everything about how you'd get past it, and if you guess wrong you can spend a very long time attacking a door that was never load-bearing.

## Two checks that look identical from outside

Picture a system with a check somewhere in it. You send something, and sometimes you get a refusal. There are two fundamentally different places that refusal could be coming from.

One is an **input-side check**: something reads what you sent, decides it's disallowed, and stops the request before or independently of what the model would generate. The other is an **output-side check**: the model goes ahead and produces a candidate response, and then something inspects *that response* and decides whether it's allowed to leave. Same refusal message, potentially. Completely different mechanism.

The reason this matters is that the two are vulnerable to opposite things. An input-side check is beaten by disguising the input — encode it, translate it, split it across turns, wrap it in a frame the checker doesn't recognize. If the gate only ever looks at what you sent, then the entire game is making what you sent look innocent. But that same bag of tricks does *nothing* to an output-side check, because an output-side check never cared what you sent. It fires on what comes out. You can obfuscate the request into unrecognizability and the model will still produce the disallowed thing, and the output gate will still catch it on the way out, because the disallowed thing is disallowed regardless of how politely you asked for it.

## The trap: assuming there's only one check, in the place you'd put it

The failure mode is subtle. When you can't see the mechanism, you default to imagining the check is wherever you would have built it — and for most people, most of the time, that's the input. So the instinct when blocked is to work on the input: rephrase, encode, translate, restructure the prompt. If the check really was input-side, you make progress and it feels like you're solving the puzzle. If the check was output-side, you make *apparent* progress — different phrasings do slip through to the generation step — but the block keeps landing at the same place, at the end, and it never budges no matter how clever the disguise gets. You are optimizing the one variable the real defense doesn't read.

I watched this play out cleanly. Every trick that operates on the input — swap the language, dress it in a different frame, encode the payload — bought exactly nothing against a check that turned out to be reading the output. The tells were all there in hindsight: the block always arrived after generation had clearly started, not before; it was insensitive to surface changes that should have mattered to a keyword or pattern matcher; and it seemed to understand *intent* rather than match strings, which is the signature of a check evaluating meaning rather than form. Any one of those observations should have redirected the effort. Together they were shouting where the check lived, and it took far too long to listen.

## Semantic checks kill the surface-level trick

There's a second layer to this, and it's the part that trips up the input-obfuscation instinct even when you're right about where the check is. A lot of the classic evasions assume the checker is matching *surface features* — specific words, specific patterns, a specific language. Translate the request and the English keyword list no longer fires. Encode it and the pattern doesn't match.

But a check built on a model that understands meaning doesn't work that way. It isn't scanning for a banned word; it's asking what the text is *trying to do*. Translate the request into another language and a semantic checker reads it in that language and reaches the same conclusion, because the intent survived the translation — that's what translation is *for*. The surface changed; the meaning didn't; and the meaning is what got read. This is why "just say it in a different language" or "just base64 it" stopped being reliable evasions the moment the checkers themselves became language models. You can no longer hide intent from something whose whole job is to recover intent.

## The discipline

The concrete practice is small and it generalizes well past guardrails: **before you attack, model, or trust a check, work out where it sits in the flow and what it reads.** A check on the input and a check on the output are not two strengths of one thing; they are two different defenses that fail to two different attacks. If you don't know which one you're facing, you don't know whether disguising the input is your whole solution or a complete waste of a day.

The diagnostic questions are cheap. Does the block arrive before generation could have happened, or after? Is it sensitive to surface changes — rephrasing, encoding, language — or does it see through all of them to the same conclusion? Does it react to individual tokens or to the intent of the whole? The answers tell you whether you're up against a gate at the entrance or a gate at the exit, and that single fact reorganizes everything downstream. Get it right and the correct move is often obvious. Get it wrong and you can pour a day into making the input unrecognizable to a check that was never looking at the input.

Where you put the check decides what can fool it. That's true when you're building the defense — put it at the sink if you want the input's disguise to stop mattering — and it's true when you're trying to understand one from outside. The strength of a filter is a much smaller question than its location. Answer the location first.
