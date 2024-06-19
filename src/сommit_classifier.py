import numpy as np

import clang.cindex
from clang.cindex import CursorKind
from git import Commit, Repo
from typing import Tuple, Any, List, Callable
from tqdm import tqdm
from pulearn import ElkanotoPuClassifier
from sklearn.svm import SVC
from clang.cindex import Config

from config import FileNameConfig, MainConfig
from flie_handlers.file_io_manager import FileIOManager


class CommitClassifier:
    def __init__(self, io_manager: FileIOManager, config: MainConfig, file_names: FileNameConfig):
        self._csv = SVC(C=10, kernel='rbf', gamma=0.4, probability=True)
        self._classifier = ElkanotoPuClassifier(estimator=self._csv, hold_out_ratio=0.2)
        self.io_manager = io_manager
        self.file_names = file_names
        self.config = config

    def fit(self, bugfix_sample: np.ndarray[np.ndarray[int]], undefined_sample: np.ndarray[np.ndarray[int]]) -> None:
        self._classifier = self.io_manager.subload(
            self.file_names.model_path, lambda: self._fit(bugfix_sample, undefined_sample)
        )

    def _fit(self, bugfix_sample: np.ndarray[np.ndarray[int]], undefined_sample: np.ndarray[np.ndarray[int]]):
        X = np.concatenate((bugfix_sample, undefined_sample))
        Y = np.concatenate((np.ones(len(bugfix_sample)), np.array([-1] * len(undefined_sample))))
        self._classifier.fit(X, Y)
        return self._classifier

    def is_bugfix_commit(self, commit: Commit, vectorize: Callable[[Commit], np.ndarray[int]] = None) -> bool:
        if vectorize is None:
            vectorizer = CommitVectorizer(self.io_manager, self.config, self.file_names)
            vectorize = vectorizer.get_vector_from_commit

        vector = vectorize(commit)
        return self._classifier.predict([vector])[0] == 1


