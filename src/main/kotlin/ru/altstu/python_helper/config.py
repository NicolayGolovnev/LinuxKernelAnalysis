import os

# repo
from typing import List, Any

import numpy as np

repo_path = 'D:\linux\linux\.git'
git_file_path = 'drivers/thunderbolt/'
max_commit = 10000000000000000000000000000000

# classification
white_sample_len = 1000
grey_sample_len = 5000
white_sample_words = ['bugzilla']
functionality_words = ['robust', 'unnecessary', 'improve', 'future', 'anticipation', 'superfluous', 'remove', 'unused']
bug_words = ['bug', 'error', 'vulnerability', 'issue']
spelling_words = ['doc', 'typo', 'mistake', 'spelling']

# vectorization
stop_words = [
    'fix',
    'error',
    'thunderbolt',
    'of',
    'and',
    'for',
    'in',
    'all',
    'add',
    'non',
    'also',
    'there',
    'the',
    'build',
    'on',
    'by',
    'with',
    'to',
    'this',
    '9aabb68568b4',
    '11',
    '1000',
    'issue',
    'driver',
    'code',
    'following',
    'after',
    'if',
]

# files
use_save_file = True
override_file = False
white_path = "white_commits.txt"
grey_path = "grey_commits.txt"
white_vectors_path = "white_vectors.npy"
gray_vectors_path = "gray_vectors.npy"

dict_path = "commit_dict.txt"
bow_vectors_path = "vectors.npy"
matrix_length_path = "matrix.npy"
clang_dll_path = 'C:/Program Files/LLVM/bin/libclang.dll'

# clustering
count_clusters_in_sample = 8
threshold = 0.498

# clustering

# output
short_output_word_ciunt = 5


def is_readable(path: str) -> bool:
    return not override_file and use_save_file and os.path.exists(path)


def save_list(path: str, object: List[Any]) -> None:
    if not is_readable(path) and use_save_file:
        np.savetxt(path, object, delimiter="\n", fmt="%s", encoding='utf-8')


def save_np(path: str, object: np.ndarray[Any]) -> None:
    if not is_readable(path) and use_save_file:
        np.save(path, object)
