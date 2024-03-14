from datetime import datetime
from typing import Callable

from git import Commit, Repo
from tqdm import tqdm


class Sampler:
    def __init__(self,
                 repo: Repo,
                 time_fragment: tuple[datetime, datetime]| None = None,
                 commit_filter: Callable[[Commit], bool] | None = None,
                 folder: str = "/",
                 max_len: int = 1000000,
                 hash_list: list[str] | None = None
                 ):
        self._repo = repo
        self._result_list = None
        if hash_list is not None:
            self._result_list = [self._repo.commit(hash_commit) for hash_commit in hash_list]

        self._commit_filter = commit_filter
        if self._commit_filter is None:
            self._commit_filter = self._mark_word_method

        self._time = time_fragment
        if self._time is None:
            self._time = (datetime.min, datetime.now())
        self._folder = folder
        self._max_len = max_len

    def sample(self) -> list[Commit]:
        if self._result_list is not None:
            return self._result_list

        self._result_list = []
        with tqdm(total=self._max_len, desc='Form Sample') as pbar:
            for commit in self._repo.iter_commits(paths=self._folder):
                if self._is_commit_for_sample(commit):
                    self._result_list.append(commit)
                    pbar.update(1)
                if len(self._result_list) >= self._max_len:
                    break
        return self._result_list

    def _is_commit_for_sample(self, commit: Commit) -> bool:
        return self._is_commit_in_time_interval(commit) and \
            self._is_not_merge_commit(commit) and \
            self._commit_filter(commit)

    def _is_commit_in_time_interval(self, commit: Commit) -> bool:
        return self._time[0].date() < commit.committed_datetime.date() < self._time[1].date()

    def _is_not_merge_commit(self, commit: Commit) -> bool:
        return len(commit.parents) == 1

    def _mark_word_method(self, commit: Commit) -> bool:
        fix_marks = ['fix']
        for mark in fix_marks:
            if mark in commit.message.lower():
                return True
        return False