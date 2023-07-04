import os

import numpy as np
import config
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
import nltk
from tqdm import tqdm
import csv

from CommitChecker import addition_in_commit


class TextTokenizer():
    def __init__(self):
        self.dict = []

        self.count_vectorizer = CountVectorizer(
            min_df=2,
            max_df=1.0,
            stop_words=config.stop_words
        )

        self.tfidf_transformer = TfidfTransformer(use_idf=False,
                                                  norm=None,
                                                  smooth_idf=False,
                                                  sublinear_tf=False)

    def vectorize(self, tokens_colection):
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

    def commit_to_units(self, commit):
        fix_marks = ['fix']
        units = []
        if not commit.message.startswith("Merge"):
            for mark in fix_marks:
                if mark in commit.message.lower():
                    units.append(self.get_message_info(commit.message.lower()))
                    break
        return units

    def get_message_info(self, message):
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


    def rep_to_vectors(self, repo):
        messages = []
        if config.use_save_file and os.path.exists(config.dict_path):
            self.dict = np.genfromtxt(config.dict_path, dtype=str)

        if not config.use_save_file or not os.path.exists(config.dict_path):
            count = 0
            for commit in tqdm(repo.iter_commits(paths=config.git_file_path), desc='Commit Processing'):
                #if len(commit.parents) == 1:
                #    addition_in_commit(commit)
                messages += [self.unit_to_token(unit) for unit in self.commit_to_units(commit)]
                count += 1
                if count > config.max_commit:
                    break


        vectors = self.vectorize(messages)

        if config.use_save_file:
            np.savetxt(config.dict_path, self.dict, delimiter="\n", fmt="%s", encoding='utf-8')

        return vectors