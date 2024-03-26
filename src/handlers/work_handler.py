from numpy import ndarray

from clusterizers.tree_clusterizer import IClusterizer
from config import FileNameConfig
from flie_handlers.file_io_manager import FileIOManager
from matrix_counter.lambda_matrix_counter import IMatrixGenerator
from samplers.sampler import Sampler
from documenters.comment_text_tokenizer import IDocumenter
from vectorizers.tf_idf_vectorizer import IVectorizer


class WorkHandler:
    def __init__(self,
                 documenter: IDocumenter,
                 vectorizer: IVectorizer,
                 matrix_counter: IMatrixGenerator,
                 clasterizer: IClusterizer,
                 file_io: FileIOManager,
                 file_names: FileNameConfig):

        self.documenter = documenter
        self.vectorizer = vectorizer
        self.matrix_counter = matrix_counter
        self.clasterizer = clasterizer
        self.file_io = file_io
        self.file_names = file_names

    def handle(self, sample: Sampler):
        sample_hash_list = self.file_io.load_if_exist(self.file_names.result_sample_path)
        sample = sample.sample(sample_hash_list)
        self.file_io.save(self.file_names.result_sample_path, [commit.hash for commit in sample])
        docs = self.file_io.subload(self.file_names.documents_path, lambda: self.documenter.docs(sample))
        docs = docs[:len(docs)//2]

        vectors = self.file_io.load_if_exist(self.file_names.bow_vectors_path)
        dict = self.file_io.load_if_exist(self.file_names.dict_path)
        if vectors is None and dict is None:
            vectors, dict = self.vectorizer.vectorize(docs)
        self.file_io.save(self.file_names.bow_vectors_path, vectors)
        self.file_io.save(self.file_names.dict_path, dict)

        matrix = self.file_io.subload(
            self.file_names.matrix_length_path,
            lambda: self.matrix_counter.create_matrix(vectors)
        )

        self.file_io.subload(self.file_names.labels_path, lambda: self.clasterizer.labels(matrix))
