from datetime import timedelta, date
import numpy as np
import matplotlib.pyplot as plt 

def get_daily_prices(ticker):
    '''Load daily prices for the given ticker.
    
    Normalize by stock splits, to undo jumps they make. 
    Return a dictionary with dates as keys and prices as values.'''

    doc = open(f'./stock_prices/{ticker}.csv')
    lines = doc.readlines()

    daily_prices = {}
    current_split_ratio = 1

    for i in range(0, len(lines)):
        parts_today = lines[i].split(', ') # read the information for a given date
        price_today = float(parts_today[0])
        date_today = parts_today[1]
        stock_split = float(parts_today[2])

        if stock_split != 1: # store split ratio, from this day on all prices are affected by the split
            current_split_ratio *= stock_split

        daily_prices[date_today] = price_today * current_split_ratio
    
    return daily_prices

def get_daily_stats(tickers, start, end):
    '''Get prices for given tickers and a given date range.
    
    Returns a list like this:
    daily_stats = [{
        'date': '2020-12-31',
        'SPY': 100,
        'EWJ': 10,
        'EZU': 3
    }]
    Only returns stats for days when all stocks have a price (were listed).'''

    daily_stats = []

    start_date = date.fromisoformat(start)
    end_date = date.fromisoformat(end)
    delta = end_date - start_date # compute the length of interval in days over which to iterate

    stock_prices = list(map(lambda ticker: get_daily_prices(ticker), tickers)) # get prices for each ticker

    for i in range(delta.days + 1):
        current_date = str(start_date + timedelta(i))

        # Stupidly check each day if prices are finally available for all stocks
        all_prices_available = True
        for prices in stock_prices:
            if not current_date in prices:
                all_prices_available = False

        if all_prices_available:
            current_day_stats = { 'date': current_date }
            for i in range(len(tickers)):
                current_day_stats[tickers[i]] = stock_prices[i][current_date]
            
            daily_stats.append(current_day_stats)

    return daily_stats


my_tickers = ['SPY', 'QQQ', 'MDY', 'IWM', 'FEZ', 'EWJ', 'EEM', 'EFA', 'SCZ', 'IYR', 'RWX', 'DBE', 'GLD', 'TLT', 'IEF', 'IEI', 'SHY', 'JNK', 'EMB']
daily_stats = get_daily_stats(my_tickers, '2000-01-01', '2016-09-01')
momentum_length = 120

# Will keep track of what is currently in portfolio
# Dictionary like { 'SPY': 10, 'EEM': 3.4 } means we have 10 stocks of SPY and 3.4 stocks of EEM
portfolio = dict([(ticker, 0) for ticker in my_tickers])
portfolio['CASH'] = 2.71

cash_at_rebalancing_dates = []
rebalancing_dates = []
day_index = 1 # will track if rebalancing on this day should happen

for i in range(len(daily_stats)):
    todays_prices = daily_stats[i]

    if i < momentum_length:
        continue

    if day_index == 20:
        # rebalance porfolio
        cash_available = portfolio['CASH'] 
        for ticker in my_tickers:
            cash_available += portfolio[ticker] * todays_prices[ticker] 
            portfolio[ticker] = 0 # sell everything

        cash_at_rebalancing_dates.append(cash_available)
        rebalancing_dates.append(todays_prices['date'])

        # figure out what to buy based on momentum
        momenta = [todays_prices[ticker] / daily_stats[i - momentum_length][ticker] for ticker in my_tickers]
        cutoff = np.percentile(momenta, 50)
        
        cash_for_one_stock = cash_available / len(list(filter(lambda x: x > cutoff, momenta)))

        for j in range(len(my_tickers)):
            ticker = my_tickers[j]
            if momenta[j] > cutoff:
                portfolio[ticker] = cash_for_one_stock / todays_prices[ticker]
        
        portfolio['CASH'] = 0

        day_index = 1
    
    day_index += 1


current_value = 0
for ticker in my_tickers:
    current_value += portfolio[ticker] * daily_stats[-1][ticker]

print(current_value)

np.set_printoptions(precision=16)
plt.xticks(np.arange(8,len(rebalancing_dates),10),rebalancing_dates[8::10],rotation=45)
plt.plot(np.log(cash_at_rebalancing_dates))
plt.show()
    




