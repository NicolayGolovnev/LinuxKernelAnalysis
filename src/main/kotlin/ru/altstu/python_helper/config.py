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

# repo
repo_path = 'D:\linux\linux\.git'

# classification
white_sample_len = 2000
grey_sample_len = 8000
white_sample_words = ['bugzilla']
functionality_words = ['robust', 'unnecessary', 'improve', 'future', 'anticipation', 'superfluous', 'remove', 'unused']
bug_words = ['bug', 'error', 'vulnerability', 'issue']
spelling_words = ['doc', 'typo', 'mistake', 'spelling']

# vectorization
POS_black_list = ['CD', 'RP', 'PRP']

# files
use_save_file = True
override_file = False
input_path = "input"
result_path = "result"
clang_dll_path = 'C:/Program Files/LLVM/bin/libclang.dll'

white_path = "saves/white_commits.txt"
grey_path = "saves/grey_commits.txt"
white_vectors_path = "saves/white_vectors.npy"
gray_vectors_path = "saves/gray_vectors.npy"
model_path = "saves/model.pickle"


result_sample_path = "sample.txt"
dict_path = "commit_dict.txt"
bow_vectors_path = "vectors.npy"
matrix_length_path = "matrix.npy"
labels_path = "labels"


# clustering
count_clusters_in_sample = 16
accuracity_treshold = 1000

# clustering

# output
short_output_word_ciunt = 5


def is_readable(path: str) -> bool:
    return not override_file and use_save_file and os.path.exists(path)


def save_list(path: str, object: List[Any]) -> None:
    if not is_readable(path) and use_save_file:
        np.savetxt(path, object, delimiter="\n", fmt="%s", encoding='utf-8')

def save_np(path: str, obj: np.ndarray[Any]) -> None:
    if not is_readable(path) and use_save_file:
        np.save(path, obj)

def save_object(path: str, obj:Any) -> None:
    with open(path, 'wb') as f:
        pickle.dump(obj, f)
