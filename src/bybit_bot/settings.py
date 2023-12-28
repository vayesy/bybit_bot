import os

API_KEY = os.environ.get('BYBIT_API_KEY', '')
API_SECRET = os.environ.get('BYBIT_API_SECRET', '')
VOLUME_INCREASE_TO_TRADE = float(os.environ.get('VOLUME_INCREASE_TO_TRADE', '0.5'))
TRAILING_TP_VALUE = float(os.environ.get('TRAILING_TP_VALUE', '0.02'))
TRAILING_TP_INTERVAL = float(os.environ.get('TRAILING_TP_INTERVAL', '0.01'))
SL_VALUE = float(os.environ.get('SL_VALUE', '0.02'))
ORDER_AMOUNT = float(os.environ.get('ORDER_AMOUNT', '100'))
PRICE_LEVEL_DAYS = int(os.environ.get('PRICE_LEVEL_DAYS', '2'))
IS_TESTNET = bool(int(os.environ.get('BYBIT_TESTNET', '1')))
QUOTE_SYMBOL = 'USDT'
