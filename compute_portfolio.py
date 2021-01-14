from functools import reduce
from datetime import date
from weight_algos.momentum_equal_cash import compute_weights_momentum_equal_cash
from weight_algos.momentum_volatility_cash import compute_weights_momentum_volatility_cash
from weight_algos.paaa import compute_weights_paaa
from weight_algos.paaa_long_short import compute_weights_paaa_long_short
from weight_algos.momentum_equal_long_short import compute_weights_momentum_equal_long_short
import numpy as np
import matplotlib.pyplot as plt 

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

def get_normalized_returns(tickers, startdate, enddate, days_in_month):
    returns = {}
    parallel_period = 999999

    for ticker in tickers:
        daily_returns = compute_daily_returns(ticker, startdate, enddate)
        starting_point = len(daily_returns) % days_in_month

        returns[ticker] = daily_returns[starting_point:]
        if len(returns[ticker]) < parallel_period:
            parallel_period = len(returns[ticker])

    for ticker in tickers:
        returns[ticker] = returns[ticker][-parallel_period:]

    return returns

def compute_portfolio_returns(tickers, lookback_period, compute_weights_alg, startdate, enddate, days_in_month):
    '''Compute monthly returns of a portfolio, given a weighing algorithm.
    
    Positional arguments:
    tickers - for which stocks you want the returns computed
    lookback_period - how long in the past to look for momentum (e.g. 6 => look at 6 month momentum)
    compute_weights_alg - what function to use to calculate the weights in the portfolio each month
    startdate - take into considerations only returns starting from this date
    enddate - take into considerations only returns until this date
    days_in_month - how many days to consider being in a month
    '''
    
    returns = get_normalized_returns(tickers, startdate, enddate, days_in_month)
    portfolio_month_returns = np.ones(len(returns[tickers[0]])//days_in_month-lookback_period)

    # start from the day for which we have enough data in past (for 6 month lookback start in day 120), iterate each month
    for day in range(days_in_month * lookback_period, len(returns[tickers[0]]), days_in_month):
        n_month_returns = {}
        last_month_daily_returns = {}
        next_month_returns = {}
        for ticker in tickers:
            n_month_returns[ticker] = reduce(lambda a,b: a*b, returns[ticker][day - days_in_month * lookback_period:day])
            last_month_daily_returns[ticker] = returns[ticker][day - days_in_month:day]
            next_month_returns[ticker] = reduce(lambda a,b: a*b, returns[ticker][day:day + days_in_month])

        weights = compute_weights_alg(n_month_returns, last_month_daily_returns)
        portfolio_month_return = weights['CASH']
        for ticker in tickers:
            portfolio_month_return += weights[ticker] * next_month_returns[ticker]
        
        portfolio_month_returns[day//days_in_month-lookback_period] = portfolio_month_return

    return portfolio_month_returns


def compute_cumulated_returns(portfolio_month_returns):
    cumulated_returns = np.cumprod(portfolio_month_returns)
    count = np.sum(portfolio_month_returns>1)
    
    return cumulated_returns, count

def compute_final_return(portfolio_month_returns):
    returns,_ = compute_cumulated_returns(portfolio_month_returns)
    plt.plot(returns)
    return returns[-1]

def get_day_strings():
    '''Generates a list of strings from "01" to "31" to be used as possible days.'''
    return ['0' + str(j) for j in range(1, 10)] + [str(j) for j in range(10, 32)]

my_tickers = ['SPY', 'EZU', 'EWJ', 'EEM', 'VNQ', 'RWX', 'IEF', 'TLT', 'DBC', 'GLD']

np.set_printoptions(precision=16)

for day in get_day_strings():
    returns_for_endday = compute_portfolio_returns(
        my_tickers, 6, compute_weights_paaa_long_short, '2006-12-19', '2020-12-%s' % day, 20
    )
    compute_final_return(returns_for_endday)

plt.show()