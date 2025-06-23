def compute_ic(fac_mat, ret_mat):
    common_idx = fac_mat.dropna().index.intersection(ret_mat.dropna().index)
    ic = fac_mat.loc[common_idx].corrwith(ret_mat.loc[common_idx], axis=1, method='spearman')
    return ic

def compute_ir(ic_series):
    return ic_series.mean() / (ic_series.std())
