from typing import NamedTuple

from github.Commit import Commit

from .author import Author


class ChangelogCommit(NamedTuple):
    author: Author
    message: str
    sha: str

    @classmethod
    def from_github_commit(cls, commit: Commit):
        author = Author(name=commit.author.name, email=commit.author.email)
        message = commit.commit.message
        sha = commit.sha
        return ChangelogCommit(author=author, message=message, sha=sha)
