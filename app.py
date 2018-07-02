import configparser
import asyncio
import ccxt.async as ccxt
from datetime import datetime
import time


def readUserConfig(configFile):
    config = configparser.ConfigParser()
    config.read(configFile, encoding='UTF-8')
    return config


async def updateMiningInfo(apiKey, secretKey):
    coinex = ccxt.coinex({
        'api': {
            'private': {
                'get': [
                    'balance',
                    'order',
                    'order/pending',
                    'order/finished',
                    'order/finished/{id}',
                    'order/mining/difficulty',
                ],
            },
        },
        'apiKey': apiKey,
        'secret': secretKey,
    })

    result = await coinex.private_get_order_mining_difficulty()
    if result['code'] == 0:
        global MINING_DIFF
        MINING_DIFF = result['data']['difficulty']
    else:
        print(result['code'], result['message'])

    await coinex.close()


async def startTrading(apiKey, secretKey):
    print(1, apiKey)
    await asyncio.sleep(1)
    print(2, secretKey)


if __name__ == '__main__':

    CURRENT_HOUR = None
    MINING_DIFF = None

    config = readUserConfig('config/apikeys.cfg')

    loop = asyncio.get_event_loop()

    while True:
        current_hour = datetime.utcnow().hour
        if CURRENT_HOUR != current_hour:
            if current_hour == 0 or CURRENT_HOUR is None:
                loop.run_until_complete(updateMiningInfo(config.defaults()['apikey'], config.defaults()['secretkey']))
            CURRENT_HOUR = current_hour
            tasks = [startTrading(config[option]['apikey'], config[option]['secretkey']) for option in
                     config.sections()]
            loop.run_until_complete(asyncio.gather(*tasks))
        print(CURRENT_HOUR)
        print(MINING_DIFF)
        time.sleep(60)
