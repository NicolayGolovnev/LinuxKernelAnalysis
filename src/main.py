import os
from typing import List, Callable

import clang
from clang.cindex import Config
from git import Repo

from clusterizers.tree_clusterizer import TreeClusterizer, DBSCANClusterizer
from documenters.comment_text_tokenizer import CommitTextDocumenter
from flie_handlers.sample_data import FileIOManager
from matrix_counter.lambda_matrix_counter import LambdaMatrixCounter
from samplers.sampler import Sampler
from thresholdFinder import ThresholdFinder

import numpy as np
import git
import json
from scipy.cluster.hierarchy import fcluster
from collections import Counter
from config import DirectoryAnalysisData, FileNameConfig, MainConfig
from scipy.spatial.distance import cosine

from vectorizers.tf_idf_vectorizer import TfIdfVectorizer
from work_handler.main_handler import MainHandler
from work_handler.paper_result_handler import PaperResultHandler
from work_handler.work_handler import WorkHandler
from сommit_classifier import CommitVectorizer, CommitClassifier


def cluster_to_string(messages, data, number):
    mean = np.mean(np.array([msg for i, msg in enumerate(messages) if data[i] == number]), axis=0)
    return mean

def get_metric(tree, count_messages, count_clasters, treshold):
    labels = fcluster(tree, treshold, criterion='distance')
    counter = Counter(labels)
    count_clasters = min(count_clasters, len(counter))
    counter = sorted(counter.items(), key=lambda x: x[1], reverse=True)
    return sum([index[1] for index in counter[:count_clasters]]) / count_messages * 100, counter[count_clasters - 1][
        1] / counter[0][1] * 100


def get_filter_method(repo: Repo, io_manager: FileIOManager, config: MainConfig, name_config: FileNameConfig):
    vectorizer = CommitVectorizer(io_manager, config, name_config)
    white_samples, grey_samples = vectorizer.make_samples(repo)
    white_vectors, gray_vectors = vectorizer.get_matrix_from_commits(repo, white_samples, grey_samples)
    classifire = CommitClassifier(io_manager, config, name_config)
    classifire.fit(white_vectors, gray_vectors)
    return classifire.is_bugfix_commit


def read_input_data_from_file(config: FileNameConfig, path:str):
    with open(f"{config.input_path}/{path}") as json_config:
        json_data = json.load(json_config)
    return DirectoryAnalysisData(**json_data)



if __name__ == '__main__':
    with open("file_names.json") as json_config:
        file_names: FileNameConfig = FileNameConfig(**json.load(json_config))

    with open("config.json") as json_config:
        config: MainConfig = MainConfig(**json.load(json_config))

    file_io = FileIOManager()
    Config.set_library_path(config.clang_dll_path)

    repo = git.Repo(config.repo_path)


    tasklist = [read_input_data_from_file(file_names, path) for path in os.listdir(file_names.input_path)]
    doc = CommitTextDocumenter(config.stop_words, config.POS_black_list)
    tf_idf = TfIdfVectorizer()
    cos_matrix = LambdaMatrixCounter(cosine)
    clusterizer = TreeClusterizer()
    dbsan_clusterizer = DBSCANClusterizer()

    wh = WorkHandler(
        documenter=doc,
        vectorizer=tf_idf,
        matrix_counter=cos_matrix,
        clasterizer=dbsan_clusterizer,
        file_io=file_io,
        file_names=file_names
    )

    rh = PaperResultHandler(
        repo=repo,
        file_io=file_io,
        file_names=file_names
    )

    #filtr_method = get_filter_method(repo, file_io, config, file_names)
    mh = MainHandler(
        work_handler=wh,
        io_manager=file_io,
        file_names=file_names,
        commit_filter=None
    )

    mh_r = MainHandler(
        work_handler=rh,
        io_manager=file_io,
        file_names=file_names,
        commit_filter=None
    )


    mh.handle(repo, tasklist)
    #mh_r.handle(repo, tasklist)






