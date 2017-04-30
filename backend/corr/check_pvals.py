import numpy as np
from statsmodels.sandbox.stats.multicomp import multipletests as multicor


def check_pvals(p_vals, params):
    """
    Corrects for multiple  testing using the user specified method and alpha
    value. Returns a boolean mask that can be used to filter the resulting
    heatmap.
    """

    # basic params
    n, p = p_vals.shape
    mc_method = params['multi_corr_method']
    mc_alpha = params['alpha_val']

    # corr matrix is symmetric we only need to correct the lower half
    ps_to_check = np.array(np.tril(np.ones((p, p)), k=-1), dtype=np.bool)

    ps = multicor(p_vals[ps_to_check], method=mc_method, alpha=float(mc_alpha))

    # make Boolean and corrected p-val matrices
    p_mask = np.zeros((p, p), dtype=np.bool)
    p_mask[ps_to_check] = ps[0]
    p_mask = mirror_lower_triangle(p_mask)
    p_vals = np.ones((p, p))
    p_vals[ps_to_check] = ps[1]
    p_vals = mirror_lower_triangle(p_vals)

    return p_vals, p_mask


def mirror_lower_triangle(m):
    """
    Copies the lower triangle's values to the upper triangle by mirroring
    the matrix over the diagonal.
    """
    n = m.shape[0]
    if n != m.shape[1]:
        raise ValueError('This function expects square a matrix.')
    for r in range(n):
        for c in range(n):
            m[r,c] = m[c,r]
    return m
