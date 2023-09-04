import os
import sys
from typing import List, Callable

import nltk

from tresholdFinder import TresholdFinder

sys.setrecursionlimit(20000)

import numpy as np
from sklearn.manifold import TSNE
import git
import config
import json
from CommitTokenizer import TextTokenizer, CommitSample
from MatrixLenGenerator import create_matrix, get_mean
from scipy.cluster.hierarchy import linkage, dendrogram, fcluster
import matplotlib.pyplot as plt
from collections import Counter
from сommitСlassifier import CommitVectorizer, CommitClassifier
from config import DirectoryAnalysisData
from scipy.optimize import fsolve, root_scalar, brentq


def cluster_to_string(messages, data, number):
    mean = get_mean(np.array([msg for i, msg in enumerate(messages) if data[i] == number]))
    return mean


def get_metric(tree, count_messages, count_clasters, treshold):
    labels = fcluster(tree, treshold, criterion='distance')
    counter = Counter(labels)
    count_clasters = min(count_clasters, len(counter))
    counter = sorted(counter.items(), key=lambda x: x[1], reverse=True)
    return sum([index[1] for index in counter[:count_clasters]]) / count_messages * 100, counter[count_clasters - 1][
        1] / counter[0][1] * 100


def get_filter_method():
    vectorizer = CommitVectorizer()
    white_samples, grey_samples = vectorizer.make_samples(repo)
    white_vectors, gray_vectors = vectorizer.get_matrix_from_commits(repo, white_samples, grey_samples)
    classifire = CommitClassifier()
    classifire.fit(white_vectors, gray_vectors)
    return classifire.is_bugfix_commit


class TestFileManager:

    def __init__(self, tests_data: List[DirectoryAnalysisData]):
        self.__root_dir: str = os.getcwd()
        self.tests_data: List[DirectoryAnalysisData] = tests_data

    def full_iteration(self, iteration_func: Callable[[DirectoryAnalysisData], None]) -> None:
        for test_data in self.tests_data:
            self._set_dir(test_data.name)
            iteration_func(test_data)
            self._back_dir()

    def _back_dir(self) -> None:
        os.chdir(self.__root_dir)

    def _set_dir(self, name: str) -> None:
        current_folder = f"{config.result_path}/{name}"
        if not os.path.exists(current_folder):
            os.mkdir(current_folder)
        os.chdir(current_folder)


def perfome_test(analysisData: DirectoryAnalysisData):
    result_sample = CommitSample(
        repo,
        folder=analysisData.path,
        max_len=analysisData.max_commit,
        commit_filter=filter_method
    )

    tt = TextTokenizer()
    vectors = tt.sample_to_vectors(result_sample.list)
    matrix = create_matrix(vectors)

    Z = linkage(matrix, 'single', metric='average')

    tf = TresholdFinder(Z, len(vectors), config.count_clusters_in_sample)
    threshold = tf.find_treshold()

    labels = fcluster(Z, threshold, criterion='distance')
    config.save_np(config.labels_path, labels)

def read_input_data_from_file(path:str):
    with open(f"{config.input_path}/{path}") as json_config:
        json_data = json.load(json_config)
    return DirectoryAnalysisData(**json_data)



if __name__ == '__main__':

    repo = git.Repo(config.repo_path)
    filter_method = get_filter_method()

    input_data = [read_input_data_from_file(path) for path in  os.listdir(config.input_path)]
    tfm = TestFileManager(input_data)
    tfm.full_iteration(perfome_test)





