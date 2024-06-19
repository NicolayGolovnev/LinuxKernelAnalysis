import numpy as np
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import squareform
from sklearn.cluster import HDBSCAN, DBSCAN


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
    def __init__(self, treshold=0.45, min_count=20):
        self.treshold = treshold
        self.min_count = 20

    def labels(self, matrix: np.array) -> np.ndarray[int]:
        dbscan = DBSCAN(eps=self.treshold, min_samples=self.min_count, metric='cosine')
        labels = dbscan.fit(matrix)
        return labels.labels_ # noqa