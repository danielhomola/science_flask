import os
import pandas as pd


def load_params(analysis_folder):
    """
    Loads the analysis specific params file and converts string to Booleans.
    """
    # load params file as a dictionary
    params_file = os.path.join(analysis_folder, 'params.csv')
    params = pd.read_csv(params_file, index_col=0).to_dict()['value']

    def str2bool(string):
        return string.lower() in ("yes", "true", "t", "1")

    bool_fields = ['autocorr']
    for field in bool_fields:
        if field in params:
            params[field] = str2bool(params[field])

    return params


def write_params(analysis_folder, params):
    """
    Saves/updates the params file of an analysis from the params dict
    """
    # save params file from params dictionary
    params_file = os.path.join(analysis_folder, 'params.csv')
    df = pd.DataFrame.from_dict(params, orient='index')
    df.columns = ['value']
    df.to_csv(params_file)
