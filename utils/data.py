import os
import pandas as pd
import akshare as ak

def get_etf_data(code: str, start=None, update=False, latest_trade_date=None):
    """获取 ETF 历史行情 (前复权)
    latest_trade_date: str, 例如 '2025-07-04'，为最新交易日。
    """
    filename = f"data/etf/{code}.csv"
    if os.path.exists(filename):
        df = pd.read_csv(filename, index_col=0, parse_dates=['datetime'])
        # 如果update为True, 检查是否真的需要更新
        if update and latest_trade_date is not None:
            local_last_date = df.index[-1]
            if local_last_date >= pd.to_datetime(latest_trade_date):
                update = False
    if update:
        try:
            df = ak.fund_etf_hist_em(symbol=code, start_date='20190701', adjust='qfq')
            df.rename(columns={
                '日期': 'datetime',
                '开盘': 'open',
                '收盘': 'close',
                '最高': 'high',
                '最低': 'low',
                '成交量': 'volume',
            }, inplace=True)
            df['datetime'] = pd.to_datetime(df['datetime'])
            df.set_index('datetime', inplace=True)
            df.to_csv(filename)
            print(f'下载数据并存储到{filename}')
        except Exception as e:
            print(f'下载{code}数据失败: {type(e).__name__}: {e}')
            return None
    # 切片
    if start is not None:
        start = pd.to_datetime(start)
        df = df[df.index >= start]
    return df

def get_data_dict(start='2025-01-01', update=False, benchmark='510300', codes_path='data/deduplicate_etfs.csv'):
    codes = pd.read_csv(codes_path)['代码'].to_list()
    benchmark_index = get_etf_data(benchmark, start=start, update=update).index
    data_dict = {}
    for code in codes:
        df = get_etf_data(code, start=start, update=update)
        df = df.reindex(benchmark_index)  # 重置日期列，并用前一日填充缺失值
        df = df.ffill()
        data_dict[str(code)] = df
    return data_dict

def get_ret_mat(data_dict, days=5):
    close_dict = {code: df['close'] for code, df in data_dict.items()}
    close_mat = pd.DataFrame(close_dict)
    ret_mat = close_mat.pct_change(periods=days).shift(-days)
    ret_mat.columns = ret_mat.columns.astype(str)
    return ret_mat
