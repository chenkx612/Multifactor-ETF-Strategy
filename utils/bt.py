import os.path
import pandas as pd
import backtrader as bt

def _create_cerebro(cash=20000, comm=0.001):
    cerebro = bt.Cerebro()
    cerebro.broker.setcash(cash)
    cerebro.broker.setcommission(comm)
    return cerebro

def add_data(cerebro, codes=[], start_date='2025-01-01', end_date='2025-06-01'):
    """加载股票数据至cerebro"""
    if not codes:
        codes = pd.read_csv('data/deduplicate_etfs.csv')['代码'].to_list()
        codes = list(map(str, codes))

    for c in codes:
        path = os.path.join('data', 'etf', c+'.csv')
        data = pd.read_csv(path, index_col=0, parse_dates=['datetime'])
        data = data.loc[start_date:end_date] 
        data = bt.feeds.PandasData(dataname=data)
        cerebro.adddata(data, name=c)

def backtest(strategy, codes=[], start_date='2025-01-01', end_date='2025-06-01', 
             benchmark_path='data/etf/510300.csv', verbose=True, **kwargs):
    cerebro = _create_cerebro()

    add_data(cerebro, codes=codes, start_date=start_date, end_date=end_date)  

    cerebro.addstrategy(strategy, **kwargs)
    cerebro.addanalyzer(bt.analyzers.Returns, _name="returns")
    if verbose:
        cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="ta")
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name="drawdown")
        cerebro.addanalyzer(bt.analyzers.TimeReturn, _name="time_return")

    result = cerebro.run()

    strat = result[0]
    returns = strat.analyzers.returns.get_analysis()
    if verbose:    
        # 获取基准收益率
        benchmark = pd.read_csv(benchmark_path, index_col=0, parse_dates=['datetime'])
        benchmark = benchmark[start_date:end_date]
        benchmark_returns = benchmark['close'].pct_change().fillna(0)
        benchmark_time_return = (1 + benchmark_returns).cumprod() - 1
        benchmark_rtot = benchmark_time_return.iat[-1]
 
        # 输出各项指标
        mdd = strat.analyzers.drawdown.get_analysis().max.drawdown
        ta = strat.analyzers.ta.get_analysis()
        print(f"基准收益率: {100*benchmark_rtot:.2f}%")
        print(f"收益率: {100*returns['rtot']:.2f}%")
        print(f"年化收益率: {returns['rnorm100']:.2f}%")
        print(f"最大回撤: {mdd:.2f}%")
        print(f"交易次数: {ta.total.total}")
        print(f"胜率: {ta.won.total / ta.total.closed * 100:.2f}%")
        if ta.won.pnl.average > 0 and ta.lost.pnl.average > 0:
            print(f"盈亏比: {-ta.won.pnl.average/ta.lost.pnl.average:.2f}")
        return strat.analyzers.time_return.get_analysis(), benchmark_time_return

    return returns['rnorm100']
