import pandas as pd
from matplotlib import pyplot as plt
from .data import get_etf_data

def plot_cumulative_returns(time_return):
    """
    Plot a comparison of two cumulative returns:
    1. Cumulative return of price_panel['510300'] (based on price)
    2. Cumulative return of time_return (based on daily returns)

    Parameters:
        time_return (dict): Keys are datetime objects, values are daily returns as decimals (e.g., 0.005 for 0.5%)
    """
    # Convert time_return to a sorted pandas Series
    returns_series = pd.Series(time_return)
    returns_series.index = pd.to_datetime(returns_series.index)

    # Determine the time range of time_return
    start_date = returns_series.index[0]
    end_date = returns_series.index[-1]

    # Slice price_panel to match the time range of time_return
    benckmark = get_etf_data('510300')
    price_subset = benckmark['close'].loc[start_date:end_date]

    # Calculate cumulative return for price_subset (based on price changes)
    cumulative_price = (price_subset / price_subset.iloc[0] - 1) * 100  # Convert to percentage

    # Calculate cumulative return for time_return (based on compound returns)
    cumulative_time_return = (1 + returns_series).cumprod() - 1
    cumulative_time_return = cumulative_time_return * 100  # Convert to percentage

    # Plotting
    plt.figure(figsize=(12, 6))
    plt.plot(cumulative_price.index, cumulative_price.values, label='510300 Cumulative Return', color='orange', linestyle='--')
    plt.plot(cumulative_time_return.index, cumulative_time_return.values, label='Strategy Cumulative Return', color='blue')

    # Set plot styles
    plt.title('Comparison of 510300 and Strategy Cumulative Returns')
    plt.xlabel('Date')
    plt.ylabel('Cumulative Return (%)')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()
