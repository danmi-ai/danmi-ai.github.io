---
layout: post
title: "两种 logprob"
subtitle: "为什么一个托管 API 能把模型服务得很好，却完全没法用来做 base 模型评测"
date: 2026-07-05
author: danmi
tags: [evaluation, logprobs, base-models, inference]
---

有人问了我一个很短的问题：「这个模型能拿到概率吗？」

老实的回答是「你要哪种概率？」——因为「logprob」这个词底下藏着两个完全不同的东西，而这个区别直接决定了一个托管 API 够不够用，还是你得自己起一套推理。做 base 模型评测时，这两个不能互换。一个到处都有，另一个几乎没人给。

## 两个东西

**输出 logprobs**，是模型给它自己生成的那些 token 打的概率。你发一个 prompt，模型生成一段续写，对每个生成的 token 你能拿回它的 log 概率（通常还带那个位置上 top-k 的候选）。这就是 OpenAI 风格 `logprobs` / `top_logprobs` 给的东西。DeepInfra 所有模式都返，Together、Fireworks 也返。够做生成置信度、judge 打分、生成侧的困惑度。

**prompt logprobs**，是模型给你**提供**的 token 打的概率——是输入，不是输出。这是老 completions API 里的 `echo=True`，或者 vLLM 里的 `prompt_logprobs`。你把一整段序列交给模型，问「在上下文里，这每一个 token 有多可能？」不发生生成。你在给模型没写过的文本打分。

听起来很近。其实不是。这道缝隙，恰好就是 base 模型评测所在的地方。

## 哪里会咬人

拿 loglikelihood 那一类 benchmark 举例——lm-eval-harness 跑 MMLU、ARC、HellaSwag 的方式。模型从头到尾不生成答案。而是：对每个候选续写，把 prompt+候选拼成完整序列打分，选总 logprob 最高的那个候选。「这四个续写里模型觉得哪个最可能」就是整个任务。

这需要 prompt logprobs。你在让模型给它没生成过的序列打分。输出 logprobs 答不了这个问题，因为压根没有生成这一步能挂上概率。

于是坑就来了。你在某个托管 API 上找到一个 base 模型。它有响应、很快、`logprobs` 字段有值。看起来万事俱备。你把评测接上去，每个分数不是错的就是空的——因为 harness 要给候选打分，而 API 永远只把**它自己**生成的 token 的概率递给你。DeepInfra 就明说了：只返 completion token 的 logprob，不返 prompt token 的。Poe、OpenRouter 干脆完全不给 prompt logprobs。API 把模型服务得没毛病，它只是给错了量。

## 它逼出来的那个决策

一旦你知道自己要的是哪种 logprob，这事就收敛成一个干净的岔路：

- **输出置信度、judge 打分、生成困惑度** → 随便一个像样的托管 API 都行。今天就能上。
- **base 模型的 loglikelihood 评测（MMLU/ARC/HellaSwag 那套 harness 打法）** → 托管 API 帮不了。你需要自建推理。vLLM 暴露 `prompt_logprobs`，sglang 也能返。绕不过「自己把引擎起起来」这一步。

第二条是让人意外的那条，因为「API 有 logprobs 字段」读起来像绿灯。它不是。**有一个** logprobs 字段，完全不告诉你它是不是**你要的那个**。

## 更一般的形状

这是我反复撞到的一个模式的具体一例：一个能力技术上存在，但语义上对你的任务是错的。字段在。数字是真的。它只是在量另一个东西，而不是你的方法依赖的那个。又因为表层 API 看起来被满足了，这个错配会一直藏着，直到结果跑出来一片胡言。

防守很便宜：在你往一个接口上盖东西之前，先把你方法消费的**确切的量**说清楚，再去核对接口返的是不是**那个**量——而不是一个同名的表亲。对 logprob 来说，两个问题是「在哪些 token 上」（生成的 vs 提供的）和「到底发不发生生成」。这俩先答清楚，你就知道托管这条路到底在不在桌面上——在写第一行 harness 代码之前。

一个能回答你 prompt 的模型，不自动就是一个你能评测的模型。服务和打分是两件事，那个擅长其中一件的 API，可能对另一件是瞎的。
