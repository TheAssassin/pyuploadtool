from typing import Type

from .. import ChangelogType, Changelog, ConventionalCommitChangelog


SUPPORTED_CHANGELOG_TYPES = {ChangelogType.STANDARD: Changelog, ChangelogType.CONVENTIONAL: ConventionalCommitChangelog}


class ChangelogTypeNotImplemented(NotImplementedError):
    pass


class ChangelogFactory:
    def __init__(self, changelog_type: ChangelogType = None):
        self.changelog_type = changelog_type
        self.changelog_generator = self.get_changelog_generator()

    def get_changelog_generator(self) -> Type[Changelog]:
        """
        Get the corresponding changelog generator from the environment
        if it is not supplied.
        :return:
        :rtype: ChangelogType
        """
        if self.changelog_type is None:
            self.changelog_type = ChangelogType.from_environment()

        generator = SUPPORTED_CHANGELOG_TYPES.get(self.changelog_type)
        if generator is None:
            raise ChangelogTypeNotImplemented(f"{self.changelog_type} is not a supported ChangeLogType")

        return generator
