import concurrent.futures
from datetime import datetime
from typing import Callable

from git import Commit
from tqdm import tqdm

from common import split_non_copy_iterator, split_iterator
from laoders.loader import CommitModel


class Sampler:
    def __init__(self,
                 commit_list: list[CommitModel],
                 time_fragment: tuple[datetime, datetime] | None = None,
                 commit_filter: Callable[[Commit], bool] | None = None,
                 max_len: int = 10_000_000,
                 commit_folder: str = "/"
                 ):
        self._commit_list = commit_list

        self._result_list = None

        self._commit_filter = commit_filter
        if self._commit_filter is None:
            self._commit_filter = lambda commit: True

        self._time = time_fragment
        if self._time is None:
            self._time = (datetime.min, datetime.now())
        self._max_len = max_len
        self._bar = None
        self._commit_folder = commit_folder

    def sample(self, hash_list: list[str] | None = None) -> list[CommitModel]:

        if hash_list is not None:
            commit_list_map = {commit.hash: commit for commit in self._commit_list}
            self._result_list = [commit_list_map[hash_commit] for hash_commit in hash_list]

        if self._result_list is not None:
            return self._result_list

        self._result_list = []
        commit_iters = split_iterator(iter(self._commit_list), 10)

        self._bar = tqdm(total=min(self._max_len, len(self._commit_list)), desc='Form Sample')

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            list(executor.map(self._thread_sample, commit_iters))
            executor.shutdown()
        self._bar.close()

        return self._result_list

    def _thread_sample(self, iterator):
        for commit in iterator:
            if self._is_commit_for_sample(commit):
                self._result_list.append(commit)
                self._bar.update(1)
            if len(self._result_list) >= self._max_len:
                return

    def _is_commit_for_sample(self, commit: CommitModel) -> bool:
        return (
                self._is_not_merge_commit(commit)
                and self._is_commit_in_time_interval(commit)
                and self._is_in_file_commit(commit)
                and self._commit_filter(commit)
        )

    def _is_commit_in_time_interval(self, commit: Commit) -> bool:
        return self._time[0].date() < commit.committed_datetime.date() < self._time[1].date()

    def _is_not_merge_commit(self, commit: Commit) -> bool:
        return len(commit.parents) == 1

    def _is_in_file_commit(self, commit: CommitModel) -> bool:
        changedFiles = [item.path for item in commit.parents[0].diff()]
        for file in changedFiles:
            if self._commit_folder in file:
                return True
        return False
