import re
import string

import nltk
import numpy as np
from git import Commit
from nltk import WordNetLemmatizer
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer, ENGLISH_STOP_WORDS
from tqdm import tqdm


class IDocumenter:
    def docs(self, commits: list[Commit]) -> list[str]:
        ...


class CommitTextDocumenter(IDocumenter):
    def __init__(self, stop_words: list[str], pos_black_list: list[str] | None = None):
        self.stop_words = set(stop_words)
        self.pos_black_list = pos_black_list
    def docs(self, commits: list[Commit]) -> list[str]:
        messages = []

        for commit in tqdm(commits, desc='Commit Vectorize'):
            messages.append(
                self._unit_to_token(
                    self._get_message_info(commit.message.lower())
                )
            )

        documents = [" ".join(message) for message in messages]
        table = str.maketrans("", "", string.punctuation)
        documents = [document.translate(table) for document in documents]
        return documents

    def _unit_to_token(self, unit) -> list[str]:
        lemmatizer = WordNetLemmatizer()
        raw_lemmas = [lemmatizer.lemmatize(token) for token in nltk.word_tokenize(unit)]
        stop_words = set(stopwords.words('english')).union(self.stop_words)
        raw_lemmas = [lemma for lemma in raw_lemmas if lemma not in stop_words]
        if not self.pos_black_list:
            return raw_lemmas
        pos_tags = nltk.pos_tag(raw_lemmas)
        chunks = nltk.ne_chunk(pos_tags)

        filtered_lemmas = np.array([word for word, pos in pos_tags if pos not in self.pos_black_list])
        return filtered_lemmas # noqa

    def _get_message_info(self, message):
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