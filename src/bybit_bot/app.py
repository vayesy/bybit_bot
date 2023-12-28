import time
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from pybit.unified_trading import HTTP, WebSocket

from . import settings
from .helper_classes import TradingPairRecord, Position
from .http_api_helpers import get_spot_only_coins, get_spot_daily_candle, place_spot_order, cancel_order, update_order


class App:
    def __init__(self):
        self.http: Optional[HTTP] = None
        self.public_ws: Optional[WebSocket] = None
        self.private_ws: Optional[WebSocket] = None
        self.pair_records: Dict[str, TradingPairRecord] = {}
        self.open_positions: Dict[str, Position] = {}
        self.trailing_tp_orders: Dict[str, {}] = {}

    def update_last_prices(self, coins: List[str]):
        e = ThreadPoolExecutor()
        tasks = {}
        for coin in coins:
            symbol = coin + settings.QUOTE_SYMBOL
            tasks[e.submit(get_spot_daily_candle, self.http, symbol, settings.PRICE_LEVEL_DAYS)] = symbol
        empty_markets = []
        for task in as_completed(tasks):
            symbol = tasks[task]
            try:
                res = task.result()
            except Exception:
                print('Failed to get klines for symbol {}'.format(symbol))
                continue
            coin = symbol[0:-len(settings.QUOTE_SYMBOL)]
            if res == []:
                empty_markets.append(coin)
                coins.remove(coin)
                continue
            row = max((record for record in res), key=lambda r: float(r[2]))
            if float(row[6]) == 0:
                # skip coin without volume
                empty_markets.append(coin)
                coins.remove(coin)
                continue
            self.pair_records[symbol] = TradingPairRecord(symbol, float(row[2]), float(row[6]))
        if empty_markets:
            print('Markets for next coins have no volume for last days: {}'.format(', '.join(sorted(empty_markets))))
        e.shutdown(wait=True, cancel_futures=True)
        return len(coins) == len(self.pair_records)

    def on_price_update_with_position(self, position: Position, symbol: str, price: float):
        if price < position.trailing_price_check:
            return
        new_tp_price = price * (1 + settings.TRAILING_TP_VALUE)
        res = update_order(self.http, symbol, position.tp_order_id, new_tp_price)
        position.tp_order_id = res['result']['orderId']
        position.trailing_price_check = price * (1 + settings.TRAILING_TP_INTERVAL)
        print('Updating TP price for {} symbol to {}'.format(symbol, new_tp_price))

    def on_price_update_without_position(self, symbol: str, price: float, volume: float):
        record = self.pair_records[symbol]
        if price > record.price and volume >= record.volume * (1 + settings.VOLUME_INCREASE_TO_TRADE):
            # create order
            linked_id = '{}-{}'.format(symbol, 'enter')
            order = place_spot_order(self.http, symbol, 'BUY', settings.ORDER_AMOUNT, linked_id=linked_id)
            if order is None:
                print('Failed to place order for {} symbol'.format(symbol))
                return
            print('Placed market order for {} symbol'.format(symbol))
            self.open_positions[symbol] = Position(symbol)

    def on_ticker(self, data: dict):
        d = data['data']
        symbol = d['symbol']
        price = float(d['lastPrice'])
        position = self.open_positions.get(symbol)
        if position:
            # check price and if needed, update TP order
            self.on_price_update_with_position(position, symbol, price)
        else:
            volume = float(d['turnover24h'])
            self.on_price_update_without_position(symbol, price, volume)

    def on_open_position(self, position: Position, symbol: str, data: dict):
        position.execution = data
        # add TP/SL orders
        price = float(data['execPrice'])
        position.trailing_price_check = price * (1 + settings.TRAILING_TP_INTERVAL)
        sl_price = price * (1 - settings.SL_VALUE)
        tp_price = price * (1 + settings.TRAILING_TP_VALUE)
        sl = place_spot_order(self.http, symbol, 'Sell', float(data['execQty']), sl_price, '{}-{}'.format(symbol, 'sl'))
        tp = place_spot_order(self.http, symbol, 'Sell', float(data['execQty']), tp_price, '{}-{}'.format(symbol, 'tp'))
        position.sl_order_id = sl['result']['orderId']
        position.tp_order_id = tp['result']['orderId']
        print('Placed TP/SL orders for {} symbol'.format(symbol))

    def on_execution(self, data: dict):
        d = data['data']
        if d['category'] != 'spot':
            return
        link_id = d.get('orderLinkId')
        if not link_id:
            return
        link_parts = link_id.split('-')
        if len(link_parts) != 2:
            print('Linked order id is not recognized {}'.format(link_id))
            return
        symbol = d['symbol']
        position = self.open_positions.get(symbol)
        if not position:
            print('Not found position for execution update {}'.format(symbol))
            return
        order_type = link_parts[1]
        if order_type == 'enter':
            # place SL & TP orders
            self.on_open_position(position, symbol, d)
        elif order_type == 'sl':
            cancel_order(self.http, symbol, position.tp_order_id)
        elif order_type == 'tp':
            cancel_order(self.http, symbol, position.sl_order_id)

    def run(self):
        # check settings first
        if not self.are_settings_valid():
            print('Some of the required configs are not provided')
            return 1
        kwargs = dict(testnet=settings.IS_TESTNET)
        self.http = HTTP(**kwargs)
        trading_pairs = get_spot_only_coins(self.http, settings.QUOTE_SYMBOL)
        if not trading_pairs:
            print('Trading pairs are empty')
            return 1
        if not self.update_last_prices(trading_pairs):
            print('Failed to fetch latest price and volume data')
            return 1
        print('Processing {} markets'.format(', '.join(self.pair_records)))
        kwargs.update(dict(channel_type='spot'))
        self.public_ws = WebSocket(**kwargs)
        kwargs.update(dict(api_key=settings.API_KEY, api_secret=settings.API_SECRET, channel_type='private'))
        self.private_ws = WebSocket(**kwargs)
        self.public_ws.ticker_stream(list(self.pair_records), self.on_ticker)
        self.private_ws.execution_stream(self.on_execution)

        # streams are working in separate thread
        while True:
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                break
        self.public_ws.exit()
        self.private_ws.exit()

    def are_settings_valid(self) -> bool:
        return len(settings.API_KEY) > 0 and len(settings.API_SECRET) > 0
