from functools import reduce
from datetime import date
from weight_algos.momentum_equal_cash import compute_weights_momentum_equal_cash
from weight_algos.momentum_volatility_cash import compute_weights_momentum_volatility_cash
from weight_algos.paaa import compute_weights_paaa

def compute_daily_returns(ticker, startdate, enddate):
    doc = open(f'./stock_prices/{ticker}.csv')
    lines = doc.readlines()
    returns = []
    for i in range(1, len(lines)):
        parts_today = lines[i].split(', ')
        price_today = parts_today[0]
        stock_split = parts_today[2]
        price_yesterday = lines[i - 1].split(', ')[0]

        date_today = date.fromisoformat(parts_today[1])

        if (date_today >= date.fromisoformat(startdate) and date_today <= date.fromisoformat(enddate)):
            returns.append(float(stock_split) * float(price_today) / float(price_yesterday))
    
    return returns

def get_normalized_returns(tickers, startdate, enddate):
    returns = {}
    parallel_period = 999999

    for ticker in tickers:
        daily_returns = compute_daily_returns(ticker, startdate, enddate)
        starting_point = len(daily_returns) % 20

        returns[ticker] = daily_returns[starting_point:]
        if len(returns[ticker]) < parallel_period:
            parallel_period = len(returns[ticker])

    for ticker in tickers:
        returns[ticker] = returns[ticker][-parallel_period:]

    return returns

def compute_returns(tickers, lookback_period, compute_weights_alg, startdate, enddate):
    returns = get_normalized_returns(tickers, startdate, enddate)

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

        weights = compute_weights_alg(n_month_returns, last_month_daily_returns)

        portfolio_month_return = weights['CASH']
        for ticker in tickers:
            portfolio_month_return += weights[ticker] * next_month_returns[ticker]
        
        total_return *= portfolio_month_return
        if (portfolio_month_return > 1):
            count += 1
    
    return total_return

# EDIT WHAT YOU WANT HERE
my_tickers = ['SPY', 'EZU', 'EWJ', 'EEM', 'VNQ', 'RWX', 'IEF', 'TLT', 'DBC', 'GLD']
# compute_returns takes arguments:
# tickers for which you want the returns computed
# how long in the past to look for momentum (e.g. 6 => look at 6 month momentum)
# what function (algorithm) to use to calculate the weights in the portfolio each month
# boundaries for starting date and ending date of the period in which you are interested in
print(compute_returns(my_tickers, 6, compute_weights_paaa, '2006-12-19', '2020-12-31'))
