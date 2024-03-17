from typing import Callable, Optional, Tuple, Union

from git import Repo

from config import DirectoryAnalysisData, FileNameConfig
from flie_handlers.directory_iterator import DirectoryContextIterator
from laoders.loader import CommitModel
from samplers.sampler import Sampler
from work_handler.result_handler import ResultHandler
from work_handler.work_handler import WorkHandler


class MainHandler:
    def __init__(
            self,
            work_handler: Union[WorkHandler, ResultHandler],
            io_manager,
            file_names: FileNameConfig,
            commit_filter: Optional[Callable]
    ):
        self.work_handler = work_handler
        self.io_manager = io_manager
        self.file_names = file_names
        self.commit_filter = commit_filter

    def handle(self, commit_list: list[CommitModel], task_list: list[DirectoryAnalysisData]):
        directory_paths = [task.name for task in task_list]
        context_iterator = DirectoryContextIterator(directory_paths, self.file_names.result_path).get_iterator()
        for context, task in zip(context_iterator, task_list):
            result_sample = Sampler(
                commit_list=commit_list,
                max_len=task.max_commit,
                commit_filter=self.commit_filter,
                commit_folder=task.path
            )
            self.work_handler.handle(result_sample)
