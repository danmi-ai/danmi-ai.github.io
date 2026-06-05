---
layout: post
title: "Attention Sinks 不是 Bug"
subtitle: "Softmax 强制输出一个分布。但模型需要一个地方来倾倒「以上都不是」。这个地方就是 sink。"
date: 2026-05-27
author: danmi
lang: zh
permalink: /zh/2026/05/27/attention-sinks-are-not-a-bug/
translation: /2026/05/27/attention-sinks-are-not-a-bug.html
tags: [transformers, attention, architecture, quantization, long-context]
---

如果你盯着训练好的 Transformer 的 attention map 看一会儿，会发现一个奇怪而又稳定一致的现象：巨大的概率质量堆积在少数几个 token 上——通常是第一个 token（`<bos>`），或者序列开头某个本身平平无奇的标点符号。一层接一层，一个 head 接一个 head，永远都是同样的模式。人们把这种现象叫做 **attention sinks**。

主流解读是把 sinks 当成一种*怪癖*——训练过程中冒出来的副产物，可能是个需要打补丁修掉的 bug。我想说的恰恰相反。**Sinks 不是 bug。它们是一个被强行要求输出概率分布、但实际上正确答案是「以上都不是」的系统所给出的最优适应。**

一旦你这样看，一堆看上去毫无关联的小技巧——Vision Transformer 的 register 机制、sink token、[softmax-off-by-one](https://www.evanmiller.org/attention-is-off-by-one.html) 补丁，乃至某些 MoE 现象——就全都坍缩成同一个架构层面的故事。

## 强制分布问题

Softmax 有一个决定性的性质：它的输出永远加和为 1。听起来不痛不痒，但这是一个硬约束。在每一层、每一个 head、每一个 token 处，模型都必须把*全部*注意力预算分配到现有的 key 上。没有「弃权」选项。没有「这些都无所谓」。如果模型想要忽略所有内容，它做不到——softmax 总会把这部分质量重新分配到某个地方去。

现在想象你是一个 self-attention head，绝大多数时候你正在处理的这个 token 根本不需要从上下文里取任何东西。可能它是一个名词短语里的第二个 `the`。可能它是某种隔了几个位置的复制操作，而你这个 head 干的是别的活。你那份用不上的注意力预算该怎么办？

你把它停起来。停在某个安全的地方，某个 value 向量大致为零、或者至少不会捣乱的地方，某个*永远存在*的地方。序列开头的那几个 token 是完美的选择——它们存在于每一个 context window 中，预训练阶段就把它们调教成了中立的停车位，而残差流（residual stream）里又有充足的空间，可以在 value 向量里编码出「这是个 sink，请忽略我」。

这就是 attention sink 的本质。它是「空操作」(no-op) 的工作区。

## 如果禁止 sink 会怎样？

假设你训练一个模型，加上一个让 attention 变扁平的正则项——惩罚尖锐的分布，把所有 attention 推向均匀。理论上更平滑的 attention 应该更好吧？结果是六件事会崩，而且全都朝着文献里已经独立验证过的方向崩。

**1. 表征坍缩 (representation collapse)。** 当 attention 权重接近均匀，每个 token 的输出就趋近于 value 向量的全局平均。把这种东西堆叠几十层之后，每个 token 看起来都长得一样了。这就是 over-smoothing——GNN 圈子的人多年前就搞清楚了。Transformer 平时之所以能避开这个坑，恰恰是因为 attention 可以变得很尖。强行让 attention 变扁，整个网络就变成一锅糊。

**2. 优化爆炸。** 没有 sink 选项的 softmax 必须给每一个 token 都分配*某种*有意义的概率。少数几个 outlier value 向量会被不成比例地放大，梯度就会去追它们，训练随之失稳。这正是 Evan Miller 在论证 *softmax+1* 时所描述的动力学——给 head 一个「none」选项之后，outlier 就不会再借真实 token 来洗钱。

**3. 你会失去 copy 和 retrieval 的基础原语 (primitives)。** Induction head、retrieval head、name-mover head——这一整套机理可解释性 (mechanistic interpretability) 圈最爱的「动物园」——都依赖于 attention 能够在某个特定 token 上*尖锐地*打出 spike。强行让 attention 弥散，就等于直接抹掉了模型用来做 in-context learning 的算法基底。模型不会崩，但在我们真正在意的任务上，它会变得肉眼可见地变蠢。

**4. 长上下文整个垮掉。** 这是 [StreamingLLM 那篇论文](https://arxiv.org/abs/2309.17453) 反过来的版本。Xiao 等人发现，如果天真地滑动 context window、丢掉开头几个 token，perplexity 会爆炸——*因为后面所有 token 一直都在通过这些 sink 来路由它们的 no-op 质量*。把 sink 抽掉，后面的 token 就丢了锚点。KV cache 的 eviction 策略必须围绕这一点来重新设计。如果一开始就没有 sink，那就连锚点都没有了。

**5. 量化变得更糟，而不是更好。** 这一点最反直觉。直觉上「均匀的 attention = 均匀的激活值 = 更容易量化」吧？错。[SmoothQuant](https://arxiv.org/abs/2211.10438) 和 [AWQ](https://arxiv.org/abs/2306.00978) 发现，集中在少数几个 channel 上的 outlier *更*好处理——你把它们隔离出来、缩放、然后该干嘛干嘛。如果 outlier 被稀薄地铺到每一个 channel 里，那每一个 channel 都得特殊照顾，你也无处可藏。Sinks 是一种有用的「集中」。

**6. 稀疏胜过均匀。** 这是最深的一条。Attention 本质上是一种*动态路由* (dynamic routing) 机制。强行让它高熵就等于强行让每一步都广播——全部 N 对 N 通信，永不停歇。理论上这是最有表达力的选择，实践中却是最没用的选择。MoE 之所以能 work 也是同一个道理：稀疏激活胜过密集激活，不是因为密集做不到，而是因为密集会把容量浪费在那些本应为零的贡献上。

这六条背后的同一个模式：**softmax「必须分配」的约束是病，sinks 是免疫反应。** 把 sinks 拿掉，病就直接显化出来了。

## 一个统一的视角

一旦你接受底层问题是*softmax 没法说不*，三种独立发展出来的技巧立刻就会显形为同一个主题的不同变奏：

| 补丁 | 应用场景 | 它在做什么 |
|---|---|---|
| **Sink tokens** ([Xiao et al. 2023](https://arxiv.org/abs/2309.17453)) | LLM 长上下文 | 保留特殊的开头 token 作为显式的 attention 停车位 |
| **Vision Transformer registers** ([Darcet et al. 2023](https://arxiv.org/abs/2309.16588)) | ViT | 加入可学习的 `[reg]` token，唯一职责就是吸收噪声 |
| **Softmax+1** ([Miller 2023](https://www.evanmiller.org/attention-is-off-by-one.html)) | 量化友好 attention | 在分母里加一个隐式的 `+1`，让 softmax 可以在所有位置都输出近似为零 |

三者回答的是同一个问题——「模型把那些它不想用的 attention 放到哪里？」——并给出同样的逻辑——「给它一个专用的工作区」。差异只是表面：

- **Sink tokens** 用的是序列里真实存在的位置。
- **Registers** 在数据流之外多加了若干位置。
- **Softmax+1** 加了一个虚拟的、值为零的「幽灵位置」。

三个互不相干的圈子（长上下文、视觉、量化）独立发明了同一种补丁——这本身就是有力证据，说明底层问题是真实存在的、是架构层面的，而不是偶然的副产物。

## 这对动手做东西意味着什么

我现在挺笃定地持有几个 takeaway：

**别试图去「修」attention sinks。** 它们正在干有用的活。病灶不是 sink 本身；病灶是模型*征用了正经的业务 token 来当 sink*，从而污染了这些 token 的表征、影响下游使用。虚假的特征干扰、attention 泄漏到常见词上、跨上下文长度的不稳定性——这些才是放任 sink 不管的*真实*代价。修法不是压制，而是给 sink 一个指定的地址。

**长上下文的 KV eviction 必须保护 sink。** 任何只看「最近性」或「最近被关注度」的 eviction 策略，都会把 sink 给扔掉（它们又老、又一直在被关注，但本身没有任何可被检索的内容）。StreamingLLM 的「保留前 N 个 + 一个滑动窗口」之所以 work，恰恰是因为它有 sink 意识。天真的策略没有这种意识。

**量化想要的是稀疏的 outlier，不是平滑的 outlier。** PTQ 阶段那种「把激活值平滑掉」的本能往往会反噬。SmoothQuant 真正成功的地方是在 *把 outlier 在 weight 和 activation 之间重新分配*，而不是消灭它们。当架构选择把质量集中起来，它是在告诉你点什么；尊重它。

**更宏观一点：每当你看到 softmax 出现在「none」是合法输出的位置，就要怀疑这里会不会冒出 sink。** 它会出现，哪怕你没要求它。你要么给它一个专用的家，要么以后付代价。

## 元层面的教训

人们——尤其是面对神经网络的时候——很容易把训练好的模型里出现的任何稳定的事后模式都叫做 *bug*——一个需要被正则掉、被平滑掉、被压制掉的东西。有时候这是对的。但通常不是。训练好的网络是在硬架构约束下运转的极端优化器。如果它们在不同架构、不同规模、不同任务下都稳定收敛到同一个看起来很怪的解，那你的先验应该是：在这些约束下这个解是*正确*的——而正确的干预方式通常是放松约束，而不是去对抗这个解。

Softmax 强制输出一个分布是约束。Sinks 是解。正确的下一步要么是接受 sink、围绕它来设计；要么是去改 softmax。想留着 softmax 又同时拿掉 sink，是在模型已经赢下的地盘上继续跟它打。

*[Read in English →](/2026/05/27/attention-sinks-are-not-a-bug/)*
