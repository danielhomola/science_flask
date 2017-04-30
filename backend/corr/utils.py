import numpy as np
import scipy.cluster.hierarchy as hclust
from scipy.spatial.distance import pdist


def order_by_hc(data, method='average', metric='correlation', get_ind=False):
    """
    Orders the DataFrame cols by hierarchical clustering.

    Correlation is used as a distance metric, and the UPGMA for joining clusters
    by default. Correlation as a distance measure cares more about the shape
    of the data then its magnitude.

    Returns
    ------
    - The reordered DataFrame.
    - if get_ind=True, the index for reordering is returned as well
    """
    dist = pdist(data.T.values, metric=metric)
    dist = np.clip(dist, 0, dist.max())
    d = hclust.linkage(dist, method=method)
    # sometimes correlation based distance doesn't work, so then use euc dist
    if np.any(d < 0):
        dist = pdist(data.T.values, metric='euclidean')
        dist = np.clip(dist, 0, dist.max())
        d = hclust.linkage(dist, method=method)
    d = hclust.dendrogram(d, labels=data.columns, no_plot=True,
                          count_sort='descending')
    data = data.T.loc[d['ivl']].T
    if get_ind:
         return data, d['leaves']
    else:
        return data
