import numpy as np
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer, ENGLISH_STOP_WORDS
import nltk
from tqdm import tqdm
from git import Commit, Repo
from typing import Callable, Union, Tuple, Iterable, Optional
from datetime import datetime

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
