import configparser
import ccxt
from pprint import pprint


# 读取配置信息
def readUserConfig(configFile):
    config = configparser.ConfigParser()
    config.read(configFile, encoding='UTF-8')
    return config


# 主程序
if __name__ == '__main__':
    userConfig = readUserConfig('config/apikeys.cfg')
    apiKey1 = userConfig['COINEX1']['apiKey']
    secretKey1 = userConfig['COINEX1']['secretKey']
    apiKey2 = userConfig['COINEX2']['apiKey']
    secretKey2 = userConfig['COINEX2']['secretKey']
    if apiKey1 == '' or secretKey1 == '' or apiKey2 == '' or secretKey2 == '':
        print('Lost value(s) in "config/apikeys.cfg"')
        exit()
    coinex1 = ccxt.coinex({
        'api': {
            'private': {
                'get': ['balance',
                        'order',
                        'order/pending',
                        'order/finished',
                        'order/finished/{id}',
                        'order/user/deals',
                        'order/mining/difficulty',
                        ],
            },
        },
        'apiKey': apiKey1,
        'secret': secretKey1, })
    coinex2 = ccxt.coinex({
        'apiKey': apiKey2,
        'secret': secretKey2, })
    markets = coinex1.load_markets()
    pprint(coinex1.api)
    print(coinex1.private_get_order_mining_difficulty())
