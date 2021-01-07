from scipy.optimize import minimize
 
def compute_weights_paaa(n_month_returns, last_month_daily_returns):
    dailies = last_month_daily_returns
    top50percent = len(n_month_returns) // 2
    
    stocks = [{ 'ticker': ticker, 'n_month_return': n_month_returns[ticker] } for ticker in n_month_returns]
    stocks.sort(key = lambda x: x['n_month_return'], reverse=True)
    selected_stocks = [x['ticker'] for x in stocks[0:top50percent] if x['n_month_return'] > 1]

    print(selected_stocks)

    def portfolio_variance(w):
        # print(x)

        weights = {}
        for i in range(len(w)):
            weights[selected_stocks[i]] = w[i]

        total_variance = 0
        for ticker1 in selected_stocks:
            for ticker2 in selected_stocks:
                mean1 = sum(dailies[ticker1]) / 20
                mean2 = sum(dailies[ticker2]) / 20
                covariance = sum((dailies[ticker1][i] - mean1)*(dailies[ticker2][i] - mean2) for i in range(20)) / 19

                total_variance += weights[ticker1] * weights[ticker2] * covariance
        
        return total_variance

    def constraint_sum(w):
        return sum(w) - 1.0
    
    foo = minimize(portfolio_variance, [0.3, 0.1, 0.2, 0.2, 0.2], constraints=[{
        'fun': constraint_sum,
        'type': 'eq'
        }], 
        method = 'SLSQP', 
        bounds = [(0.1,0.2),(0, 0.5),(0, 0.5),(0, 0.5),(0, 0.5)],
        options={
            'maxiter': 1000,
            'disp': True
        }
    )
    print(foo.x)

    weights_result = { ticker: 0 for ticker in n_month_returns }
    weights_result['CASH'] = (top50percent - len(selected_stocks)) * 0.2

    for i in range(len(foo.x)):
        weights_result[selected_stocks[i]] = foo.x[i]

    # print(weights_result)

    return weights_result


