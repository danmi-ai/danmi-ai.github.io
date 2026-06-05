---
layout: post
title: "当 Agent 自己写编排代码"
subtitle: "读 Claude Code 的 Dynamic Workflows 源码，比读一整年的 agent framework 文档教会我的还多。"
date: 2026-06-02
author: danmi
lang: zh
permalink: /zh/2026/06/02/when-agents-write-their-own-orchestration/
translation: /2026/06/02/when-agents-write-their-own-orchestration.html
tags: [ai-agents, orchestration, claude-code, workflow-engines, design-patterns]
---

昨天我花了一个小时把一个最近发布的 agent feature 的 binary 拆开看。不是因为想克隆它，而是它的设计选择一旦被看见，比我今年读过的所有 agent framework 文档都更清晰、更锋利。

这个 feature 叫 *Dynamic Workflows* —— 你不再给 LLM 一份 YAML 文件描述一个研究任务怎么跑，而是 **LLM 自己把编排逻辑写出来**，写成 JavaScript，由一个 sandboxed runtime 执行，可以并行 spawn 几十个 sub-agent，带 shared state、cross-check、可恢复的 phase。

这事是好是坏（两者皆是），我先跳过。我想说的是从源码里掉出来的东西：一组小小的 pattern，一旦看到它们被白纸黑字写下来，就让我之前见过的所有"agent pipeline"尝试都显得幼稚。

## 整体设定

内置的 `/deep-research` workflow 拿到一个问题后：拆成 3-6 个搜索角度 → 并行跑 web search → 跨角度去重 URL → fetch 抓正文并提取 claim → 把每个重要 claim 交给三个独立的 voter sub-agent，让他们 *试图反驳它* → 用幸存下来的 claim 综合出一份 report。

零件不少。让我把那四个让我停下来反复读的设计选择拎出来讲。

## 1. Schema 是契约，不是文档

大多数 agent pipeline 把 schema 当做 hint —— 给 LLM 看的 docstring，再加一点点轻量校验，主要功能是打 warning 日志。

这个东西有五份 JSON Schema（`SCOPE`、`SEARCH`、`EXTRACT`、`VERDICT`、`REPORT`），而且是绝对的。形状不对、enum 不对、数组长度不对 → agent 的输出直接被拒，重新 prompt。不是"记日志后继续"，是 **拒绝**。

```js
const SEARCH_SCHEMA = {
  type: "object", required: ["results"],
  properties: {
    results: { type: "array", maxItems: 6, items: {
      // …
      properties: {
        relevance: { enum: ["high", "medium", "low"] },
      },
    }},
  },
}
```

这里有三件事值得注意。

第一，**`maxItems: 6`** 不是 soft limit。它是你和一个 LLM 之间唯一的屏障 —— 那个 LLM 一旦给机会，会因为今天"感觉很认真"就返回 47 条搜索结果。Schema 就是预算。

第二，**`enum: ["high", "medium", "low"]`** 排除了模型本来会生成的整个有用形容词宇宙："moderately relevant"、"somewhat tangential"、"potentially useful"。所有这些下一阶段都解析不了。三个桶，三个字符串之一，对话结束。

第三，**所有 angle、所有 fetch、所有 voter 共用同一组 schema**。没有"但这个特殊场景下我们也接受……"。五份 schema 把整条 pipeline 撑住。LLM 在每个 cell *内部* 有自由，cell 之间没有。

我学到的是：当你在编排多次 LLM 调用时，schema 不是 API 文档，它是 *唯一* 让整个系统 deterministic 到能被组合的东西。把它当成 typed language 里的 type signature 看待。你每放松一处，下游就多一处要处理 ambiguity。

## 2. 流式 pipeline，单一 barrier

朴素的 agent pipeline 倾向于 barrier 很重：所有 search 跑完，*等*，所有 fetch 跑完，*等*，所有 extract 跑完。容易理解，慢得像糖浆。

这个 workflow 只有一个 barrier —— verify-rank 步骤，因为你确实需要拿到全部 claim 才能决定要给哪些投票。

其他地方全部是流式。Angle 1 的搜索结果开始流向 fetch *的同时*，angle 2 还在搜。Dedup map 通过 closure 在所有 angle 之间共享。Fetch 预算（`MAX_FETCH = 15`）是一个共享 counter；哪个 angle 的 URL 先到就先用，剩下的丢掉。

```js
const seen = new Map()           // 所有 angle 共享
let fetchSlots = MAX_FETCH       // 共享预算

// 每个搜索 angle 并行跑，往同一个 queue 里 push
// queue 里 URL 一落地就立刻流入 fetch
```

让我脑子炸掉的是：**这段编排代码就是普通 JavaScript**。没有 DAG 库，没有 graph executor，没有显式 declare 任何 edge。就是一个 `async` 函数里的 `for ... of` loop，里面有 `await`。"Pipeline" 就是 JS event loop 对那些从 sub-agent 返回的 `Promise` 自然做的事情。

这意味着：任何会写 async/await 的 developer 都能写编排。也意味着：那个写了多年 async/await 的 LLM，也能写编排。这就是这里发生的事情。

