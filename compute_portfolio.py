from functools import reduce

def compute_daily_returns(ticker):
    doc = open(f'./stock_prices/{ticker}.txt')
    lines = doc.readlines()
    returns = []
    for i in range(1, len(lines)):
        parts_today = lines[i].split(', ')
        price_today = parts_today[0]
        stock_split = parts_today[2]
        price_yesterday = lines[i - 1].split(', ')[0]

        returns.append(float(stock_split) * float(price_today) / float(price_yesterday))
    
    return returns

def get_normalized_returns(tickers, offset):
    returns = {}
    parallel_period = 999999

    for ticker in tickers:
        daily_returns = compute_daily_returns(ticker)
        returns_until_offset = daily_returns[0:-offset] if offset > 0 else daily_returns
        starting_point = len(returns_until_offset) % 20

        returns[ticker] = returns_until_offset[starting_point:]
        if len(returns[ticker]) < parallel_period:
            parallel_period = len(returns[ticker])

    for ticker in tickers:
        returns[ticker] = returns[ticker][-parallel_period:]

    return returns

def compute_weights(n_month_returns, last_month_daily_returns):
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

my_tickers = ['SPY', 'EZU', 'EWJ', 'EEM', 'VNQ', 'RWX', 'IEF', 'TLT', 'DBC', 'GLD']

def compute_returns(tickers, lookback_period, offset):
    returns = get_normalized_returns(tickers, offset)

    total_return = 1
    count = 0

    # start from the day for which we have enough data in past (for 6 month lookback start in day 120), iterate each month
    for day in range(20 * lookback_period, len(returns[tickers[0]]), 20):
        n_month_returns = {}
        last_month_daily_returns = {}
        next_month_returns = {}
        for ticker in tickers:
            n_month_returns[ticker] = reduce(lambda a,b: a*b, returns[ticker][day - 20 * lookback_period:day])
            last_month_daily_returns[ticker] = returns[ticker][day - 20:day]
            next_month_returns[ticker] = reduce(lambda a,b: a*b, returns[ticker][day:day + 20])

        weights = compute_weights(n_month_returns, last_month_daily_returns)

        portfolio_month_return = weights['CASH']
        for ticker in tickers:
            portfolio_month_return += weights[ticker] * next_month_returns[ticker]
        
        total_return *= portfolio_month_return
        if (portfolio_month_return > 1):
            count += 1
    
    return total_return

print(compute_returns(my_tickers, 6, 0))
