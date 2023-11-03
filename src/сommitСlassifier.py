import pickle

import numpy as np

import config
import clang.cindex
from clang.cindex import CursorKind
from git import Commit, Repo
from typing import Tuple, Any, List, Callable
from tqdm import tqdm
from pulearn import ElkanotoPuClassifier
from sklearn.svm import SVC

clang.cindex.Config.set_library_file(config.clang_dll_path)

class CommitClassifier:
    def __init__(self):
        self._csv = SVC(C=10, kernel='rbf', gamma=0.4, probability=True)
        self._classifier = ElkanotoPuClassifier(estimator=self._csv, hold_out_ratio=0.2)

    def fit(self, bugfix_sample: np.ndarray[np.ndarray[int]], undefined_sample: np.ndarray[np.ndarray[int]]) -> None:
        if config.is_readable(config.model_path):
            with open(config.model_path, 'rb') as f:
                self._classifier = pickle.load(f)
        else:
            X = np.concatenate((bugfix_sample, undefined_sample))
            Y = np.concatenate((np.ones(len(bugfix_sample)), np.zeros(len(undefined_sample))))
            self._classifier.fit(X, Y)
            config.save_object(config.model_path,self._classifier)

    def is_bugfix_commit(self, commit: Commit, vectorize: Callable[[Commit], np.ndarray[int]] = None) -> bool:
        if vectorize is None:
            vectorizer = CommitVectorizer()
            vectorize = vectorizer.get_vector_from_commit

        vector = vectorize(commit)
        return self._classifier.predict([vector])[0] == 1

class CommitVectorizer:
    def __init__(self):
        self._white_sample = self._init_sample(config.white_path)
        self._gray_sample = self._init_sample(config.grey_path)

    def make_samples(self, repo: Repo) -> Tuple[List[str], List[str]]:
        with tqdm(config.white_sample_len + config.grey_sample_len, desc='Make samples') as pbar:
            for commit in repo.iter_commits():
                if self._is_bug_fix_commit_for_sample(commit):
                    self._white_sample.append(str(commit))
                    pbar.update(1)
                elif self._is_undefined_commit_for_sample(commit):
                    self._gray_sample.append(str(commit))
                    pbar.update(1)
                if self._is_samples_complete():
                    break

        config.save_list(config.white_path, self._white_sample)
        config.save_list(config.grey_path, self._gray_sample)

        return self._white_sample, self._gray_sample

    def get_matrix_from_commits(self, repo: Repo, bugfix_sample: List[str], undefined_sample: List[str]) -> Tuple[
        np.ndarray[np.ndarray[int]], np.ndarray[np.ndarray[int]]]:
        if config.is_readable(config.white_vectors_path) and config.is_readable(config.gray_vectors_path):
            white_vectors = np.load(config.white_vectors_path)
            gray_vectors = np.load(config.gray_vectors_path)
        else:
            white_vectors = np.vstack(list(map(lambda x: self.get_vector_from_hash(repo, x), bugfix_sample)))
            gray_vectors = np.vstack(list(map(lambda x: self.get_vector_from_hash(repo, x), undefined_sample)))

        config.save_np(config.white_vectors_path, white_vectors)
        config.save_np(config.gray_vectors_path, gray_vectors)

        return white_vectors, gray_vectors

    def get_vector_from_hash(self, repo: Repo, commit_hash: str)-> np.ndarray[int]:
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
        vector[28] = int(any(word in commit.message for word in config.functionality_words))
        vector[29] = int(any(word in commit.message for word in config.bug_words))
        vector[30] = int(any(word in commit.message for word in config.spelling_words))
        return vector

    @staticmethod
    def _init_sample(file_path: str) -> List[str]:
        if config.is_readable(file_path):
            return np.genfromtxt(file_path, dtype=str).tolist()
        return []

    def _is_bug_fix_commit_for_sample(self, commit: Commit) -> bool:
        return len(commit.parents) == 1 and \
               any(word in commit.message for word in config.white_sample_words) and \
               len(self._white_sample) < config.white_sample_len

    def _is_undefined_commit_for_sample(self, commit: Commit) -> bool:
        return len(commit.parents) == 1 and len(self._gray_sample) < config.grey_sample_len

    def _is_samples_complete(self) -> bool:
        return len(self._white_sample) >= config.white_sample_len and len(self._gray_sample) >= config.grey_sample_len

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
                hunks_count += change.diff.decode("utf-8").count('@@')
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
