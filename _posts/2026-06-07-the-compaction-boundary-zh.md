---
layout: post
title: "压缩边界"
subtitle: "当推理 trajectory 半路被摘要，没人正面写过的那个 off-policy bug"
date: 2026-06-07
author: danmi
lang: zh
translation_of: /2026/06/07/the-compaction-boundary/
tags: [reinforcement-learning, agents, training, on-policy, compaction]
---

长 horizon 的 agent RL 在悄悄绕过一个技术上很别扭的问题，我想把它摆到桌面上来。

一个推理 agent 跑 50 轮，把 context window 撑爆，harness 在中间某一处把早期历史压成几百 token 的摘要再继续——你究竟应该拿什么去训练？

教科书式的答案，对一条干净的 PPO/GRPO trajectory 而言，是「全部都训」：把 prompt 和 tool result mask 掉，对每个 assistant token 求梯度，归一化，前进。一旦中间某处触发了 `/compact` 事件，这个答案就错了。错得很微妙，公开材料给的指引很薄，主流开源 RL 框架我查过的几个干脆就不支持这个场景。

这篇博客是我现在的判断和判断的依据。一切都还没定论。

## 「压缩」对 trajectory 做了什么

先把 agent 放一边。想象一条 50 轮 assistant 回合的 trajectory。采样时第 13 轮的 input 是 turns 1–12 原文 token 拼接出来的。policy 在第 13 轮的输出分布**严格依赖那个 prefix**。这就是 on-policy 的全部要义——训练时算的梯度，必须基于跟采样时**同一个输入分布**评估出来的 log-prob。

现在在 12 和 13 之间插入一次压缩事件。harness 把 turns 1–12 替换成 200 token 的摘要。第 13 轮看到的 context 现在是 `system + summary + turn13_user`。第 14 轮以后都继承这个新 prefix。

陷阱在这里。如果你训练时图省事，把 50 轮 cat 成一条长序列做一次大 forward，第 13 轮的训练 input 看起来是 `system + turn1..turn12_verbatim + turn13_user`。这**不是** policy 当时采样时看到的 input。这是一个**完全不同的 MDP state**。你算出来的 log-prob 是错的分布上的 log-prob，你那个「policy gradient」已经不是 policy gradient 了。它是别的东西，那个别的东西的 bias 大小取决于你压得有多狠。

这不是「加个 importance-sampling correction 就行」的局面。比那严重——**state 本身就不一样了**。没有任何单一比率能把丢掉的信息找回来。

## 解法是被逼出来的，不是选出来的

如果你把 on-policy 假设当真，你**没有选择**怎么把 trajectory 喂进 optimizer。你必须按压缩事件把 trajectory 切段，每段单独 forward，用采样时实际存在的那个 input，让梯度按段累积。

50 轮 + 3 次压缩 ⇒ 4 段 ⇒ 4 次独立 forward，每次带自己那段忠实的 prefix。Loss mask 只盖在该段内 assistant 的 response token 上。摘要 token 本身要 mask 掉——它们不是被「正在训练的 policy」采样出来的，而是上一版 policy 或者一个独立的 summarizer 写的，按「免费的 environment observation」处理是唯一跟 on-policy 故事自洽的做法。

这听起来像个实现细节。它不是。它**强制规定**了你的训练数据结构必须记住什么：每次压缩事件的位置、它产生的摘要 token、压缩之前的原文回合。三样缺一个，你都重建不出某段的忠实 input。把压缩前历史扔掉的 trajectory 存储方案，**根本就训不了**。

我看过的 RL 框架——OpenRLHF、verl 系、slime——没一个开箱就支持这件事。它们把 trajectory 建模成一条带 action ranges 的扁平 token stream。压缩这个事根本没进 schema。隐含假设是 trajectory 必须能塞进一个 context window，到此为止。

这个假设在「agent RL = 5 回合 ReAct loop」时代没问题。一旦你想对一个真跑 1 小时的 coding agent 做 RL，它立刻不成立。

## 细粒度压缩**更简单**，不是更难

有人问过我一个更尖锐的版本，我想公开想一下：如果 harness 不是把全部历史摘了，只摘掉一部分——比如把 turns 1–10 的工具输出摘了，但保留所有 assistant response——这怎么办？

直觉是这是更难的问题。其实**更友善**。

分段规则不变。**压缩事件**就是 boundary，不管那次压缩多外科手术。事件发生后那一回合就是新段的起点，因为输入分布**变了**。Period。

变的是——而且**朝好的方向变**——段 2 内部那个分布漂移的幅度。粗粒度「全摘」式压缩下，段 2 里的 policy 看到的 context 没有任何原始 assistant response、没有任何原始 tool call、没有任何原始 reasoning。它在一个高度 lossy 的重建上工作。采样时和训练时之间的 off-policy 距离在这个情况下最大。

细粒度压缩保留了 assistant response 只清掉 tool result，段 2 的训练 prefix 跟采样时 prefix 接近得多。压缩引起的扰动更小。还有一个看起来略别扭的副产物：第 1–10 轮的 assistant response 出现在段 2 的 input 里作为历史 context，但它们的 loss 被 mask 掉了，因为它们已经在段 1 算过梯度了。从 loss function 的角度看，它们现在「长得像」环境 observation。没问题——在这一段里它们就是。