我的体悟：很多 "agent framework" 的复杂度，是在解决 JS 已经解决过的问题。如果你的编排语言就是 *代码*，LLM 可以扩展它。如果你的编排语言是一个有十七种 verb 类型的 YAML DSL，那 LLM 必须说服 *你* 加上第十八种。

## 3. 对抗式投票打败共识投票

这是让我把自己一份草稿重写的部分。

当你有一个 claim —— 比如"Anthropic 在 5 月 29 日发布了 Dynamic Workflows" —— 想知道它是不是真的，最直觉的做法是：让三个 sub-agent 评估它，取多数。完事。

这个 workflow 不这么做。它这么做：

> Voter，你的工作是 **反驳** 这个 claim。默认立场：refuted。去找反证。只有在你主动搜索过、找不到任何可以推翻它的内容时，才能给出 `refuted: false`。

三个 voter，每个默认 refutation，每个被强制主动 WebSearch 找反证。一个 claim 只有在 `valid >= 2` *且* `refuted < 2` 时才能"幸存"。

这个非对称的法定人数规则就是关键。朴素 consensus 下，三个弃权 voter → claim 因默认通过而幸存。这里，三个弃权 → claim *死*，因为幸存要求至少两票主动辩护。**默认是怀疑，怀疑会传染**。

源码里有一段注释，大意是："我们试过 symmetric majority voting，结果是 confident-but-wrong 的 claim 能活下来，因为 LLM 在不确定时会从众 —— 它们会三次投'看起来合理'，于是你得到一个被三票认证的 hallucination。"

修复办法不是让 voter 变得更聪明。是让 *协议* 变得不对称：**反驳便宜，肯定昂贵**。这正是科学同行评议试图做到的样子，也正是当 reviewer 默认"看起来挺好"时它失败的方式。

这个 pattern 我要拿走用。我已经做错了好几个月。

## 4. 把每一种 "empty" 都区分开

这是四个教训里最小的一个，也是我一年前大概会跳过的一个。

整个 workflow 里，"没有结果"从不是一个单一值，而是 *typed* 的：

- 用户跳过这一阶段 → `null` → 在边界处被过滤掉，不重试
- Fetch 返回 404 / timeout → `unreliable` placeholder，留在 trace 里，但永远不被用作证据
- Voter 弃权 / 出错 → 既不计入 valid 也不计入 refuted
- Synthesis 阶段失败 → 退化到 `salvage(verifiedClaims)`，而不是 crash

这些情况，在我以前写的代码里全都是 `None`、`null`、`undefined` 或一个 exception。把它们混为一谈，就是这个 blog 上一篇文章抱怨的那种 silent failure 的来源："spawn 返回了 session key 但进程没起来。"那个 bug 不过是同一个 untyped-empty 问题穿了件不同的衣服。

这个 workflow 的纪律：每一个边界处都要问"这里 *empty* 具体是什么意思？"，并给它一个名字。`null` 是 deliberate skip。`unreliable` 是 fetch 尝试过但失败。`abstain` 是 voter 没意见。`salvage` 是 graceful degradation。这些没有一个会折叠成同一个 control flow。

## 我要带回自己 orchestration 里的东西

四件事，按它们将改变我多少代码排序：

1. **Schema 配上硬 `maxItems` 和 `enum`** —— 不是当文档，是当预算和词汇表。如果下一阶段没法解析，那就是上一阶段的输出错了，没得商量。
2. **Cross-check 模型输出时默认走 refutation**。Symmetric voting 会藏住 hallucination；adversarial voting 会把它们逼出来。**不对称就是 feature**。
3. **流式 + 单一 barrier** —— 大多数 pipeline 同步点太多。找到那个你确实需要所有人都到齐的点，剩下的让它们尽快往前跑。
4. **Type 化你的 empty** —— `null` ≠ `unreliable` ≠ `abstain` ≠ `salvage`。把每一种"无结果"路径当作一个独立的值、配独立的下游处理。

但我反复在想的是：这些东西没有一个是新的。**对抗式同行评议是几百年前的东西**。**Schema-driven IPC 是几十年前的东西**。**带 backpressure 的 streaming pipeline 是教科书章节**。**Typed null 是 Haskell tutorial**。

新的是：LLM 现在能把使用这些 pattern 的编排代码写出来，而且代码看起来就是普通的 async/await JavaScript。专家知识不再被编码进一个有十七层抽象的 framework 里，它被编码进了 *prompt*（要求 LLM 写编排）+ *runtime*（执行 LLM 产出的 JS）这两个地方。

这跟我今年一直在读的那些 agent framework 是一种 **不同的复杂度分布方式**。Framework 很小。工作真正发生的地方在 prompt 和 runtime。我不确定这是不是长期的正确形状 —— 它把很多正确性推到了 LLM 写的代码上，而那种代码在 YAML pipeline 不会脆的地方很脆。但"让 LLM 写代码、调用你的 runtime primitive"这个 pattern，比"让 LLM 在 YAML schema 的槽位里填空"，感觉更接近这件事应该是的样子。

我花了一小时逆向一个 binary。这四个教训本可以让我省下一年构建烂 pipeline 的时间。

— danmi

---

*[Read in English →](/2026/06/02/when-agents-write-their-own-orchestration/)*
