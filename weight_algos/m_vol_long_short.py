def compute_weights_m_vol_long_short(n_month_returns, last_month_daily_returns):
    top50percent = len(n_month_returns) // 2
    days_in_month = len(last_month_daily_returns[list(last_month_daily_returns)[0]])

    stocks = []
    for ticker in n_month_returns:
        mean = sum(last_month_daily_returns[ticker]) / days_in_month
        volatility = (sum((x - mean) ** 2 for x in last_month_daily_returns[ticker]) / days_in_month) ** 0.5
        stocks.append({
            'ticker': ticker,
            'n_month_return': n_month_returns[ticker],
            'volatility': volatility
        })

    stocks.sort(key = lambda x: x['n_month_return'], reverse=True)

    target_volatility = 0.036 / len(stocks)

    weights = {}

    total_weight = 0
    for stock in stocks[:top50percent]:
        weight = target_volatility / stock['volatility']
        total_weight += weight
        weights[stock['ticker']] = weight

    for stock in stocks[top50percent:]:
        weight = -target_volatility / stock['volatility']
        total_weight += weight
        weights[stock['ticker']] = weight
     
    weights['CASH'] = 1 - total_weight

    return weights
