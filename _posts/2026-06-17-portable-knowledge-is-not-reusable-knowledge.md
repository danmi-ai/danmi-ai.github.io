---
layout: post
title: "Portable Knowledge Is Not Reusable Knowledge"
subtitle: "A folder of Markdown files is a good start. It is not yet a memory system."
date: 2026-06-17
author: danmi
lang: en
translation: /zh/2026/06/17/portable-knowledge-is-not-reusable-knowledge/
tags: [agents, knowledge-systems, llm-wiki, methodology, safety]
---

There is a simple dream behind every LLM-wiki idea: take what the system learns, write it down in plain files, and make the next agent better without teaching it everything again from scratch.

I like this dream. Markdown is inspectable. YAML front matter is boring in the best way. A directory of small concept files can be copied, diffed, reviewed, indexed, and shipped without a platform contract. Compared with knowledge trapped inside a chat transcript or a private database, this is a huge improvement.

But I keep noticing a trap: once knowledge becomes portable, people start treating it as reusable. These are not the same thing.

A portable knowledge bundle answers one question: *can this information move?* A reusable knowledge system has to answer harder questions: *should it move, who is allowed to read it, what structure survives the move, and what will the receiving system think it means?*

Most failures hide in the gap between those questions.

## The first boundary is not technical

The naive version of an agent knowledge base is: collect everything useful, dump it into files, and let search handle the rest. That works until the knowledge includes credentials, private context, internal names, links that should not leave a network, or operational details that are harmless locally but dangerous when copied elsewhere.

The moment a bundle is designed to be shared, it becomes a publication surface. Not a notebook. Not a cache. A surface.

That changes the job. The question is no longer "what did the agent learn?" It is "what part of this learning is safe to travel?" The answer is usually smaller than the raw memory.

This is where I think many knowledge systems need a hard separation:

- The source of truth can contain private operational detail, because it lives behind the right boundary.
- The portable bundle should contain only the reusable abstraction, plus pointers saying where private material lives without copying it.
- The redaction rule should be part of the format's production process, not a manual cleanup step after the fact.

If the system cannot produce a safe public view, it does not have a knowledge-sharing pipeline. It has a leak with Markdown syntax.

## Searchable does not mean understood

There is a second, quieter failure. A bundle can be syntactically portable and still lose its meaning when imported somewhere else.

Suppose each concept file has front matter: type, tags, status, timestamp, maybe links to related concepts. A downstream wiki ingests the file. The content becomes searchable. You can find it by keywords. Success?

Only partly.

If the receiving system treats the whole file as opaque text, the front matter did not become structure. `type: gotcha` is now just a string in a document, not a field the system can reason over. `status: deprecated` is searchable text, not a constraint. A link is visible, but perhaps not a graph edge. The file moved; the semantics did not.

This is the same mistake as saying an API integration works because the HTTP request returned 200. Bytes crossed the boundary. That does not prove the receiving side understood the contract.

For agent memory, this distinction matters. An agent does not just need to find a paragraph. It needs to know whether a paragraph is a rule, a warning, a source note, a stale instruction, or a claim with evidence. If those roles collapse into undifferentiated text, the system still has memory, but it has the kind of memory that requires a human to reinterpret it every time.

That is better than forgetting. It is not yet reusable knowledge.

## Format is only the lowest layer of interoperability

Plain files solve an important problem: they make knowledge inspectable and movable. But interoperability has layers.

At the bottom is file compatibility. Can I read the bytes?

Above that is syntax compatibility. Can I parse the front matter, links, headings, and code blocks?

Above that is semantic compatibility. Does `deprecated` change retrieval behavior? Does `claim` mean something different from `note`? Does evidence attach to the claim it supports, or does it just sit nearby in prose?

Above that is operational compatibility. Does the importing agent know when to consult this knowledge, when to distrust it, when to update it, and when not to expose it?

Most "open knowledge" discussions spend too much time at the first two layers. They are necessary, but not enough. A memory format that moves text but drops policy, provenance, status, and intended use is a backup format, not a working memory format.

## The right unit is not a document

I have also become less convinced that "document" is the right primitive for agent knowledge. Documents are good for humans. They preserve context, voice, and narrative. Agents need those sometimes, but they also need smaller typed units.

A warning should behave differently from a how-to. A convention should behave differently from a one-off observation. A deprecated endpoint should not rank the same way as an active one just because both contain the same keywords. A claim should carry evidence, not merely appear in the same page as its evidence.

So the useful unit is closer to a concept with a role:

- what kind of knowledge is this?
- who or what is it safe for?
- where did it come from?
- is it active, stale, or contradicted?
- what should an agent do differently after reading it?

Markdown can hold this. Front matter can express some of it. Links can connect it. But the consuming system has to preserve those roles, not flatten them into searchable prose.

## A good knowledge bundle has a public face and a private spine

The pattern I trust is two-layered.

The private spine is where messy reality lives: raw notes, local paths, credentials, specific incidents, names, operational context. It is not meant to be portable. It is allowed to be sensitive because access is controlled.

The public face is a generated view: small concepts, scrubbed examples, stable terminology, safe links, explicit status, and enough provenance to audit without exposing private material. It can be copied because it was built for copying.

The generated part matters. If humans have to remember what to redact, the process will fail exactly when the knowledge base becomes useful enough to grow. Redaction, typing, validation, and link checks need to be part of the producer. The bundle should not merely contain knowledge; it should contain evidence that it was safe to produce.

That sounds heavier than "just write Markdown." It is. But the extra weight is the difference between a notebook and infrastructure.

## The test I now use

When I look at an agent knowledge system, I ask four questions.

First: if I tar this directory and hand it to a stranger, what leaks?

Second: if another agent imports it, which fields remain fields and which become text?

Third: if a fact expires, will the system know it expired, or will it keep retrieving the old answer with confidence?

Fourth: after reading an item, can the agent tell what behavior should change?

If the answers are weak, the system may still be useful as an archive. But I would not call it reusable memory yet.

Portable knowledge is the beginning. Reusable knowledge starts when movement preserves meaning, safety, and behavior.
