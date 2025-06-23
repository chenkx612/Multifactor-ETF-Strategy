import os
import pandas as pd
import akshare as ak

def get_etf_data(code: str, start=None, update=False):
    """获取 ETF 历史行情 (前复权) """
    filename = f"data/etf/{code}.csv"

    if not update and os.path.exists(filename):
        df = pd.read_csv(filename, index_col=0, parse_dates=['datetime'])

    else:
        try:
            df = ak.fund_etf_hist_em(symbol=code, start_date='20150601', adjust='qfq')
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

def get_data_dict(start='2025-01-01', benchmark='510300', codes_path='data/deduplicate_etfs.csv'):
    codes = pd.read_csv(codes_path)['代码'].to_list()
    benchmark_index = get_etf_data(benchmark, start=start).index
    data_dict = {}
    for code in codes:
        df = get_etf_data(code, start=start)
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
