import os
import numpy as np
from backend.utils.check_uploaded_files import open_file

def top_variance(params):
    """
    Selects the user defined number of top features with the highest variance
    from the datasets.
    """
    datasets = ['dataset1']
    feat_num = params['feat_num']
    if not params['autocorr']:
        datasets.append('dataset2')
    for dataset in datasets:
        path = os.path.join(params['study_folder'], params[dataset])
        X, sep = open_file(path)
        # keep only the top N var features
        X = X[np.argsort(X.var())[-int(feat_num):]]
        filename, ext = os.path.splitext(params[dataset])
        params[dataset] = filename + '_topvar' + ext
        path = os.path.join(params['output_folder'], params[dataset])
        X.to_csv(path, sep=sep)
    params['fs_done'] = True
    return params

