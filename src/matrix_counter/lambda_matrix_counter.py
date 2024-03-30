import concurrent.futures
import itertools
from typing import Callable

import numpy
import numpy as np
import tqdm.contrib.concurrent
from sklearn.metrics.pairwise import cosine_similarity
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
        similarities: np.ndarray = cosine_similarity(data)
        np.fill_diagonal(similarities, 0)
        return similarities

        size = data.shape[0]
        matrix_shape = size * (size - 1) // 2
        self._matrix = np.zeros(matrix_shape, dtype=np.float32)
        self._bar = tqdm(total=matrix_shape, desc='Distance counting')
        iterators = split_iterator(range(size), self.thread_count)
        self._data = data

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.thread_count) as executor:
            results = executor.map(self._part_count_matrix, iterators)
            for _ in results:
                pass
            executor.shutdown()
        return self._matrix

    def _part_count_matrix(self, iterator):
        size = self._data.shape[0]
        for i in iterator:
            for j in range(i + 1, size):
                cur_distance = self._count_distance(self._data[i].toarray()[0], self._data[j].toarray()[0])
                flat_index = i * size + j - (i + 1) * (i + 2) // 2
                self._matrix[flat_index] = cur_distance
                self._bar.update(1)



