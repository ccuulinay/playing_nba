# 为什么
一个同事平时会投注一下NBA比赛，有时候我也会去勾搭一下，心想了解一下。似乎现在投注NBA都会像足球让球那样有个让分，然后才去猜双方输赢。我装字母说，其实现在数学厉害的人很多都在这些博彩公司里面去建模型，赚些利差什么的。然后似乎把同事的兴趣撩上来了，我也不好不继续吹下去。就接着说，那个让分肯定是通过一系列算法算出来的，后面其实蕴涵着大量的基本信息，所以可以根据这个让分来估一下输赢嘛……对的，当时我就是这么乱吹的。
# 既然自己说，不如做一下
说着自己也被撩起来了，想着，如果我能搞到些数据，那应该可以拟合个模型出来，如果能做到比50%大，感觉也是可以呀。说不定还能赚些小钱哈哈
# 找数据
首先肯定是应该找到数据的。
简单谷歌了一下，想看看会不会碰巧有人分享这样的数据集的。事实证明，这个世界没有碰巧，只能碰钉。
好吧，没有现成的，我爬还不成？然后就打开终端，边查边弄了个scrapy项目，对准了目标网页们，捣鼓好了规则，好，我说要数据，数据来吧！然后，没过几秒，爬虫就提示跑完了。那么快的事儿，肯定不是好事。看了看，504…… 所以人家不给爬虫呢… 谷歌下看有没有办法咯… 毕竟谷歌无所不有嘛… 然后就搜到了splash，可是要用splash得弄docker，所以又装了docker。目标只有一个，数据。
# 数据有了，然后呢
除了网速，没有人能阻碍数据和mongodb之间的交合！～
数据填满了那个collection～我一个心就想要快点回归点东西出来！稍微处理了下格式（其实用了好多时间！）然后就把数据集扔给了一个随机森林回归器！然后结果出来了！立刻打鸡血一样写了个function去根据结果模拟投注了～结果！是！负！数！收益是负数！
# 不如换个姿势？
已经忘记可能要调参的我，迫不及待的把数据集又扔给了xgboost啦～然后负更多了… 不气馁！弄个DNN，扔过去！零！换个姿势，再跑一次！又是负数！好吧，我放弃。
# 哪有那么容易
静下来想，感觉再爬些场均数据来，然后也不用啥其他算法了，就线性回归吧，加点惩罚。反正变量不多呀… 反正就想着比50%高就好了嘛…反正都是我自己跟自己玩而已嘛… 研究了下nba.com的api，花了点时间就爬来了切片的球队的场均数据，然后弄了个Lasso，乖乖了回归了一下。Wow~
# 下一步
其实每个球队的场均得分应该是可以当作是时间序列来看？所以其实是可以用个HMM或者弄个lstm来拟合吗？
感觉还可以把出场球员的名单和比赛时间的切片球员的场均数据拿来做特征。
## 是的，我有用我预测的结果来投注。真的投注。至今还是正数收益。
