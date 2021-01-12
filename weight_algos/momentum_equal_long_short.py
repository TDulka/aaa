def compute_weights_momentum_equal_long_short(n_month_returns, last_month_daily_returns):
    top50percent = len(n_month_returns) // 2
    weight = 1 / top50percent
    
    stocks = [{ 'ticker': ticker, 'n_month_return': n_month_returns[ticker] } for ticker in n_month_returns]
    stocks.sort(key = lambda x: x['n_month_return'], reverse=True)
    
    top_stocks = [x['ticker'] for x in stocks[0:top50percent]]

    weights = dict([
        (ticker, weight) if ticker in top_stocks 
        else (ticker, -weight) 
        for ticker in n_month_returns
    ])

    weights['CASH'] = 1
 
    return weights
