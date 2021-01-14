from scipy.optimize import minimize
from qpsolvers import solve_qp
from numpy import array, dot, identity, ones, zeros
 
def compute_weights_paaa(n_month_returns, last_month_daily_returns):
    dailies = last_month_daily_returns
    days_in_month = len(dailies[list(dailies)[0]])
    top50percent = len(n_month_returns) // 2
    
    stocks = [{ 'ticker': ticker, 'n_month_return': n_month_returns[ticker] } for ticker in n_month_returns]
    stocks.sort(key = lambda x: x['n_month_return'], reverse=True)
    selected_stocks = [x['ticker'] for x in stocks[0:top50percent] if x['n_month_return'] > 1]
    number_of_selected = len(selected_stocks)

    weights = { ticker: 0 for ticker in n_month_returns }
    weights['CASH'] = (top50percent - number_of_selected) * 1 / top50percent
    
    if number_of_selected == 0:
        return weights

    var_covar_matrix = []
    for index1 in range(number_of_selected):
        var_covar_matrix.append([])
        for index2 in range(number_of_selected):
            mean1 = sum(dailies[selected_stocks[index1]]) / days_in_month
            mean2 = sum(dailies[selected_stocks[index2]]) / days_in_month
            covariance = sum(
                (dailies[selected_stocks[index1]][i] - mean1)*
                (dailies[selected_stocks[index2]][i] - mean2) 
                for i in range(days_in_month)
            ) / days_in_month
            var_covar_matrix[index1].append(covariance)

    # uses https://pypi.org/project/qpsolvers/
    P = array(var_covar_matrix)
    q = zeros(number_of_selected)
    G = identity(number_of_selected) * (-1)
    h = zeros(number_of_selected)
    A = ones(number_of_selected)
    b = array([1 - weights['CASH']]) 
    lb = zeros(number_of_selected)
    up = array([0.5 for i in selected_stocks])

    optimized_weights = solve_qp(P, q, G, h, A, b, lb, up)

    for i in range(number_of_selected):
        weights[selected_stocks[i]] = optimized_weights[i]

    return weights


