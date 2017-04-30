import os
import pandas as pd
import numpy as np
import scipy as sp
import matplotlib
matplotlib.use('Agg')
import seaborn as sns
from .check_pvals import check_pvals
from .utils import order_by_hc
from backend.utils.check_uploaded_files import open_file

def corr_main(params):
    """
    This is the main backend function which performs the following steps:
    - takes the user specified, top n variance features
    - calculates a the correlation between these features
    - performs correction for multiple testing with the user specified method
    - saves results, plots matrices as heatmaps and save these figures as well
    """

    # --------------------------------------------------------------------------
    # CALCULATE CORRELATIONS
    # --------------------------------------------------------------------------

    # open first dataset
    path = os.path.join(params['output_folder'], params['dataset1'])
    dataset1, sep = open_file(path)
    n, p = dataset1.shape
    # if there's a 2nd dataset, merge them
    if not params['autocorr']:
        path2 = os.path.join(params['output_folder'], params['dataset2'])
        dataset2, sep2 = open_file(path2)
        merged_datasets_df = dataset1.join(dataset2, how='inner',
                                           lsuffix='_data1', rsuffix='_data2')
        X = merged_datasets_df.values
    else:
        merged_datasets_df = dataset1
        X = merged_datasets_df.values

    # standardise X
    X = (X - X.mean(0)) / X.std(0)[np.newaxis, :]

    # calculate Spearman rank correlations and corresponding p-values
    r_vals, p_vals = sp.stats.spearmanr(X)

    # correct for multiple testing
    p_vals, p_mask = check_pvals(p_vals, params)

    # delete correlations that did not pass the multi test correction
    r_vals[~p_mask] = 0
    p_vals[~p_mask] = 1

    # --------------------------------------------------------------------------
    # WRITE RESULTS FOR DATA1, DATA2, DATA1-2
    # --------------------------------------------------------------------------

    params = write_results(params, r_vals[:p, :p], p_vals[:p, :p],
                           (dataset1, dataset1), 'dataset1', True)
    if not params['autocorr']:
        params = write_results(params, r_vals[p:, p:], p_vals[p:, p:],
                               (dataset2, dataset2), 'dataset2', True)
        params = write_results(params, r_vals[:p, p:], p_vals[:p, p:],
                               (dataset1, dataset2), 'dataset1_2')

    # if corr_done in params is False one of the writing steps failed
    if 'corr_done' not in params:
        params['corr_done'] = True
    return params


def write_results(params, r, p, datasets, name, sym=False):
    """
    Generates and saves all result files for user and visualisations.
    """
    # create r and p DataFrames
    r = pd.DataFrame(r, columns=datasets[1].columns, index=datasets[0].columns)
    p = pd.DataFrame(p, columns=datasets[1].columns, index=datasets[0].columns)

    # if sym, set diagonal to 1, because line 60 set it 0
    if sym:
        np.fill_diagonal(r.values, 1)
        np.fill_diagonal(p.values, 1)

    # filter rows and columns which are all 0, if sym=True then diag can be 1
    to_keep_row = ((r == 0).sum(axis=1) != r.shape[1] - int(sym)).values
    to_keep_col = ((r == 0).sum(axis=0) != r.shape[0] - int(sym)).values
    rf = r.iloc[to_keep_row, to_keep_col]
    pf = p.iloc[to_keep_row, to_keep_col]

    # check size of the filtered data, abort if empty dim encountered
    if len(rf.shape) == 1 or rf.shape == (0, 0):
        params['corr_done'] = False
        return params

    # save r and p matrices
    params['r_' + name] = 'r_' + name + '.csv'
    path = os.path.join(params['output_folder'], params['r_' + name])
    rf.to_csv(path)
    params['p_' + name] = 'p_' + name + '.csv'
    path = os.path.join(params['output_folder'], params['p_' + name])
    pf.to_csv(path)

    # cannot cluster if either of the dimensions is one
    if rf.shape[0] == 1:
        data_clusters_row = [0]
        data_clusters_col = range(rf.shape[1])
    elif rf.shape[1] == 1:
        data_clusters_row = range(rf.shape[0])
        data_clusters_col = [0]
    else:
        # calculate cluster ordering by r values
        _, data_clusters_row = order_by_hc(datasets[0][rf.index], get_ind=True)
        _, data_clusters_col = order_by_hc(datasets[1][rf.columns], get_ind=True)

    # reorder by dataset clusters, this is the default in vis
    rf = rf.iloc[data_clusters_row, data_clusters_col]
    pf = pf.iloc[data_clusters_row, data_clusters_col]

    # plot r_vals and save figure
    g = sns.heatmap(rf, cmap='RdBu_r')
    params['r_plot' + name] = 'r_' + name + '.png'
    path = os.path.join(params['output_folder'], params['r_plot' + name])
    fig = g.get_figure()
    fig.savefig(path)
    fig.clf()
    # plot p_vals and save figure

    g = sns.heatmap(pf)
    params['p_plot' + name] = 'p_' + name + '.png'
    path = os.path.join(params['output_folder'], params['p_plot' + name])
    fig = g.get_figure()
    fig.savefig(path)
    fig.clf()
    return params
