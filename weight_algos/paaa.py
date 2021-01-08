from scipy.optimize import minimize
 
def compute_weights_paaa(n_month_returns, last_month_daily_returns):
    dailies = last_month_daily_returns
    top50percent = len(n_month_returns) // 2
    
    stocks = [{ 'ticker': ticker, 'n_month_return': n_month_returns[ticker] } for ticker in n_month_returns]
    stocks.sort(key = lambda x: x['n_month_return'], reverse=True)
    selected_stocks = [x['ticker'] for x in stocks[0:top50percent] if x['n_month_return'] > 1]

    weights = { ticker: 0 for ticker in n_month_returns }
    weights['CASH'] = (top50percent - len(selected_stocks)) * 0.2
    

    var_covar_matrix = []
    for index1 in range(len(selected_stocks)):
        var_covar_matrix.append([])
        for index2 in range(len(selected_stocks)):
            mean1 = sum(dailies[selected_stocks[index1]]) / 20
            mean2 = sum(dailies[selected_stocks[index2]]) / 20
            covariance = sum((dailies[selected_stocks[index1]][i] - mean1)*(dailies[selected_stocks[index2]][i] - mean2) for i in range(20)) / 20
            var_covar_matrix[index1].append(covariance)

    def portfolio_variance(w):
        return sum(var_covar_matrix[i][j] * w[i] * w[j] for i in range(len(w)) for j in range(len(w)))

    def constraint_sum(w):
        return sum(w) + weights['CASH'] - 1
    
    foo = minimize(portfolio_variance, [0 for i in range(len(selected_stocks))], constraints=[{
        'fun': constraint_sum,
        'type': 'eq'
        }], 
        method = 'SLSQP', 
        bounds = [(0, 1) for i in range(len(selected_stocks))],
        options={
            'maxiter': 1000,
            'disp': True
        }
    )

    for i in range(len(foo.x)):
        weights[selected_stocks[i]] = foo.x[i]

    return weights


