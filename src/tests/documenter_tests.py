import unittest

import nltk
from git import Commit

from documenters.comment_text_tokenizer import CommitTextDocumenter
from tests.tools.mock_tools import MockStaticFactory


class MyTestCase(unittest.TestCase):

    def test_name_filtering(self):
        commit = MockStaticFactory.get_commit(
            ":This is a sample text that contains the name Alex Smith who is one of the developers of this project."
            "You can also find the surname Jones here.s")

        documenter = CommitTextDocumenter()
        documents = documenter.docs([commit])

        assert 'alex' not in documents[0]
        assert 'smith' not in documents[0]
        assert 'jones' not in documents[0]
        assert 'text' in documents[0]

    def test_link_filter(self):
        commit = MockStaticFactory.get_commit(
            "This is a sample text that contains web link https://lore.kernel.org."
            " You can also find the site www.google.com here and file link linux/core")

        documenter = CommitTextDocumenter()
        documents = documenter.docs([commit])

        assert 'https' not in documents[0]
        assert 'com' not in documents[0]
        assert 'google' not in documents[0]
        assert 'www' not in documents[0]
        assert 'linux' in documents[0]
        assert 'core' in documents[0]

    def test_reg_filter(self):
        commit = MockStaticFactory.get_commit(
            "This is a sample text that contains web link https://lore.kernel.org."
            " You can also find the site www.google.com here and file link linux/core")

        documenter = CommitTextDocumenter()
        documents = documenter.docs([commit])

        assert 'https' not in documents[0]
        assert 'com' not in documents[0]
        assert 'google' not in documents[0]
        assert 'www' not in documents[0]
        assert 'linux' in documents[0]
        assert 'core' in documents[0]

if __name__ == '__main__':
    unittest.main()
