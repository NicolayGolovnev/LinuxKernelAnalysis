from abc import ABCMeta, abstractmethod

import numpy as np
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
import nltk


class TextTokenizer():
    def __init__(self):
        self.stop_word = [
            'fix',
            'error',
            'thunderbolt',
            'of',
            'and',
            'for',
            'in',
            'all',
            'add',
            'non',
            'also',
            'there',
            'the',
            'build',
            'on',
            'by',
            'with',
            'to',
            'this',
            '9aabb68568b4',
            '11',
            '1000',
            'issue',
            'driver',
            'code',
            'following',
            'after',
            'if',
        ]

        self.vectorizer = TfidfVectorizer(use_idf=False,
                                          norm=None,
                                          smooth_idf=False,
                                          sublinear_tf=False,
                                          min_df=2,
                                          max_df=1.0,
                                          stop_words=self.stop_word)

    def vectorize(self, tokens_colection):

        tokens_colection = [list(x) for x in set(tuple(x) for x in tokens_colection)]

        bow = self.vectorizer.fit_transform([' '.join(d) for d in tokens_colection])

        norms = np.linalg.norm(bow.toarray(), axis=1)
        vectors = bow.toarray()[norms != 0]

        return np.unique(vectors, axis=0)

    def vector_to_message(self, vector):
        sorted_indexes = np.argsort(vector)[::-1]
        features = self.vectorizer.get_feature_names_out()
        texts_restored = [features[i] for i in sorted_indexes[:5]]
        return texts_restored

    def unit_to_token(self, unit):
        lemmatizer = WordNetLemmatizer()
        raw_lemmas = [lemmatizer.lemmatize(token) for token in nltk.word_tokenize(unit)]
        pos_tags = nltk.pos_tag(raw_lemmas)
        N_lemmas = np.array([word for word, pos in pos_tags])
        return N_lemmas

    def commit_to_units(self, commit):
        fix_marks = ['fix']
        # regex = re.compile(r'^\s*-(?:(?!^$)[\s\S])+$', re.MULTILINE)
        units = []
        for unit in commit.message.lower().split('\n'):
            for mark in fix_marks:
                if mark in unit:
                    if 'clx' in unit:
                        print(commit)
                    units.append(unit)
                    break
        return units
