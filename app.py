import configparser
import ccxt


def readUserConfig(configFile):
    config = configparser.ConfigParser()
    config.read(configFile, encoding='UTF-8')
    return config


if __name__ == '__main__':
    userConfig = readUserConfig('config/apikeys.cfg')
    apiKey = userConfig['OKEX']['apiKey']
    secretKey = userConfig['OKEX']['secretKey']
    if apiKey == '' or secretKey == '':
        print('Lost value(s) in "config/apikeys.cfg"')
        exit()
    coinex = ccxt.coinex({
        'apiKey': apiKey,
        'secret': secretKey, })
    markets = coinex.load_markets()
    print(coinex.has['withdraw'])