class CommitVectorizer:
    def __init__(self, io_manager: FileIOManager, config: MainConfig, name_config: FileNameConfig):
        self.io = io_manager
        self.name_config = name_config
        self.config = config
        self._white_sample = self._init_sample(self.name_config.white_path)
        self._gray_sample = self._init_sample(self.name_config.grey_path)

    def make_samples(self, repo: Repo) -> Tuple[List[str], List[str]]:
        with tqdm(self.config.white_sample_len + self.config.grey_sample_len, desc='Make samples') as pbar:
            for commit in repo.iter_commits():
                if self._is_bug_fix_commit_for_sample(commit):
                    self._white_sample.append(str(commit))
                    pbar.update(1)
                elif self._is_undefined_commit_for_sample(commit):
                    self._gray_sample.append(str(commit))
                    pbar.update(1)
                if self._is_samples_complete():
                    break

        self.io.save(self.name_config.white_path, self._white_sample)
        self.io.save(self.name_config.grey_path, self._gray_sample)

        return self._white_sample, self._gray_sample

    def get_matrix_from_commits(self, repo: Repo, bugfix_sample: List[str], undefined_sample: List[str]) -> Tuple[
        np.ndarray[np.ndarray[int]], np.ndarray[np.ndarray[int]]]:
        if self.io.is_readable(
                self.name_config.white_vectors_path
        ) and self.io.is_readable(
            self.name_config.gray_vectors_path
        ):
            white_vectors = np.load(self.name_config.white_vectors_path)
            gray_vectors = np.load(self.name_config.gray_vectors_path)
        else:
            white_vectors = np.vstack(list(map(lambda x: self.get_vector_from_hash(repo, x), bugfix_sample)))
            gray_vectors = np.vstack(list(map(lambda x: self.get_vector_from_hash(repo, x), undefined_sample)))

        self.io.save(self.name_config.white_vectors_path, white_vectors)
        self.io.save(self.name_config.gray_vectors_path, gray_vectors)

        return white_vectors, gray_vectors

    def get_vector_from_hash(self, repo: Repo, commit_hash: str) -> np.ndarray[int]:
        return self.get_vector_from_commit(repo.commit(commit_hash))

    def get_vector_from_commit(self, commit: Commit) -> np.ndarray[int]:
        vector = np.zeros(31)

        addition_strings = self._pattern_in_commit(commit, lambda string: string.startswith('+'))
        deletion_strings = self._pattern_in_commit(commit, lambda string: string.startswith('-'))
        addition = self._get_ast(addition_strings)
        deletion = self._get_ast(deletion_strings)

        vector[0] = len(commit.parents[0].diff(commit))
        vector[1] = len(addition_strings.splitlines()) + len(deletion_strings.splitlines())
        vector[2] = self._count_hunks(commit)
        vector[3:8] = self._get_vector_of_struct(addition, deletion, CursorKind.FOR_STMT, CursorKind.WHILE_STMT)
        vector[8:13] = self._get_vector_of_struct(addition, deletion, CursorKind.IF_STMT, CursorKind.SWITCH_STMT,
                                                  CursorKind.CONDITIONAL_OPERATOR)
        vector[13:18] = self._get_vector_of_struct(addition, deletion, CursorKind.UNARY_OPERATOR,
                                                   CursorKind.BINARY_OPERATOR)
        vector[18:23] = self._get_vector_of_struct(addition, deletion, CursorKind.VAR_DECL, CursorKind.FUNCTION_DECL)
        vector[23:28] = self._get_vector_of_struct(addition, deletion, CursorKind.CALL_EXPR)
        vector[28] = int(any(word in commit.message for word in self.config.functionality_words))
        vector[29] = int(any(word in commit.message for word in self.config.bug_words))
        vector[30] = int(any(word in commit.message for word in self.config.spelling_words))
        return vector

    def _init_sample(self, file_path: str) -> List[str]:
        if self.io.is_readable(file_path):
            return np.genfromtxt(file_path, dtype=str).tolist()
        return []

    def _is_bug_fix_commit_for_sample(self, commit: Commit) -> bool:
        return len(commit.parents) == 1 and \
            any(word in commit.message for word in self.config.white_sample_words) and \
            len(self._white_sample) < self.config.white_sample_len

    def _is_undefined_commit_for_sample(self, commit: Commit) -> bool:
        return len(commit.parents) == 1 and len(self._gray_sample) < self.config.grey_sample_len

    def _is_samples_complete(self) -> bool:
        return len(self._white_sample) >= self.config.white_sample_len and len(self._gray_sample) >= self.config.grey_sample_len

    def _get_vector_of_struct(self, addition: clang.cindex.TranslationUnit, deletion: clang.cindex.TranslationUnit,
                              *object_types: Any) -> np.ndarray[int]:
        vector = np.zeros(5)
        count_addition = self._count_object(addition.cursor, *object_types)
        count_deletion = self._count_object(deletion.cursor, *object_types)
        vector[0] = count_addition
        vector[1] = count_deletion
        vector[2] = abs(count_addition - count_deletion)
        vector[3] = count_addition + count_deletion
        vector[4] = int(count_addition > count_deletion)
        return vector

    @staticmethod
    def _pattern_in_commit(commit: Commit, filter_function: Callable[[str], bool]) -> str:
        try:
            changes = commit.parents[0].diff(commit, create_patch=True)
            additions_rows = []
            for change in changes:
                raw_commit = change.diff.decode("utf-8")
                rows = raw_commit.splitlines()[1:]
                rows = filter(filter_function, rows)
                rows = map(lambda a: a[1:], rows)
                additions_rows += rows
            additions = "\n".join(additions_rows)
            return additions
        except:
            return ""

    @staticmethod
    def _count_hunks(commit: Commit):
        changes = commit.parents[0].diff(commit, create_patch=True)
        hunks_count = 0
        try:
            for change in changes:
                if isinstance(change.diff, bytes):
                    change.diff = change.diff.decode("utf-8")
                hunks_count += change.diff.count('@@')
            return hunks_count
        except:
            return 0

    @staticmethod
    def _get_ast(code: str) -> clang.cindex.TranslationUnit:
        index = clang.cindex.Index.create()
        translation_unit = index.parse('dummy.c', args=['-std=c99'], unsaved_files=[('dummy.c', code)])
        return translation_unit

    def _count_object(self, ast: clang.cindex.Cursor, *object_types: Any) -> int:
        counter = 0
        if ast.kind in object_types:
            counter += 1
        for child in ast.get_children():
            counter += self._count_object(child, *object_types)
        return counter
