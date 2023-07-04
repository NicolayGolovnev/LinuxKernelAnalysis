# repo
repo_path = 'D:\linux\linux\.git'
git_file_path = 'drivers/thunderbolt/'
max_commit = 10000000000000000000000000000000

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
dict_path = "commit_dict.txt"
bow_vectors_path = "vectors.npy"
matrix_length_path = "matrix.npy"

# clustering
count_clusters_in_sample = 8
threshold = 0.498

# clustering

#output
short_output_word_ciunt = 5


