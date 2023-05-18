import sys
sys.setrecursionlimit(20000)

import numpy as np
from sklearn.manifold import TSNE
import git
from tqdm import tqdm

from CommitTokenizer import TextTokenizer
from MatrixLenGenerator import create_matrix, get_mean
from scipy.cluster.hierarchy import linkage, dendrogram, fcluster
import matplotlib.pyplot as plt
from collections import Counter

repo_path = 'D:\linux\linux\.git'
repo = git.Repo(repo_path)

def cluster_to_string(messages, data, number):
    mean = get_mean(np.array([msg for i, msg in enumerate(messages) if data[i] == number]))
    return mean

def get_metric(tree, count_messages, count_clasters, treshold):
    labels = fcluster(tree, treshold, criterion='distance')
    counter = Counter(labels)
    count_clasters = min(count_clasters, len(counter))
    counter = sorted(counter.items(), key=lambda x: x[1], reverse=True)
    return sum([index[1] for index in counter[:count_clasters]])/count_messages * 100, counter[count_clasters -1][1] / counter[0][1] * 100


if __name__ == '__main__':
    treshold = 0.498
    count_of_clasters = 8
    folder = 'drivers/thunderbolt/'
    count = 10000 #repo.git.rev_list('--count', '--', folder)

    tt = TextTokenizer()

    messages = []
    i = 0
    for commit in tqdm(repo.iter_commits(paths=folder), desc='Commit Processing', total=count):
        messages += [tt.unit_to_token(unit) for unit in tt.commit_to_units(commit)]
        i += 1
        if i > count:
            break

    vectors = tt.vectorize(messages)
    matrix = create_matrix(vectors)
    Z = linkage(matrix, 'single', metric='average')

    labels = fcluster(Z, treshold, criterion='distance')
    counter = Counter(labels)
    counter = sorted(counter.items(), key=lambda x: x[1], reverse=True)
    for index in counter[:count_of_clasters]:
        cluster = cluster_to_string(vectors, labels, index[0])
        print('[', ', '.join( tt.vector_to_message(cluster)), ']')

    print("Find", len(vectors), "messages")
    print("Covered", get_metric(Z, len(vectors), count_of_clasters, treshold)[0], "%")
    print("Scatter", get_metric(Z, len(vectors), count_of_clasters, treshold)[1], "%")


    plt.figure(figsize=(10, 5))
    plt.title('Hierarchical Clustering Dendrogram')
    plt.ylabel('Distance')
    dend = dendrogram(Z, color_threshold=treshold, no_labels=True)
    plt.axhline(y=treshold, color='r', linestyle='--')
    plt.show()

    X = np.arange(0, 0.9, 0.001)
    Y1 = np.array([get_metric(Z, len(vectors), 4, x)[0] for x in X])
    Y2 = np.array([get_metric(Z, len(vectors), 4, x)[1] for x in X])


    plt.figure(figsize=(10, 5))
    plt.plot(X, Y1, label='Covered')
    plt.plot(X, Y2, label='Equability')
    plt.axvline(x=treshold, color='r', linestyle='--')

    plt.legend()
    plt.show()

    tsne = TSNE(n_components=2)
