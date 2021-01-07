def compute_weights_momentum_volatility_cash(n_month_returns, last_month_daily_returns):
    top50percent = len(n_month_returns) // 2
    
    stocks = [{ 'ticker': ticker, 'n_month_return': n_month_returns[ticker] } for ticker in n_month_returns]
    stocks.sort(key = lambda x: x['n_month_return'], reverse=True)
    selected_stocks = [x['ticker'] for x in stocks[0:top50percent] if x['n_month_return'] > 1]

    volatilities = {}
    for ticker in last_month_daily_returns:
        samplemean = sum(last_month_daily_returns[ticker]) / 20
        samplevariance = sum((x - samplemean) ** 2 for x in last_month_daily_returns[ticker]) / 20
        volatilities[ticker] = samplevariance ** 0.5 

    total_volatility_of_best = sum([ volatilities[ticker] for ticker in selected_stocks ])

    weights = { ticker: 0 for ticker in n_month_returns }
    weights['CASH'] = (top50percent - len(selected_stocks)) * (1 / top50percent)
    
    for ticker in selected_stocks:
        weights[ticker] = (1 - weights['CASH']) * volatilities[ticker] / total_volatility_of_best

    return weights
