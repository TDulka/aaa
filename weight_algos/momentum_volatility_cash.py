def compute_weights_momentum_volatility_cash(n_month_returns, last_month_daily_returns):
    top50percent = len(n_month_returns) // 2
    
    array = []
    for ticker in n_month_returns:
        array.append({ 'ticker': ticker, 'n_month_return': n_month_returns[ticker]})
    array.sort(key = lambda x: x['n_month_return'], reverse=True)
    
    best_half = array[0:top50percent]   

    weights = { 'CASH': 0 }
    for ticker in n_month_returns:
        weights[ticker] = 0 
    
    volatilities = {}
    for ticker in last_month_daily_returns:
        samplemean = sum(last_month_daily_returns[ticker]) / 20
        samplevariance = sum(map(lambda x: (x - samplemean) ** 2 , last_month_daily_returns[ticker]))
        volatilities[ticker] = samplevariance ** 0.5 / 20 ** 0.5

    total_volatility_of_best = 0
    for entry in best_half:
        total_volatility_of_best += volatilities[entry['ticker']]

    for entry in best_half:
        ticker = entry['ticker']
        if n_month_returns[ticker] > 1:
            weights[ticker] = volatilities[ticker] / total_volatility_of_best

    weight_sum = 0
    for ticker in weights:
        weight_sum += weights[ticker]

    weights['CASH'] = 1 - weight_sum

    return weights