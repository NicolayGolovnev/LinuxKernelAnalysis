import sys
sys.setrecursionlimit(20000)

import numpy as np
from sklearn.manifold import TSNE
import git
import config
from CommitTokenizer import TextTokenizer, CommitSmaple
from MatrixLenGenerator import create_matrix, get_mean
from scipy.cluster.hierarchy import linkage, dendrogram, fcluster
import matplotlib.pyplot as plt
from collections import Counter
from сommitСlassifier import CommitVectorizer, CommitClassifier


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




if __name__ == '__main__':
    repo = git.Repo(config.repo_path)
    vectorizer = CommitVectorizer()

    white_samples, grey_samples = vectorizer.make_samples(repo)
    white_vectors, gray_vectors = vectorizer.get_matrix_from_commits(repo, white_samples, grey_samples)

    classifire = CommitClassifier()
    classifire.fit(white_vectors, gray_vectors)

    result_sample = CommitSmaple(
        repo,
        commit_filter=classifire.is_bugfix_commit,
        folder=config.git_file_path,
        max_len=config.max_commit
    )

    tt = TextTokenizer()
    vectors = tt.sample_to_vectors(result_sample.lsit)
    matrix = create_matrix(vectors)
    Z = linkage(matrix, 'single', metric='average')

    labels = fcluster(Z, config.threshold, criterion='distance')
    counter = Counter(labels)
    counter = sorted(counter.items(), key=lambda x: x[1], reverse=True)
    for index in counter[:config.count_clusters_in_sample]:
        cluster = cluster_to_string(vectors, labels, index[0])
        print('[', ', '.join(tt.vector_to_message(cluster)), ']')

    print("Find", len(vectors), "messages")
    print("Covered", get_metric(Z, len(vectors), config.count_clusters_in_sample, config.threshold)[0], "%")
    print("Fragmentation", get_metric(Z, len(vectors), config.count_clusters_in_sample, config.threshold)[1], "%")

    plt.figure(figsize=(10, 5))
    plt.title('Hierarchical Clustering Dendrogram')
    plt.ylabel('Distance')
    dend = dendrogram(Z, color_threshold=config.threshold, no_labels=True)
    plt.axhline(y=config.threshold, color='r', linestyle='--')
    plt.show()

    X = np.arange(0, 0.8, 0.001)
    Y1 = np.array([get_metric(Z, len(vectors), 4, x)[0] for x in X])
    Y2 = np.array([get_metric(Z, len(vectors), 4, x)[1] for x in X])

    plt.figure(figsize=(10, 5))
    plt.plot(X, Y1, label='Covered')
    plt.plot(X, Y2, label='Fragmentation')
    plt.axvline(x=config.threshold, color='r', linestyle='--')

    plt.legend()
    plt.show()

    tsne = TSNE(n_components=2)
