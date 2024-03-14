import os


class DirectoryContextIterator:
    """Класс со страшным сайдэфектом, следует быть осторожнее"""

    def __init__(self, directories: list[str], result_path:str):
        self._root_dir: str = os.getcwd()
        self.directories: list[str] = directories
        self.result_path: str = result_path

    def get_iterator(self) -> str:
        for dir in self.directories:
            self._set_dir(dir)
            yield dir
            self._back_dir()

    def _back_dir(self) -> None:
        os.chdir(self._root_dir)

    def _set_dir(self, name: str) -> None:
        current_folder = f"{self.result_path}/{name}"
        if not os.path.exists(current_folder):
            os.mkdir(current_folder)
        os.chdir(current_folder)

