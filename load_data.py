import requests
import os
from datetime import date

def get_price_data(ticker, start_date, end_date):
    token = 'b042b161206797d2cbbee462c1de6d01ddf85897'
    base_URL = 'https://api.tiingo.com/tiingo'
    headers = {
        'Content-Type': 'application/json'
    }
    data = requests.get(
        f'{base_URL}/daily/{ticker}/prices?token={token}&startDate={start_date}&endDate={end_date}',  
        headers=headers
    ).json()

    return list(map(lambda x: { 'price': x['close'], 'date': x['date'], 'splitFactor': x['splitFactor'] }, data))

def store_price_data(ticker, price_data, do_rewrite):
    f = open(f'./stock_prices/{ticker}.txt', 'w' if do_rewrite else 'a')
    f.writelines(
        '{price}, {date}, {splitFactor}\n'.format(price=entry['price'], date=entry['date'][0:10], splitFactor=entry['splitFactor']) 
        for entry in price_data
    )
    f.close()

# loads data for given tickers, rewrites files in stock_prices folder
def load_historic_data():
    tickers = ['SPY', 'EZU', 'EWJ', 'EEM', 'VNQ', 'RWX', 'IEF', 'TLT', 'DBC', 'GLD']
    start_date = '1990-12-19'
    end_date = date.today()
    
    for ticker in tickers:
        price_data = get_price_data(ticker, start_date, end_date)
        store_price_data(ticker, price_data, True)

# updates data with newest prices
def add_recent_data():
    for docname in os.listdir('./stock_prices'):
        doc = open(f'./stock_prices/{docname}')
        lines = doc.readlines()
        doc.close()
        lastline = lines[-1]

        ticker = docname.split('.')[0]
        lastdate = lastline.split(', ')[1]
        today = date.today()

        new_data = get_price_data(ticker, lastdate, today)
        new_data.pop(0) # to not duplicate last date

        store_price_data(ticker, new_data, False)

add_recent_data()