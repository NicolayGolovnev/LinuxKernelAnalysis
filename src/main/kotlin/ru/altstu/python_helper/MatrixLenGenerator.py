import os

import config
import numpy as np
from tqdm import tqdm
from scipy.spatial import distance
from scipy.spatial.distance import cosine

def cos_distance(one_message, other_message):
    return cosine(one_message, other_message)

def get_mean(data):
    return np.mean(data, axis=0)

def create_matrix(data: list):
    size = len(data)
    matrix = np.zeros((size*(size-1)//2))
    if config.use_save_file and os.path.exists(config.matrix_length_path):
        matrix = np.load(config.matrix_length_path)
    else:
        with tqdm(total= size * (size - 1) // 2, desc='Distance counting') as pbar:
            for i in range(size):
                for j in range(i+1, size):
                    cur_distance = cos_distance(data[i], data[j])
                    flat_index = i * size + j - (i + 1) * (i + 2) // 2
                    matrix[flat_index] = cur_distance
                    pbar.update(1)
        if config.use_save_file:
            np.save(config.matrix_length_path, matrix)

    return matrix
