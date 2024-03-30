import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, date

import numpy as np
from git import Repo, Commit
from scipy.spatial.distance import cosine
from config import FileNameConfig
from flie_handlers.file_io_manager import FileIOManager
from samplers.sampler import Sampler


@dataclass
class CommitDescription:
    commit_hash: str
    distance_to_centroid: float
    github_url: str
    text: str
    date: str


@dataclass
class WordWeight:
    word: str
    weight: float


@dataclass
class ResultData:
    cluster_number: int
    cluster_size: int
    ratio: float
    centroid: list[WordWeight]
    date_proportion: dict[date, float]
    main_commit: list[CommitDescription]

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, (ResultData, WordWeight, CommitDescription)):
            return obj.__dict__
        return super(NpEncoder, self).default(obj)

class ResultHandler:
    def __init__(self,
                 repo: Repo,
                 file_io: FileIOManager,
                 file_names: FileNameConfig):

        self.repo = repo
        self.file_io = file_io
        self.file_names = file_names

    def handle(self, sample: Sampler):
        #TODO Нужно поченить подгрузку семплера и перенести подгруз в него
        sample = self.file_io.load(self.file_names.result_sample_path)
        vectors = self.file_io.load(self.file_names.bow_vectors_path)
        hash_to_vectors = {hash_commit: vector for hash_commit, vector in zip(sample, vectors)}

        dict = self.file_io.load(self.file_names.dict_path)

        labels = self.file_io.load(self.file_names.labels_path)
        labels_counter = Counter(labels)
        labels_id = sorted(list(set(labels)), key=lambda x: -labels_counter[x])
        for label_id in labels_id:
            if label_id >= 0:
                commit_in_cluster = [commit for i, commit in enumerate(sample) if labels[i] == label_id]
                vectors_in_cluster = [vector.toarray() for i, vector in enumerate(vectors) if labels[i] == label_id]
                centroid = np.average(np.array(vectors_in_cluster), axis=0)
                centroid_info = [WordWeight(dict[i], weight) for i, weight in enumerate(centroid) if weight > 0.2]
                centroid_info = sorted(centroid_info, key=lambda x: -x.weight)

                commits: list[CommitDescription] = []
                dates: dict[datetime, float] = defaultdict(int)

                for commit_hash in commit_in_cluster:
                    comit_data: Commit = self.repo.commit(commit_hash)
                    dates[str(comit_data.committed_datetime.date().replace(day=1, month=1))] += 1 / len(commit_in_cluster)

                    commits.append(
                        CommitDescription(
                            commit_hash=commit_hash,
                            distance_to_centroid=cosine(centroid, hash_to_vectors[commit_hash]),
                            github_url=f"https://github.com/torvalds/linux/commit/{commit_hash}",
                            text=comit_data.message,
                            date=str(comit_data.committed_datetime.date())
                        )
                    )
                commits = sorted(commits, key=lambda x: x.distance_to_centroid)

                result = ResultData(
                    cluster_number=label_id,
                    cluster_size=len(commit_in_cluster),
                    ratio=len(commit_in_cluster) / len(sample),
                    centroid=centroid_info,
                    date_proportion=dates,
                    main_commit=commits,
                )

                json_str = json.dumps(result, cls=NpEncoder, indent='\t', separators=(',', ': '))
                with open(F"{label_id}.json", "w") as text_file:
                    text_file.write(json_str)
