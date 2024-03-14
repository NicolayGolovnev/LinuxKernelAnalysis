import os
import pickle
from dataclasses import dataclass
from typing import List, Optional, Any, Callable

from numpy import ndarray
import numpy as np



@dataclass
class SampleData:
    word_dictionary: List[str]
    commit_list: List[str]
    distance_matrix: ndarray[float]
    cluster_labels: ndarray[int]
    vectors: ndarray[ndarray[float]]


class FileIOManager:
    @staticmethod
    def save(path: str, data: Any) -> None:
        if not FileIOManager.is_readable(path):
            if isinstance(data, ndarray):
                np.save(path, data)
            elif isinstance(data, list):
                np.savetxt(path, data, delimiter="\n", fmt="%s", encoding='utf-8')
            else:
                with open(path, 'wb') as f:
                    pickle.dump(data, f)

    @staticmethod
    def _read_text(path: str) -> List[str]:
        return list(np.genfromtxt(path, dtype=str, delimiter='\n', invalid_raise = False, encoding='utf-8'))

    @staticmethod
    def _read_npy(path: str) -> ndarray:
        return np.load(path, allow_pickle=True)

    @staticmethod
    def _read_object(path: str) -> Any:
        with open(path, 'rb') as f:
            return pickle.load(f)

    _extension_method_read = {
        '.npy': _read_npy,
        '.txt': _read_text,
        '.pickle': _read_object
    }
    @staticmethod
    def load(path: str) -> Any:
        _, file_extension = os.path.splitext(path)
        if file_extension not in FileIOManager._extension_method_read:
            raise IOError("can't read file with read extension")
        return FileIOManager._extension_method_read[file_extension](path)

    @staticmethod
    def load_if_exist(path: str) -> Any:
        if FileIOManager.is_readable(path):
            return FileIOManager.load(path)
        return None

    @staticmethod
    def subload(path: str, load_function: Callable):
        if FileIOManager.is_readable(path):
            return FileIOManager.load(path)
        result = load_function()
        FileIOManager.save(path, result)
        return result

    @staticmethod
    def is_readable(path: str) -> bool:
        return os.path.exists(path)
