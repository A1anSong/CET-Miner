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
    global CURRENT_HOUR
    global MINING_DIFF
    global CURRENT_CET_PRICE
    global TARGET_TRADING_FEE

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

    difficulty = await coinex.private_get_order_mining_difficulty()
    MINING_DIFF = float('%.2f' % float(difficulty['data']['difficulty']))

    current_cet_price = await coinex.fetch_ticker('CET/USDT')
    CURRENT_CET_PRICE = float('%.4f' % float(current_cet_price['last']))
    TARGET_TRADING_FEE = float('%.2f' % (CURRENT_CET_PRICE * MINING_DIFF))

    print('当前UTC时间（取小时位）：', CURRENT_HOUR)
    print('当前挖矿难度（CET/小时）', MINING_DIFF)
    print('当前对标CET价格', CURRENT_CET_PRICE)
    print('当前交易手续费目标（折算USDT）', TARGET_TRADING_FEE)

    await coinex.close()


async def startTrading(apiKey, secretKey):
    global TARGET_TRADING_FEE
    trading_fee_sum = 0

    coinex = ccxt.coinex({
        'apiKey': apiKey,
        'secret': secretKey,
    })

    balance = await coinex.fetch_balance()
    cet_amount = balance['CET']['free']
    if cet_amount > 1:
        await coinex.create_market_sell_order('CET/USDT', cet_amount)

    before = coinex.milliseconds()
    coinex.purge_cached_orders(before)

    while trading_fee_sum < TARGET_TRADING_FEE:
        balance = await coinex.fetch_balance()
        usdt_amount = balance['USDT']['free']
        sc_amount = balance['SC']['free']
        print('usdt:', usdt_amount, 'sc:', sc_amount)

        sc_price = await coinex.fetch_ticker('SC/USDT')
        sc_buy_price = float(sc_price['info']['buy'])
        sc_sell_price = float(sc_price['info']['sell'])
        trading_price = float('%.4f' % ((sc_buy_price + sc_sell_price) / 2))
        print('trading_price:', trading_price)

        if sc_amount * trading_price < usdt_amount * 0.1:
            buy_sc_order = await coinex.create_market_buy_order('SC/USDT', usdt_amount * 0.3)
            trading_fee_sum += buy_sc_order['fee']['cost'] * float(buy_sc_order['info']['avg_price'])
            print('计入市价买单手续费，trading_fee_sum', trading_fee_sum)
        elif sc_amount * trading_price > usdt_amount * 0.9:
            sell_sc_order = await coinex.create_market_sell_order('SC/USDT', sc_amount * 0.3)
            trading_fee_sum += sell_sc_order['fee']['cost']
            print('计入市价卖单手续费，trading_fee_sum', trading_fee_sum)
        else:
            sell_order = await coinex.create_limit_sell_order('SC/USDT', sc_amount, trading_price)
            buy_order = await coinex.create_limit_buy_order('SC/USDT', sc_amount, trading_price)
            if sell_order['status'] == 'closed':
                trading_fee_sum += sell_order['fee']['cost']
                print('计入限价卖单手续费，trading_fee_sum', trading_fee_sum)
            if buy_order['status'] == 'closed':
                trading_fee_sum += buy_order['fee']['cost'] * trading_price
                print('计入限价买单手续费，trading_fee_sum', trading_fee_sum)

        openedOrders = await coinex.fetch_open_orders('SC/USDT')
        if len(openedOrders) > 2:
            for order in openedOrders:
                await coinex.cancel_order(order['id'], 'SC/USDT')

    openedOrders = await coinex.fetch_open_orders('SC/USDT')
    for order in openedOrders:
        await coinex.cancel_order(order['id'], 'SC/USDT')

    print('撤销未成交的订单')

    await coinex.close()


if __name__ == '__main__':

    CURRENT_HOUR = None
    MINING_DIFF = None
    CURRENT_CET_PRICE = None
    TARGET_TRADING_FEE = None
    CONFIG = None

    loop = asyncio.get_event_loop()

    while True:
        current_hour = datetime.utcnow().hour
        if CURRENT_HOUR != current_hour:
            CONFIG = readUserConfig('config/apikeys.cfg')
            CURRENT_HOUR = current_hour
            loop.run_until_complete(updateMiningInfo(CONFIG.defaults()['apikey'], CONFIG.defaults()['secretkey']))
            tasks = [startTrading(CONFIG[option]['apikey'], CONFIG[option]['secretkey']) for option in
                     CONFIG.sections()]
            loop.run_until_complete(asyncio.gather(*tasks))
        time.sleep(600)
