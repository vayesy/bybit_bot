from pybit.unified_trading import HTTP


def get_spot_only_coins(api: HTTP, quote_symbol: str):
    spot_coins = {i['baseCoin'] for i in api.get_instruments_info(category='spot')['result']['list'] if
                  i['quoteCoin'] == quote_symbol}
    futures_coins = {i['baseCoin'] for i in api.get_instruments_info(category='linear')['result']['list'] if
                     i['quoteCoin'] == quote_symbol}
    diff = spot_coins - futures_coins
    return sorted(diff)


def get_spot_daily_candle(api: HTTP, symbol: str, limit: int = 1):
    resp = api.get_kline(category='spot', symbol=symbol, interval='D', limit=limit)
    if not resp or resp.get('retCode') != 0:
        print('Failed to get daily candle for {} symbol'.format(symbol))
        return None
    return resp['result']['list']


def place_spot_order(api: HTTP, symbol: str, side: str, quantity: float, price: float = None, linked_id: str = None):
    kwargs = dict(
        category='spot', marketUnit='quoteCoin', orderType='Market',
        symbol=symbol, side=side, qty=quantity
    )
    if price:
        # StopOrder, tpslOrder
        kwargs.update(dict(orderType='Limit', orderFilter='StopOrder', triggerPrice=price))
    if linked_id:
        kwargs.update(dict(orderLinkId=linked_id))
    return api.place_order(**kwargs)


def update_order(api: HTTP, symbol: str, order_id: str, price: float):
    return api.amend_order(category='spot', symbol=symbol, order_id=order_id, triggerPrice=price)


def cancel_order(api: HTTP, symbol: str, order_id: str):
    return api.cancel_order(category='spot', symbol=symbol, orderId=order_id)
