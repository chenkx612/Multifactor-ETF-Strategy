import pandas as pd
from .data import get_etf_data

def deduplicate_etf_pool(etfs: pd.DataFrame,
                          window: int,
                          corr_threshold: float) -> pd.DataFrame:
    """
    对ETF池去重, 计算最近 window 天收益率相关性，
    对相关性高于阈值的ETF对, 仅保留第一次出现的ETF, 所以在去重前需根据关心的指标先进行排序。

    参数：
    - etfs: 包含'代码'列, 已按某指标从高到低排序的DataFrame
    - window: 计算相关性所需的样本天数
    - corr_threshold: 相关性阈值

    返回：
    - 过滤去重后的etfs子集
    """
    # 获取回溯日期范围
    benchmark = get_etf_data('510300')
    start_date = benchmark.index[-window]
    
    # 取收益率
    returns = {}
    for code in etfs['代码']:
        df = get_etf_data(code, start=start_date)
        returns[code] = df['涨跌幅']

    # 构建所有ETF的收益率DataFrame
    returns_df = pd.DataFrame(returns)

    # 计算相关性矩阵
    corr_mat = returns_df.corr()

    # 标记需要剔除的代码
    to_drop = set()
    codes = list(etfs['代码'])
    for i, code_i in enumerate(codes):
        for code_j in codes[i+1:]:
            if corr_mat.loc[code_i, code_j] > corr_threshold:
                # 保留先出现（成交额更大）的code_i，剔除code_j
                to_drop.add(code_j)

    # 返回过滤后的数据
    filtered = etfs[~etfs['代码'].isin(to_drop)].copy()
    return filtered
