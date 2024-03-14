from typing import Callable

import numpy as np
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