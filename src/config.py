import os
import pickle
from dataclasses import dataclass
from typing import List, Any
import numpy as np

@dataclass
class DirectoryAnalysisData:
    name: str
    path: str
    max_commit: int

@dataclass
class FileNameConfig:
    input_path: str
    result_path: str
    white_path: str
    grey_path: str
    white_vectors_path: str
    gray_vectors_path: str
    bow_vectors_path: str
    dict_path: str
    labels_path: str
    result_sample_path: str
    matrix_length_path: str
    model_path: str
    documents_path: str
    load_commits: str
    bugfix_hashes: str

@dataclass
class MainConfig:
    repo_path: str

    # classification
    white_sample_len: int
    grey_sample_len: int
    white_sample_words: List[str]
    functionality_words: List[str]
    bug_words: List[str]
    spelling_words: List[str]
    stop_words: List[str]

    # vectorization
    POS_black_list: List[str]

    # files
    use_save_file: bool
    override_file: bool
    clang_dll_path: str

    # clustering
    count_clusters_in_sample: int
    accuracity_treshold: int


