#CET挖矿机器人

感兴趣的可以使用我的邀请链接注册CoinEx：
[https://www.coinex.com/account/signup?refer_code=f93eb](https://www.coinex.com/account/signup?refer_code=f93eb)
>2018.07.07开源测试版

暂时没有空完善详细的文档，本项目暂时没有更新计划

#使用说明：
在'config/apikeys.cfg'中添加需要刷CET的小号APIKEY
例如
>[ABC]
>apiKey = ********
>secretKey = ********

可以添加多个，'ABC'是你自定义区分APIKEY的名称，意味着可以多个小号同时刷

'[DEFAULT]'是默认大号的APIKEY，也可以填小号的，主要作用是用来获取当前挖矿难度

可以刷的小号上限个数没有经过测试，取决于机器配置和网络状况

#已知BUG（暂无修复计划，有能力的可以自己更改一下代码）：
1. 计算手续费的公式有问题，原因在挂单之后没有及时获取吃单的状态
2. 时间问题，对于网络网络状态没有设计容错机制，连接断开程序会终止运行

#需要注意的地方和建议：
默认刷'SC/USDT'交易对，可以在代码里切换，筹码不足时会自动补仓，同时也意味着耗损。

理论上账户余额充足的情况下，会自动刷到目标交易手续费为止，但是余额越小耗损越大，大单交易耗损越小。使用时可以自行评估。

#Python版本
建议高于3.5版本，不要使用3.7版本，因Python 3.7版本将'async'添加为了关键字，很多库不好直接使用，会导致程序报错。

感兴趣的可以添加微信交流：
![](./WechatQR.jpeg)

或者搜索微信'xccstudio'添加，备注"量化交流"

会不断开源和优化量化投资小工具

熊市慢慢，望共勉陪伴