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
        self.min_count = min_count

    def labels(self, matrix: np.array) -> np.ndarray[int]:
        dbscan = DBSCAN(eps=self.treshold, min_samples=self.min_count, metric='cosine')
        labels = dbscan.fit(matrix)
        return labels.labels_ # noqa

# TODO Сделать подтягивание параметров из файла конфига
# Заменить metric='cosine' на metric='euclidean'. Данные уже L2-нормализованы после LSA, а для единичных векторов косинусное расстояние эквивалентно евклидову: cos(x,y) = 1 - ||x-y||²/2.
class HDBSCANClusterizer(IClusterizer):
    def __init__(self, min_cluster_size=10, min_samples=5, metric='euclidean',
                 cluster_selection_method='eom', cluster_selection_epsilon=0.4):
        self.min_cluster_size = min_cluster_size
        self.min_samples = min_samples
        self.metric = metric
        self.cluster_selection_method = cluster_selection_method
        self.cluster_selection_epsilon = cluster_selection_epsilon

    def labels(self, matrix: np.array) -> np.ndarray[int]:
        clusterer = HDBSCAN(
            min_cluster_size=self.min_cluster_size,
            min_samples=self.min_samples,
            metric=self.metric,
            cluster_selection_method=self.cluster_selection_method,
            cluster_selection_epsilon=self.cluster_selection_epsilon
        )
        labels = clusterer.fit(matrix)
        return labels.labels_