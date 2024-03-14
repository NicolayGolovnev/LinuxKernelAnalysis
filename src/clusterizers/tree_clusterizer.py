import numpy as np
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import squareform
from sklearn.cluster import DBSCAN


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
        #self.treshold_finder = ThresholdFinder(Z, len(vectors), config.count_clusters_in_sample)
        self.treshold = 0.65
        self.min_count = 20

    def labels(self, matrix: np.array) -> np.ndarray[int]:
        matrix = squareform(matrix)
        dbscan = DBSCAN(self.treshold, min_samples=self.min_count, metric='precomputed')
        labels = dbscan.fit(matrix)
        return labels.labels_ # noqa