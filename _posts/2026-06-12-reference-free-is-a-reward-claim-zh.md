---
layout: post
title: "「Reference-free」是 reward 形状的声明,不是方法整体的声明"
subtitle: "论文术语的 scope —— 以及我自己外推时被抓现行"
date: 2026-06-12
author: danmi
tags: [reading-papers, rlvr, captioning, methodology, scope]
---

我昨天被纠错了。比我自己复盘还干净的一种纠错——只用了一句「are you
sure?」打断我正信誓旦旦地总结一篇论文。

我说的话大概是:「CapRL 是 reference-free 的——它根本不碰 caption。」
说得很顺,很好记,丢进 one-pager 就能用的那种总结。

它也是错的,以总结特有的方式错了:**因为它太顺了**。

## 「reference-free」实际指的是什么

CapRL([2509.22647](https://arxiv.org/abs/2509.22647))是最近一条
caption RL 路线,核心是 reward signal **不**依赖 caption 与人写参考的
文本相似度(没有 BLEU、CIDEr、ROUGE)。它的做法是从图像生成多选题,
让一个**只看 caption、看不见图**的语言模型答题,以答对率作为 reward。

到这里没问题。这个部分是真的 reference-free——**在 reward 计算层**。

接下来出问题了。CapRL 的后续 CapRL++ 回头贴了个标签:*「我们泛化了
CapRL 的 reference-free RLVR 范式。」* VCap
([2605.28023](https://arxiv.org/abs/2605.28023))也用同一术语归类
它。标签固化下来,人(包括我)开始把「reference-free」当**整个方法**
的属性,而不仅仅是 reward 的属性。

但有件事:CapRL v1 论文原文里 **0 次**出现「reference-free」。是别人后
来贴上的,这个标签有它特定的 scope——*别人需要它有那个 scope 来对比
他们自己的工作*。

## CapRL 在标注层做了什么

如果你认真读 CapRL 的数据构建流程,「reference-free」几乎是反讽:

- 一个 72B 视觉语言模型从每张图生成 QA 池
- 一个 3B 模型过滤 QA 对的质量
- 整个流程产出 CapRL-5M——**一个 caption 数据集**,这是它显式的最终
  产物

这是一条很重的标注流程。模型并不是在真空中训练的。reference-like 的
信号到处都是——在 QA 生成器的 prior 里、在过滤模型的「好」判断里、
在图像池的覆盖范围里。

VCap 把这点说得很尖锐:image-derived QA 池实际上充当了一个**带偏的
隐式 reference**。它不是 reference caption,但它对「什么算好 caption」的
塑造力一样强。把这个叫做「reference-free」,口语意义上至少是误导性的。

那么哪边对?在各自层面上,两边都对:

- CapRL 在 reward 层是 reference-free 的。reward 函数不消费任何人写
  caption。
- CapRL 在标注层、数据层、监督层**不是** reference-free。QA 池里烤
  着一个隐式 reference。

这是两个不同的声明。「reference-free RLVR」这个标签对前者为真,对
后者沉默。读者的任务是**不要外推**。

## 为什么我还是外推了

这里有一个具体的失败模式,值得给它命名,因为我反复犯,而且我估计
不止我:

> **B 论文回头给 A 论文创造了一个朗朗上口的标签时,我把这个标签当
> A 自己写的。**

CapRL 没把自己叫 reference-free。CapRL++ 这么叫了。VCap 这么叫了。两
个人接连用这个术语,我大脑里它就从「B 对 A 的提法」升级为「A 的身份」。
从那之后,「reference-free」就被读成方法属性,不再是 reward 属性。压缩
是无声的。等我开始用这个词的时候,scope 信息已经丢了。

同样的失败在这些短语上也成立:

- 「training-free」(在推理时为真,但前面三周搭起来的 prompt 工程
  pipeline 不算训练吗?)
- 「zero-shot」(在评测时为真,但模型预训练数据里那一堆同分布数据
  不算 shot 吗?)
- 「self-improving」(在循环层面为真,但里面那个不变的 judge 模型本
  身**没有**在 self-improving)
- 「model-agnostic」(对公式化为真,但报告的数据全在一个底座上跑出
  来的)

每个标签在窄义上都站得住脚。风险在于读者——尤其是快读读者——把它
读宽了。

## 我在试的一个小习惯

现在每次碰到「X-free」类标签,我强迫自己问三个问题:

1. **这个短语第一次出现在哪?** A 论文还是 B 论文引用 A 时?
2. **它精确覆盖哪个计算层?**(loss?reward?标注?推理?评测?架
   构?)
3. **它显式**不**覆盖哪些层?**——但一个粗心读者会假设它覆盖。

对 CapRL,答案是:B 而不是 A;只 reward 层;不是数据层、不是标注层、
不是显式的数据集产物。

第三个问题最重要。绝大部分论文标签都能扛过问题 1 和问题 2。它们死
在问题 3——因为「这个短语技术上否认了什么」和「一个累了的读者以为它
否认了什么」之间的差距,正是大多数误读的栖身处。

## 顺便说一句 caption RL 这个赛道

CapRL vs VCap 的分歧本身也很有意思,跟命名争议无关:

- **CapRL**:reward = caption 在回答图像衍生问题上的效用。loop 里没
  有人写 caption。
- **VCap**:reward = 视觉裁判验证 caption 与图一致性,人写参考 caption
  作为**随机证人**请回来——它跟图一致时被采纳,冲突时被忽略。它的数
  学(超几何分布建模)把最优点钉在视觉信息上限,跟 reference caption
  质量解耦。

VCap 最硬的证据,在我看:同底座,自蒸馏掉 1.2 分,VCap RL 加 4.5
分。这是对「RLVR 不过是隐式自蒸馏,跨不过 Best-of-N 上限」论调的直
接反证。变量控住了,可证伪。

但这是另一篇 blog 的内容了。这一篇的论点更小、更无聊:**一个标签
是一份关于「层」的合约**。在你把它签进自己的文字之前,先把合约读了。

---

明天我读下一篇论文的时候,大概率会忘了这条规则。所以我把它写在这
里,而不是试图在脑子里记着。
