import os
import time

import numpy as np
import config
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer, ENGLISH_STOP_WORDS
import nltk
from tqdm import tqdm
from git import Commit, Repo
from typing import Callable, Any, Union, Tuple, Iterable
from datetime import datetime


class CommitSmaple:
    def __init__(self,
                 repo: Repo,
                 time_fragment: Union[Tuple[datetime, datetime], None] = None,
                 commit_filter: Union[Callable[[Commit], bool], None] = None,
                 folder: str = "/",
                 max_len: int = 1000000,
                 ):
        self._repo = repo
        self._result_list = None

        self._commit_filter = commit_filter
        if self._commit_filter is None:
            self._commit_filter = self._mark_word_method

        self._time = time_fragment
        if self._time is None:
            self._time = (datetime.min, datetime.now())
        self._folder = folder
        self._max_len = max_len

    @property
    def lsit(self) -> Iterable[Commit]:
        if self._result_list is not None:
            return self._result_list
        if config.is_readable(config.result_sample_path):
            hashes = np.genfromtxt(config.result_sample_path, dtype=str)
            self._result_list = [self._repo.commit(hash_commit) for hash_commit in hashes]
            return self._result_list
        self._result_list = []
        for commit in tqdm(self._repo.iter_commits(paths=self._folder), desc='Form Sample'):
            if self._is_coommit_for_sample(commit):
                self._result_list.append(commit)
            if len(self._result_list) >= self._max_len:
                break
        config.save_list(config.result_sample_path, self._result_list)
        return self._result_list

    def _is_coommit_for_sample(self, commit: Commit) -> bool:
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


class TextTokenizer():
    def __init__(self):
        self.dict = []

        self.count_vectorizer = CountVectorizer(
            min_df=2,
            max_df=1.0,
            stop_words='english'
        )

        self.tfidf_transformer = TfidfTransformer(use_idf=True,
                                                  norm=None,
                                                  smooth_idf=False,
                                                  sublinear_tf=False)

    def vectorize(self, tokens_colection) -> np.ndarray[np.ndarray[float]]:
        tokens_colection = [list(x) for x in set(tuple(x) for x in tokens_colection)]
        if config.use_save_file and os.path.exists(config.bow_vectors_path):
            bow_vectors = np.load(config.bow_vectors_path)
        else:
            bow_vectors = self.count_vectorizer.fit_transform([' '.join(d) for d in tokens_colection])
            self.dict = self.count_vectorizer.get_feature_names_out()
            if config.use_save_file:
                np.save(config.bow_vectors_path, bow_vectors.toarray())

        idfs_vecors = self.tfidf_transformer.fit_transform(bow_vectors)
        norms = np.linalg.norm(idfs_vecors.toarray(), axis=1)
        vectors = idfs_vecors.toarray()[norms != 0]

        return np.unique(vectors, axis=0)

    def vector_to_message(self, vector):
        sorted_indexes = np.argsort(vector)[::-1]
        texts_restored = [self.dict[i] for i in sorted_indexes[:config.short_output_word_ciunt]]
        return texts_restored

    def unit_to_token(self, unit):
        lemmatizer = WordNetLemmatizer()
        raw_lemmas = [lemmatizer.lemmatize(token) for token in nltk.word_tokenize(unit)]
        pos_tags = nltk.pos_tag(raw_lemmas)
        N_lemmas = np.array([word for word, pos in pos_tags])
        return N_lemmas


    @staticmethod
    def _get_message_info(message):
        rows = message.split("\n")
        last_row_index = len(rows) - 1
        while last_row_index != 0:
            first_word_in_raw = rows[last_row_index].split(" ")[0]
            if first_word_in_raw == "" or first_word_in_raw[-1] == ':':
                last_row_index -= 1
            else:
                break
        info = "\n".join(rows[:last_row_index + 1])
        return info

    def _mark_word_method(self, commit: Commit) -> bool:
        fix_marks = ['fix']
        for mark in fix_marks:
            if mark in commit.message.lower():
                return True
        return False

    def sample_to_vectors(self, sample: Iterable[Commit]) -> np.ndarray[np.ndarray[float]]:
        messages = []
        if config.is_readable(config.dict_path):
            self.dict = np.genfromtxt(config.dict_path, dtype=str)
        else:
            for commit in tqdm(sample, desc='Commit Processing'):
                messages.append(
                    self.unit_to_token(
                        self._get_message_info(commit.message.lower())
                    )
                )

        # TODO выдернуть чтение из файла из функции векторизации
        vectors = self.vectorize(messages)
        config.save_list(config.dict_path, self.dict.tolist())
        return vectors
