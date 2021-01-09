def compute_weights_all_equal(n_month_returns, last_month_daily_returns):
    weights = dict([(ticker, 1 / len(n_month_returns)) for ticker in n_month_returns])
    weights['CASH'] = 0

    return weights