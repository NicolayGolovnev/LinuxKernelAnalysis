import numpy as np
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer


class IVectorizer:
    def vectorize(self, documents: list[str]) -> tuple[list[np.ndarray[float]], dict[int, str]]:
        ...


class TfIdfVectorizer(IVectorizer):
    def __init__(
            self,
            min_df=2,
            max_df=1.0,
            stop_words='english'
    ):
        self.min_df = min_df
        self.max_df = max_df
        self.stop_words = stop_words

        self.count_vectorizer = CountVectorizer(
            min_df=min_df,
            max_df=max_df,
            stop_words=stop_words
        )

        self.tfidf_transformer = TfidfTransformer(use_idf=True,
                                                  norm=None,
                                                  smooth_idf=False,
                                                  sublinear_tf=False)

    def vectorize(self, documents: list[str]) -> tuple[list[np.ndarray[float]], dict[int, str]]:
        bow_vectors = self.count_vectorizer.fit_transform(documents)
        self.dict = self.count_vectorizer.get_feature_names_out()
        idfs_vectors = self.tfidf_transformer.fit_transform(bow_vectors)
        return idfs_vectors, self.dict
