import numpy as np
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import squareform
from sklearn.cluster import HDBSCAN


class IClusterizer:
    def labels(self, matrix: np.array) -> np.ndarray[int]:
        ...

class TreeClusterizer(IClusterizer):
    def __init__(self):
        #self.treshold_finder = ThresholdFinder(Z, len(vectors), config.count_clusters_in_sample)
        self.treshold_finder = lambda: 0.8

    def labels(self, matrix: np.array) -> np.ndarray[int]:
        Z = linkage(matrix, 'single', metric='average')
        labels = fcluster(Z, self.treshold_finder(), criterion='distance')
        return labels # noqa

class DBSCANClusterizer(IClusterizer):
    def __init__(self):
        self.treshold = 0.5
        self.min_count = 20

    def labels(self, matrix: np.array) -> np.ndarray[int]:
        dbscan = HDBSCAN(
            min_cluster_size=self.min_count,
            metric='precomputed',
            n_jobs=1,
            max_cluster_size=matrix.shape[0] // 10
        )
        labels = dbscan.fit(matrix)
        return labels.labels_ # noqa