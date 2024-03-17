from dataclasses import dataclass
from datetime import datetime
from typing import Callable
from git import Repo, Commit, DiffIndex
from tqdm import tqdm
import concurrent.futures

from common import split_non_copy_iterator


@dataclass
class DiffIndexModel:
    diff: str
    path: str


@dataclass
class ParrentCommit:
    hash: str
    parent_diff: list[DiffIndexModel]

    def diff(self, *param, **params):
        return self.parent_diff


@dataclass
class CommitModel:
    hash: str
    message: str
    parents: list[ParrentCommit]
    committed_datetime: datetime


class Loader:
    def __init__(self, repo_init: Callable[[], Repo]):
        self._repo_init = repo_init
        self._bar = None

    def load(self, commit_count: int, count_thread: int = 1) -> list[CommitModel]:
        self._bar = tqdm(total=commit_count, desc='Load Commit')
        iterators = split_non_copy_iterator(lambda: self._repo_init().iter_commits(), count_thread)
        arguments = zip(iterators, [commit_count // count_thread] * count_thread)

        load_commits = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=count_thread) as executor:
            results = executor.map(self._loader_iteration, arguments)
            for result in results:
                load_commits += result
            executor.shutdown()
        self._bar.close()
        return load_commits  # noqa

    def _loader_iteration(self, params: tuple[iter, int]):
        iter, commit_count = params
        load_commits = []
        for i, commit in enumerate(iter):
            self._bar.update(1)
            if self._is_not_merge_commit(commit):
                commit_models = self._commit_to_loader(commit)
                load_commits.append(commit_models)
            if i >= commit_count:
                break
        return load_commits

    def _commit_to_loader(self, commit: Commit) -> CommitModel:
        diff: DiffIndex = commit.parents[0].diff(commit, create_patch=True)
        diff_list = []

        for changes in diff:
            changes_model = DiffIndexModel(
                diff=changes.diff.decode("utf-8"),
                path=changes.a_path
            )
            diff_list.append(changes_model)

        parent_commit = ParrentCommit(
            hash=str(commit.parents[0]),
            parent_diff=diff_list
        )

        commit = CommitModel(
            hash=str(commit),
            message=commit.message,
            parents=[parent_commit],
            committed_datetime=commit.committed_datetime
        )
        return commit

    def _is_not_merge_commit(self, commit: Commit) -> bool:
        return len(commit.parents) == 1
