import numpy as np
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer, ENGLISH_STOP_WORDS
import nltk
from tqdm import tqdm
from git import Commit, Repo
from typing import Callable, Union, Tuple, Iterable, Optional
from datetime import datetime


class CommitSample:
    def __init__(self,
                 repo: Repo,
                 time_fragment: Union[Tuple[datetime, datetime], None] = None,
                 commit_filter: Union[Callable[[Commit], bool], None] = None,
                 folder: str = "/",
                 max_len: int = 1000000,
                 hash_list: Optional[Iterable[str]] = None
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

    @property
    def list(self) -> Iterable[Commit]:
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


class TextTokenizer:
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

    def vectorize(self, tokens_collection) -> np.ndarray[np.ndarray[float]]:
        bow_vectors = self.count_vectorizer.fit_transform([' '.join(d) for d in tokens_collection])
        self.dict = self.count_vectorizer.get_feature_names_out()
        idfs_vectors = self.tfidf_transformer.fit_transform(bow_vectors)
        return idfs_vectors.toarray()

    def unit_to_token(self, unit, pos_black_list: Optional[Iterable[str]] = None):
        lemmatizer = WordNetLemmatizer()
        raw_lemmas = [lemmatizer.lemmatize(token) for token in nltk.word_tokenize(unit)]
        if pos_black_list is None:
            return raw_lemmas
        pos_tags = nltk.pos_tag(raw_lemmas)
        filtered_lemmas = np.array([word for word, pos in pos_tags if pos not in pos_black_list])
        return filtered_lemmas

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

        for commit in tqdm(sample, desc='Commit Processing'):
            messages.append(
                self.unit_to_token(
                    self._get_message_info(commit.message.lower())
                )
            )

        vectors = self.vectorize(messages)
        return vectors
