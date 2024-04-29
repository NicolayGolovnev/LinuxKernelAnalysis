import re
import string

import nltk
import numpy as np
from git import Commit
from nltk import WordNetLemmatizer, Tree
from nltk.corpus import stopwords
from tqdm import tqdm


class IDocumenter:
    def docs(self, commits: list[Commit]) -> list[str]:
        ...


class CommitTextDocumenter(IDocumenter):
    def __init__(self, stop_words: list[str] = (), pos_black_list: list[str] | None = None):
        self.stop_words = set(stop_words)
        self.pos_black_list = pos_black_list

    def docs(self, commits: list[Commit]) -> list[str]:
        messages = []

        for commit in tqdm(commits, desc='Commit Vectorize'):
            messages.append(
                self._unit_to_token(
                    self._get_message_info(commit.message)
                )
            )

        documents = [" ".join(message) for message in messages]
        table = str.maketrans("", "", string.punctuation)
        documents = [document.translate(table) for document in documents]
        return documents

    def _human_name_filter(self, tokens: list[str]) -> list[str]:
        nltk_results = nltk.ne_chunk(nltk.pos_tag(tokens))
        filtered_tokens = []
        for nltk_result in nltk_results:
            if not isinstance(nltk_result, nltk.tree.Tree):
                filtered_tokens.append(nltk_result[0])
            elif nltk_result.label() != 'PERSON':
                filtered_tokens.append(nltk_result[0][0])

        return filtered_tokens

    def _web_filter(self, text: str) -> str:
        result = re.sub('https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+|www\.(?:[-\w.]|(?:%[\da-fA-F]{2}))+', "", text)

        return result

    def _unit_to_token(self, unit) -> list[str]:
        lemmatizer = WordNetLemmatizer()
        tokens = nltk.word_tokenize(unit)
        tokens = self._human_name_filter(tokens)
        raw_lemmas = [lemmatizer.lemmatize(token) for token in tokens]
        stop_words = set(stopwords.words('english')).union(self.stop_words)
        raw_lemmas = [lemma.lower() for lemma in raw_lemmas if lemma not in stop_words]
        if not self.pos_black_list:
            return raw_lemmas


        pos_tags = [nltk.pos_tag([lemma])[0] for lemma in raw_lemmas]

        filtered_lemmas = np.array([word for word, pos in pos_tags if pos not in self.pos_black_list])
        return filtered_lemmas  # noqa

    def _get_message_info(self, message):
        info = message
        words = info.split()
        if "#" not in words:
            return info
        return " ".join(words[1:])
