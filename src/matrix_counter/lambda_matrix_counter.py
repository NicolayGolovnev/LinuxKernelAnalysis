import concurrent.futures
import itertools
from typing import Callable

import numpy as np
import tqdm.contrib.concurrent
from sklearn.decomposition import TruncatedSVD
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import Normalizer
from tqdm import tqdm

class IMatrixGenerator:
    def create_matrix(self, vectors: list[np.ndarray[float]]) -> np.array:
        ...

class LambdaMatrixCounter(IMatrixGenerator):
    def __init__(self, distance_method: Callable[[np.ndarray, np.ndarray], float]):
        self._count_distance = distance_method

    def create_matrix(self, data: list[np.ndarray[float]]) -> np.array:
        size = len(data)
        matrix = np.zeros((size * (size - 1) // 2))
        with tqdm(total=size * (size - 1) // 2, desc='Distance counting') as pbar:
            for i in range(size):
                for j in range(i + 1, size):
                    cur_distance = self._count_distance(data[i], data[j])
                    flat_index = i * size + j - (i + 1) * (i + 2) // 2
                    matrix[flat_index] = cur_distance
                    pbar.update(1)
        return matrix


class LambdaMatrixCounterTreading(IMatrixGenerator):
    def __init__(self, distance_method: Callable[[np.ndarray, np.ndarray], float], thread_count: int = 1, n_components: int = 200):
        self._count_distance = distance_method
        self.thread_count = thread_count
        self.n_components = n_components
        self._matrix = None
        self._bar = None
        self._data = None

    def create_matrix(self, data: np.ndarray[float]) -> np.array:
        # TODO В библиотеке написано, что 100 - это рекомендация. Посмотреть, как повлияет
        #  Сделать динамическое формирование - число компонент
        n_comp = min(self.n_components, data.shape[1], max(data.shape[0] // 5, 2))
        lsa = make_pipeline(TruncatedSVD(n_components=n_comp), Normalizer(copy=False))
        data = lsa.fit_transform(data)
        # print("start converting")
        data = np.float32(data)
        # print("stop converting")
        return data
