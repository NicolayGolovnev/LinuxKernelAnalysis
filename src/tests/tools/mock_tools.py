from unittest.mock import Mock

from git import Commit


class MockStaticFactory:
    @staticmethod
    def get_commit(commit_message: str) -> Commit:
        mock_obj = Mock()
        mock_obj.message = commit_message
        return mock_obj

