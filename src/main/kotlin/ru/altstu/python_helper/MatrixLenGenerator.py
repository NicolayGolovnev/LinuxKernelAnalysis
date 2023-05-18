import math
import numpy as np
from tqdm import tqdm
from scipy.spatial import distance
from scipy.spatial.distance import cosine

def cos_distance(one_message, other_message):
    return cosine(one_message, other_message)

def get_mean(data):
    return np.mean(data, axis=0)

def create_matrix(data: list):
    size= len(data)
    matrix = np.zeros((size, size))
    with tqdm(total= (size * size) // 2 - size, desc='Distance counting') as pbar:
        for i in range(size):
            for j in range(i+1, size):
                cur_distance = cos_distance(data[i], data[j])
                matrix[i, j] = cur_distance
                matrix[j, i] = cur_distance
                pbar.update(1)
    return distance.squareform(matrix)
