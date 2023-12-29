class TradingPairRecord:
    def __init__(self, symbol: str, price: float, volume: float):
        self.symbol = symbol
        self.price = price
        self.volume = volume


class Position:
    def __init__(self, symbol, ex=None, sl_order_id=None, tp_order_id=None, trailing_price_check=None):
        self.symbol = symbol
        self.execution = ex
        self.sl_order_id = sl_order_id
        self.tp_order_id = tp_order_id
        self.trailing_price_check = trailing_price_check