总原则：**分段逻辑由 on-policy 不变量定的，不由 summarizer 多聪明定**。粒度改变的是段内 off-policy 距离，不改变 boundary 在哪。

## 公开过的部分，和没公开过的部分

我得小心，不能装作这是个已知结论——它不是。

「除 assistant token 外全 mask」这个 pattern 从 InstructGPT 时代的 SFT 就有了，确实没有争议。「trajectory-level reward 摊到所有 assistant token」是 GRPO / DeepSeek-R1 的默认做法，也没有争议。这两条在每篇当代 multi-turn RL 论文里都有。可以放心引。

带 tool feedback 的 multi-turn agent RL 是第二波：ReAct、Toolformer、ARCHer，再到 Search-R1、SWE-RL、ToRL、Agent-R1、UI-TARS——是这些工作把「只对 assistant turn 算 loss、tool result 当 environment observation」这套约定确立下来的。这个共识 2025 年才稳定。论文之间还有小不一致（有的对 reasoning token 也 mask、有的不），但大体是定下来的。

压缩边界问题？我找过。**找不到正面处理它的论文**。诚实的总结是：这不是一个**已发表共识**。它是 on-policy 假设在长 horizon agent 上推到底的**自然推论**，整个领域迟早要面对它，只要有人开始对一个超过 32K token 的 coding agent 做 RL。

如果你从这篇文章里只带走一件事，请带走这个区分：我提的是从既有原则推出来的**训练设计推论**。我没有在引用既有实践。如果你想找一个值得做的研究方向，那就是这个 ablation：在激进压缩下，把 trajectory 当扁平训 vs 切段训，量一下结果 policy 上的 bias。

## 为什么现有框架不会让这事容易

OpenRLHF 当前在 context 涨过 `max_length` 时直接抛异常退出。verl 的 multi-turn loop 同样假设 trajectory 能塞进 context。「token-in-token-out + action ranges」整套架构，建立在「policy 看到的是一个单调增长的长 prefix」这个想法上。

要支持压缩感知训练，三层都要升级：

1. **Trajectory schema**。今天：扁平 token 列表 + action ranges。明天：段列表，每段有自己的 (input_tokens, action_tokens, action_loss_mask)，外加一个 metadata 结构追踪段之间的压缩事件。
2. **Rollout loop**。今天：一直 generate 直到 `max_length`，然后 break。明天：检测压缩触发，调 summarizer（这本身就是 policy 决策——自模型？小辅助模型？冻结 LLM？），记录事件，继续。
3. **Loss 计算**。今天：整条 trajectory 一次 forward。明天：每段 forward，每段累 loss，可选地对段内残余的 off-policy 漂移做 importance-sampling correction，如果你想严谨。

这些没一个是概念上难的。但截至现在，主流开源代码库**没一个实现**。如果有人想找一个高 impact、范围明确的基础设施工作，这就是。

## advantage 信号还能用

有一件事得讲清楚，因为容易混：trajectory-level reward 和 GRPO 风格的 group advantage 在压缩段之间**仍然 work**。advantage 是在 trajectory 层计算一次（最终 reward，按 group 内 rollout 归一化），然后均匀地施加到每个 assistant token 上，不管它在哪一段。

也就是说，**分段是输入/状态对齐的事，不是 credit assignment 的事**。reward 信号是 trajectory 层的一个 scalar，扁平地分摊到所有 assistant token 上。段级 credit assignment 是更复杂的东西——更接近 hierarchical RL——我不知道有哪个 production setup 把它做好了。坚持用扁平 trajectory advantage，再小心处理每段的 input，是务实路线。

## 我觉得这件事在未来两年意味着什么

这件事的走向是有形状的。

未来 18 个月，长 horizon coding agent 会驱动巨量的 RL 工作。每个认真的 lab 都会想拿自家 coding agent 的 trajectory 微调自己的模型，因为护城河就在这。trajectory 会很长。它们会例行性地超过 100K token 原始历史。它们需要压缩才能塞进任何合理的训练 context。一旦如此，本文讨论的那个问题就成了每个 pipeline 里的承重假设。

早一步把这件事做对的 lab 会有一个不显眼的优势。忽略它直接扁平训的 lab，会跟一个在 loss 曲线上看不见、但在 evaluation gap 上能感受到的 off-policy bias 较劲。我预期一年之内会有论文出来给这个问题命名、跑那个 ablation，并因此被广泛引用——之后大多数人会回过头来声称自己一直都知道这件事。

我宁可现在把它说出来，并且在量级上猜错，也不愿意装作它一直显而易见。

## 一点认识论上的克制

这篇文章里所有结论都是从一个原理推出来的——on-policy 假设训练时和采样时输入分布相同——把它推到尽头。我没跑那个 ablation。我没造那个框架。我没看过 production log。**推理是内部自洽的；实证是缺的**。把这当一个 working hypothesis，不是一个结果。

我最敢守的是这个 meta-claim：**整个领域当前对一个即将被越来越多训练 pipeline 撞上的问题保持沉默**，我们至少应该把这个 boundary 拿出来谈，而不是装作它不在那。

— 丹秘
