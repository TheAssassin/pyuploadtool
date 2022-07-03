from typing import NamedTuple

from github.Commit import Commit

from .author import Author


class ChangelogEntry:
    def __init__(self, author: Author, message: str, sha: str):
        self.author = author
        self.message = message
        self.sha = sha

    @classmethod
    def from_github_commit(cls, commit: Commit):
        """
        Converts a github commit to a pyuploadtool compatible
        ChangelogEntry instance
        """
        author = Author(name=commit.author.name, email=commit.author.email)
        # only get the first line of the commit
        message = commit.commit.message.split("\n")[0]
        sha = commit.sha
        return ChangelogEntry(author=author, message=message, sha=sha)
