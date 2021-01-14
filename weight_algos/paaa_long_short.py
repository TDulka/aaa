from qpsolvers import solve_qp
from numpy import array, dot, identity, ones, zeros, transpose

def compute_weights_paaa_long_short(n_month_returns, last_month_daily_returns):
    dailies = last_month_daily_returns
    days_in_month = len(dailies[list(dailies)[0]])
    half = len(n_month_returns) // 2
    
    stocks = [{ 
        'ticker': ticker, 
        'n_month_return': n_month_returns[ticker]
    } for ticker in n_month_returns]
    stocks.sort(key = lambda x: x['n_month_return'], reverse=True)
    number_of_stocks = len(n_month_returns)

    weights = { ticker: 0 for ticker in n_month_returns }

    var_covar_matrix = []
    for index1 in range(number_of_stocks):
        var_covar_matrix.append([])
        for index2 in range(number_of_stocks):
            mean1 = sum(dailies[stocks[index1]['ticker']]) / days_in_month
            mean2 = sum(dailies[stocks[index2]['ticker']]) / days_in_month
            covariance = sum(
                (dailies[stocks[index1]['ticker']][i] - mean1)*
                (dailies[stocks[index2]['ticker']][i] - mean2) 
                for i in range(days_in_month)
            ) / days_in_month
            var_covar_matrix[index1].append(covariance)

    # uses https://pypi.org/project/qpsolvers/
    P = array(var_covar_matrix)
    q = zeros(number_of_stocks)
    A = ones(number_of_stocks)
    b = array([1]) 
    lb = array([0 for i in range(half)] + [-0.3 for i in range(half)])
    ub = array([0.3 for i in range(half)] + [0 for i in range(half)])

    optimized_weights = array(solve_qp(P, q, A = A, b = b, lb = lb, ub = ub))

    total_stock_weight = 0

    for i in range(number_of_stocks):
        w = round(optimized_weights[i], 5)
        weights[stocks[i]['ticker']] = w
        total_stock_weight += w

    weights['CASH'] = 1 - total_stock_weight

    return weights


