import concurrent.futures
import itertools
from typing import Callable

import numpy
import numpy as np
import tqdm.contrib.concurrent
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import Normalizer
from tqdm import tqdm

from common import split_iterator


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
    def __init__(self, distance_method: Callable[[np.ndarray, np.ndarray], float], thread_count: int = 1):
        self._count_distance = distance_method
        self.thread_count = thread_count
        self._matrix = None
        self._bar = None
        self._data = None

    def create_matrix(self, data: np.ndarray[float]) -> np.array:
        lsa = make_pipeline(TruncatedSVD(n_components=100), Normalizer(copy=False))
        data = lsa.fit_transform(data)
        similarities: np.ndarray = cosine_similarity(data)
        similarities = similarities / 2 + 1
        np.fill_diagonal(similarities, 0)
        return similarities
