def compute_weights_momentum_equal_cash(n_month_returns, last_month_daily_returns):
    top50percent = len(n_month_returns) // 2
    weight = 0.2
    
    array = []
    for ticker in n_month_returns:
        array.append({ 'ticker': ticker, 'n_month_return': n_month_returns[ticker]})
    array.sort(key = lambda x: x['n_month_return'], reverse=True)
    
    best_half = array[0:top50percent]   

    weights = { 'CASH': 0 }
    for ticker in n_month_returns:
        weights[ticker] = 0 

    for entry in best_half:
        ticker = entry['ticker']
        if n_month_returns[ticker] > 1:
            weights[ticker] = weight
        else:
            weights['CASH'] += weight

    return weights
