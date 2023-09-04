import numpy as np

from scipy.cluster.hierarchy import fcluster
from collections import Counter
from typing import Callable, Tuple, List

from tqdm import tqdm
import config

class TresholdFinder:

    def __init__(self, tree: np.ndarray[float], count_messages: int, count_cluters: int):
        self._tree = tree
        self._count_messages = count_messages
        self._count_clusters = count_cluters

    def find_treshold(self, point_range: Tuple[float, float] = (0, 0.8)) -> float:
        intersections = self._find_intersection(
            lambda x: self._get_metric(x, TresholdFinder._cover_metric_method),
            lambda x: self._get_metric(x, TresholdFinder._scatter_metric_method),
            point_range
        )
        return intersections[-1]

    @staticmethod
    def _cover_metric_method(counter: List[Tuple[int, int]], count_clasters:int) -> float:
        return sum([index[1] for index in counter[:count_clasters]]) / sum([index[1] for index in counter]) * 100

    @staticmethod
    def _scatter_metric_method(counter: List[Tuple[int, int]], count_clasters:int) -> float:
        return counter[count_clasters - 1][1] / counter[0][1] * 100

    def _get_metric(self, treshold:float, method:Callable[[List[Tuple[int, int]], int],float]) -> float:
        counter = self._get_cluster_counter(treshold)
        count_clasters = min(self._count_clusters, len(counter))
        return method(counter, count_clasters)

    def _get_cluster_counter(self, treshold: float) -> List[Tuple[int, int]]:
        labels = fcluster(self._tree, treshold, criterion='distance')
        counter = Counter(labels)
        counter = sorted(counter.items(), key=lambda x: x[1], reverse=True)
        return counter

    def _find_intersection(self,
                           func1: Callable[[float], float],
                           func2: Callable[[float], float],
                           x_range: Tuple[float, float]) -> List[float]:
        x_values = np.linspace(x_range[0], x_range[1], config.accuracity_treshold)

        intersections = []
        with tqdm(total=config.accuracity_treshold - 1, desc='Auto Treshold') as pbar:
            for i in range(1, len(x_values)):
                if np.sign(func1(x_values[i - 1]) - func2(x_values[i - 1])) != np.sign(func1(x_values[i]) - func2(x_values[i])):
                    intersection_point = x_values[i - 1]
                    intersections.append(intersection_point)
                pbar.update(1)

        return intersections
