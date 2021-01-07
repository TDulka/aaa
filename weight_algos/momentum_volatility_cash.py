def compute_weights_momentum_volatility_cash(n_month_returns, last_month_daily_returns):
    top50percent = len(n_month_returns) // 2
    
    stocks = [{ 'ticker': ticker, 'n_month_return': n_month_returns[ticker] } for ticker in n_month_returns]
    stocks.sort(key = lambda x: x['n_month_return'], reverse=True)
    
    best_half = stocks[0:top50percent]   

    weights = { ticker: 0 for ticker in n_month_returns }
    weights['CASH'] = 0 
    
    volatilities = {}
    for ticker in last_month_daily_returns:
        samplemean = sum(last_month_daily_returns[ticker]) / 20
        samplevariance = sum((x - samplemean) ** 2 for x in last_month_daily_returns[ticker]) / 20
        volatilities[ticker] = samplevariance ** 0.5 

    total_volatility_of_best = sum([ volatilities[stock['ticker']] for stock in best_half ])

    for entry in best_half:
        ticker = entry['ticker']
        if n_month_returns[ticker] > 1:
            weights[ticker] = volatilities[ticker] / total_volatility_of_best

    weights['CASH'] = 1 - sum([weights[ticker] for ticker in weights])

    return weights