from .. import Changelog


class ChangelogParser:
    def __init__(
        self,
        changelog: Changelog,
        title: str = None,
        commit_link_prefix: str = None,
    ):
        """
        Generates a changelog by arranging the commits according
        to the Conventional Commit Spec

        :param title: the title of the release, generally, the tag name
        :type title: str

        :param commit_link_prefix: a link prefix, which can be used to show a commit
        for example
        commit_link_prefix = https://github.com/$GITHUB_REPOSITORY/commit
        here, we will add the commit hash to the end.
        :type commit_link_prefix: str
        """
        self.changelog = changelog
        self.commit_link_prefix = commit_link_prefix.rstrip("/")
        self.title = title
