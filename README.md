# Bybit bot
Simple trading bot on Bybit spot for coins, that are not present on the futures.  
Opens position when price gets higher than max of previous days and volume increases.

## Run
`python -m bybit_bot`

## Configuration
All configs can be provided as environment variables or put to `.env` file in the project root or `src` folder.  
Available configs:
* `BYBIT_API_KEY` - API key to access Bybit endpoints;
* `BYBIT_API_SECRET` - API secret to access Bybit endpoints;
* `VOLUME_INCREASE_TO_TRADE` - relative amount of volume change compared to prev days to open a trade. For example, `0.5` means enter trade if volume increased 50%. Default value `0.5`;
* `TRAILING_TP_VALUE` - relative TP for the position as change in percents. For example, `0.02` means set TP as current price + 2%. Default value `0.02`;
* `TRAILING_TP_INTERVAL` - how often trailing TP should be updated, as price change percentage. For example, `0.01` means TP will be updated every 1% change in price. Default value `0.01`;
* `SL_VALUE` - relative SL value, works same as TP but without trailing logic. Default value `0.02`;
* `ORDER_AMOUNT` - amount in base currency (USDT) to enter single trade with. Default value is `100`;
* `BYBIT_TESTNET` - should testnet env be used (`1`) or not (`0`). Default value is `1`;
* `PRICE_LEVEL_DAYS` - how many previous days to fetch prices for. Default value is `2`.
